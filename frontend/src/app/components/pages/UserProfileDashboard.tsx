import React, { useState, useEffect } from 'react';
import { User, Edit, Lock, LogOut, Activity, TrendingUp, Target, HelpCircle, RefreshCw } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import api from '../lib/api';
import { toast } from 'sonner';
import { BiometricService } from '../../../service/biometric.service';
import { GoalService } from '../../../service/goals.service';
import { StreakService } from '../../../service/streak.service';
import { LogService } from '../../../service/log.service';
import { SettingsService } from '../../../service/settings.service';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '../ui/dialog';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { GoalType, ActivityLevel, GoalPatchRequest } from '../../../types/goals';

// ==================== TYPE DEFINITIONS ====================

interface UserProfileData {
  userInfo: {
    name: string;
    email: string;
    streak: number;
    joinDate: string;
  };
  healthMetrics: {
    bmi: number;
    bmiCategory: string;
    bmr: number;
    tdee: number;
    activityLevel: string;
  };
  bodyStats: {
    height: number;
    currentWeight: number;
    targetWeight: number;
    weightToLose: number;
  };
  weightHistory: Array<{
    date: string;
    weight: number;
  }>;
  dailySummary: {
    mealsLogged: number;
    workoutsCompleted: number;
    weightLost: number;
    streak: number;
  };
}

// ==================== HELPER FUNCTIONS ====================

const calculateAge = (dobString: string | null): number => {
  if (!dobString) return 25;
  const diff = Date.now() - new Date(dobString).getTime();
  return Math.abs(new Date(diff).getUTCFullYear() - 1970);
};

const calculateBMI = (weight: number, heightCm: number): number => {
  if (!weight || !heightCm) return 0;
  return parseFloat((weight / ((heightCm / 100) ** 2)).toFixed(1));
};

const getBMICategory = (bmi: number): string => {
  if (bmi < 18.5) return 'Thiếu cân';
  if (bmi < 25) return 'Bình thường';
  if (bmi < 30) return 'Thừa cân';
  return 'Béo phì';
};

const calculateBMR = (gender: string, weight: number, height: number, age: number): number => {
  if (!weight || !height) return 0;
  if (gender === 'male') {
    return Math.round(88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age));
  }
  return Math.round(447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age));
};

const activityMultipliers: Record<string, number> = {
  sedentary: 1.2,
  low_active: 1.375,
  moderately_active: 1.55,
  very_active: 1.725,
  extremely_active: 1.9,
};

const getActivityLabel = (level: string): string => {
  const labels: Record<string, string> = {
    sedentary: 'Ít vận động',
    low_active: 'Vận động nhẹ',
    moderately_active: 'Vừa phải',
    very_active: 'Năng động',
    extremely_active: 'Rất năng động',
  };
  return labels[level] || level.replace('_', ' ');
};

// ==================== MAIN COMPONENT ====================

interface UserProfileDashboardProps {
  onLogout?: () => void;
}

export default function UserProfileDashboard({ onLogout }: UserProfileDashboardProps) {
  const [loading, setLoading] = useState(true);
  const [profileData, setProfileData] = useState<UserProfileData | null>(null);
  const [goal, setGoal] = useState<any>(null);
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [showPasswordDialog, setShowPasswordDialog] = useState(false);
  
  // Password change form state
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [changingPassword, setChangingPassword] = useState(false);
  
  // Goal edit form state
  const [editingGoal, setEditingGoal] = useState(false);
  const [selectedGoalType, setSelectedGoalType] = useState<string>('');
  const [selectedActivityLevel, setSelectedActivityLevel] = useState<string>('');

  // ==================== DATA FETCHING ====================
  
  useEffect(() => {
    fetchAllData();
  }, []);

  const fetchAllData = async () => {
    setLoading(true);
    try {
      // TODO: Connect API endpoint here - Fetch all data in parallel
      const [userRes, bioRes, goalRes, streakRes] = await Promise.allSettled([
        api.get('/users/me'),
        BiometricService.getHistory(undefined, undefined, 100), // Get last 100 weight records
        GoalService.getCurrentGoal(),
        StreakService.getStreakInfo(),
      ]);

      // Process user data
      const userData = userRes.status === 'fulfilled' ? userRes.value.data : null;
      const biometrics = bioRes.status === 'fulfilled' ? bioRes.value.items || [] : [];
      const goalData = goalRes.status === 'fulfilled' ? goalRes.value : null;
      const streak = streakRes.status === 'fulfilled' ? streakRes.value : null;
      
      // Store goal in state for use in render
      setGoal(goalData);

      // Calculate statistics
      // TODO: Connect API endpoint here - Count total meals logged
      // For now, we'll estimate or you can add a dedicated API endpoint
      let mealsLogged = 0;
      let workoutsCompleted = 0;
      
      // Try to get a sample of recent logs to estimate
      try {
        const today = new Date().toISOString().split('T')[0];
        const thirtyDaysAgo = new Date();
        thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
        const fromDate = thirtyDaysAgo.toISOString().split('T')[0];
        
        // Sample a few dates to estimate
        const sampleDates: string[] = [];
        for (let i = 0; i < 7; i++) {
          const date = new Date();
          date.setDate(date.getDate() - i);
          sampleDates.push(date.toISOString().split('T')[0]);
        }
        
        const logPromises = sampleDates.map((date: string) => 
          Promise.allSettled([
            LogService.getDailyFoodLogs(date),
            LogService.getDailyExerciseLogs(date),
          ])
        );
        
        const logResults = await Promise.all(logPromises);
        let totalMeals = 0;
        let totalWorkouts = 0;
        
        logResults.forEach((settledPair) => {
          const [foodLogsResult, exerciseLogsResult] = settledPair;
          if (foodLogsResult.status === 'fulfilled') {
            totalMeals += foodLogsResult.value.length;
          }
          if (exerciseLogsResult.status === 'fulfilled') {
            totalWorkouts += exerciseLogsResult.value.length;
          }
        });
        
        // Estimate total based on sample (multiply by ~4.3 for 30 days from 7 days)
        mealsLogged = Math.round(totalMeals * 4.3);
        workoutsCompleted = Math.round(totalWorkouts * 4.3);
      } catch (err) {
        console.warn('Could not fetch log statistics:', err);
        // Use default values if API fails
        mealsLogged = 0;
        workoutsCompleted = 0;
      }

      // Process biometrics
      const currentWeight = biometrics.length > 0 
        ? parseFloat(String(biometrics[0].weight_kg)) 
        : (parseFloat(String(userData?.profile?.weight_kg)) || 0);
      const height = userData?.profile?.height_cm_default || 170;
      const age = calculateAge(userData?.profile?.date_of_birth);
      const gender = userData?.profile?.gender || 'male';
      
      // Calculate health metrics
      const bmi = calculateBMI(currentWeight, height);
      const bmiCategory = getBMICategory(bmi);
      const bmr = calculateBMR(gender, currentWeight, height, age);
      const activityLevel = goalData?.baseline_activity || 'sedentary';
      const tdee = Math.round(bmr * (activityMultipliers[activityLevel] || 1.2));

      // Process weight history for chart
      const weightHistory = [...biometrics]
        .reverse()
        .map((log: any) => ({
          date: new Date(log.logged_at).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit' }),
          weight: parseFloat(String(log.weight_kg)),
        }));

      // Calculate weight statistics
      const weights = biometrics.map((b: any) => parseFloat(String(b.weight_kg)));
      const highestWeight = weights.length > 0 ? Math.max(...weights) : currentWeight;
      const lowestWeight = weights.length > 0 ? Math.min(...weights) : currentWeight;
      const averageWeight = weights.length > 0 
        ? (weights.reduce((a, b) => a + b, 0) / weights.length).toFixed(1)
        : currentWeight.toFixed(1);

      // Calculate weight lost (from highest to current)
      const weightLost = highestWeight - currentWeight;

      // Get target weight from goal
      // TODO: Backend should return target_weight in goal response
      const targetWeight = goalData?.target_weight_kg || 68; // Fallback if not available
      const weightToLose = currentWeight - targetWeight;

      // Format join date - Use user.created_at from API
      const joinDate = userData?.user?.created_at 
        ? new Date(userData.user.created_at).toLocaleDateString('vi-VN', { 
            day: '2-digit', 
            month: '2-digit', 
            year: 'numeric' 
          })
        : '---';

      // Build profile data object
      const data: UserProfileData = {
        userInfo: {
          name: userData?.profile?.full_name || userData?.user?.username || 'Người dùng',
          email: userData?.user?.email || '',
          streak: streak?.current_streak || 0,
          joinDate,
        },
        healthMetrics: {
          bmi,
          bmiCategory,
          bmr,
          tdee,
          activityLevel,
        },
        bodyStats: {
          height,
          currentWeight,
          targetWeight,
          weightToLose,
        },
        weightHistory,
        dailySummary: {
          mealsLogged,
          workoutsCompleted,
          weightLost: weightLost > 0 ? weightLost : 0,
          streak: streak?.current_streak || 0,
        },
      };

      setProfileData(data);
      
      // Initialize edit form with current values
      if (goalData) {
        setSelectedGoalType(goalData.goal_type || '');
        setSelectedActivityLevel(goalData.baseline_activity || '');
      }
    } catch (error) {
      console.error('Error loading profile:', error);
      toast.error('Không thể tải thông tin hồ sơ');
    } finally {
      setLoading(false);
    }
  };

  // ==================== GOAL UPDATE HANDLER ====================
  
  const handleUpdateGoal = async () => {
    if (!selectedGoalType || !selectedActivityLevel) {
      toast.error('Vui lòng chọn đầy đủ mục tiêu và mức độ hoạt động');
      return;
    }
    
    setEditingGoal(true);
    try {
      const updateData: GoalPatchRequest = {
        goal_type: selectedGoalType as GoalType,
        baseline_activity: selectedActivityLevel as ActivityLevel,
      };
      
      await GoalService.patchGoal(updateData);
      toast.success('Đã cập nhật mục tiêu và mức độ hoạt động thành công!');
      setShowEditDialog(false);
      
      // Refresh data to show updated values
      await fetchAllData();
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'Không thể cập nhật mục tiêu';
      toast.error(typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg));
    } finally {
      setEditingGoal(false);
    }
  };

  // ==================== PASSWORD CHANGE HANDLER ====================
  
  const handleChangePassword = async () => {
    if (!currentPassword || !newPassword || !confirmPassword) {
      toast.error('Vui lòng điền đầy đủ thông tin');
      return;
    }
    
    if (newPassword !== confirmPassword) {
      toast.error('Mật khẩu xác nhận không khớp');
      return;
    }
    
    if (newPassword.length < 6) {
      toast.error('Mật khẩu mới phải có ít nhất 6 ký tự');
      return;
    }
    
    setChangingPassword(true);
    try {
      await SettingsService.changePassword(currentPassword, newPassword);
      toast.success('Đã đổi mật khẩu thành công');
      setShowPasswordDialog(false);
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'Không thể đổi mật khẩu';
      toast.error(typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg));
    } finally {
      setChangingPassword(false);
    }
  };

  // ==================== RENDER ====================

  if (loading) {
    return (
      <div className="flex h-[50vh] items-center justify-center">
        <div className="text-center">
          <RefreshCw className="size-8 animate-spin text-pink-600 mx-auto mb-4" />
          <p className="text-gray-600">Đang tải dữ liệu...</p>
        </div>
      </div>
    );
  }

  if (!profileData) {
    return (
      <div className="text-center py-12 text-gray-500">
        Không thể tải thông tin hồ sơ
      </div>
    );
  }

  const { userInfo, healthMetrics, bodyStats, weightHistory, dailySummary } = profileData;

  // Calculate BMI progress bar width (scale 0-40 BMI)
  const bmiProgress = Math.min((healthMetrics.bmi / 40) * 100, 100);

  // Calculate weight statistics for chart
  const weights = weightHistory.map(w => w.weight);
  const chartMin = weights.length > 0 ? Math.min(...weights) - 1 : bodyStats.currentWeight - 1;
  const chartMax = weights.length > 0 ? Math.max(...weights) + 1 : bodyStats.currentWeight + 1;

  return (
    <div className="space-y-6 pb-8">
      {/* ==================== HEADER SECTION ==================== */}
      <Card className="bg-gradient-to-br from-pink-500 to-purple-600 text-white border-none shadow-lg">
        <CardContent className="pt-6">
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center gap-4">
              <div className="size-20 bg-white/20 rounded-full flex items-center justify-center text-3xl font-bold backdrop-blur-sm">
                {userInfo.name.charAt(0).toUpperCase() || <User />}
              </div>
              <div>
                <h2 className="text-2xl font-bold">{userInfo.name}</h2>
                <p className="text-sm opacity-90">{userInfo.email}</p>
                <Badge className="mt-2 bg-white/20 text-white border-white/30 hover:bg-white/30">
                  Streak: {userInfo.streak} ngày 🔥
                </Badge>
              </div>
            </div>
            <Dialog 
              open={showEditDialog} 
              onOpenChange={(open) => {
                setShowEditDialog(open);
                // Initialize form when dialog opens
                if (open && goal) {
                  setSelectedGoalType(goal.goal_type || '');
                  setSelectedActivityLevel(goal.baseline_activity || '');
                }
              }}
            >
              <DialogTrigger asChild>
                <Button variant="ghost" size="icon" className="text-white hover:bg-white/20 rounded-full">
                  <Edit className="size-5" />
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-md">
                <DialogHeader>
                  <DialogTitle>Chỉnh sửa mục tiêu và hoạt động</DialogTitle>
                  <DialogDescription>
                    Cập nhật mục tiêu sức khỏe và mức độ hoạt động của bạn. Hệ thống sẽ tự động tính lại BMR và TDEE.
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4 mt-4">
                  <div className="space-y-2">
                    <Label htmlFor="goal-type">Mục tiêu</Label>
                    <Select 
                      value={selectedGoalType} 
                      onValueChange={setSelectedGoalType}
                    >
                      <SelectTrigger id="goal-type">
                        <SelectValue placeholder="Chọn mục tiêu" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value={GoalType.LOSE_WEIGHT}>Giảm cân</SelectItem>
                        <SelectItem value={GoalType.GAIN_WEIGHT}>Tăng cân</SelectItem>
                        <SelectItem value={GoalType.MAINTAIN_WEIGHT}>Duy trì cân nặng</SelectItem>
                        <SelectItem value={GoalType.BUILD_MUSCLE}>Xây dựng cơ bắp</SelectItem>
                        <SelectItem value={GoalType.IMPROVE_HEALTH}>Cải thiện sức khỏe</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="activity-level">Mức độ hoạt động</Label>
                    <Select 
                      value={selectedActivityLevel} 
                      onValueChange={setSelectedActivityLevel}
                    >
                      <SelectTrigger id="activity-level">
                        <SelectValue placeholder="Chọn mức độ hoạt động" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value={ActivityLevel.SEDENTARY}>Ít vận động</SelectItem>
                        <SelectItem value={ActivityLevel.LOW_ACTIVE}>Vận động nhẹ</SelectItem>
                        <SelectItem value={ActivityLevel.MODERATELY_ACTIVE}>Vừa phải</SelectItem>
                        <SelectItem value={ActivityLevel.VERY_ACTIVE}>Năng động</SelectItem>
                        <SelectItem value={ActivityLevel.EXTREMELY_ACTIVE}>Rất năng động</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="flex gap-2 justify-end pt-4">
                    <Button 
                      variant="outline" 
                      onClick={() => setShowEditDialog(false)}
                      disabled={editingGoal}
                    >
                      Hủy
                    </Button>
                    <Button 
                      onClick={handleUpdateGoal} 
                      disabled={editingGoal || !selectedGoalType || !selectedActivityLevel}
                      className="bg-gradient-to-r from-pink-500 to-purple-600"
                    >
                      {editingGoal ? 'Đang cập nhật...' : 'Cập nhật'}
                    </Button>
                  </div>
                </div>
              </DialogContent>
            </Dialog>
          </div>

          {/* Info Row */}
          <div className="grid grid-cols-3 gap-4 pt-4 border-t border-white/20">
            <div>
              <p className="text-xs opacity-80 uppercase tracking-wider">Tham gia</p>
              <p className="font-semibold">{userInfo.joinDate}</p>
            </div>
            <div>
              <p className="text-xs opacity-80 uppercase tracking-wider">Mục tiêu</p>
              <p className="font-semibold capitalize">
                {goal?.goal_type?.replace('_', ' ') || 'Chưa đặt'}
              </p>
            </div>
            <div>
              <p className="text-xs opacity-80 uppercase tracking-wider">Hoạt động</p>
              <p className="font-semibold">{getActivityLabel(healthMetrics.activityLevel)}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* ==================== HEALTH METRICS SECTION ==================== */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* BMI Card */}
        <Card className="hover:shadow-md transition-shadow border-2 border-dashed border-blue-200">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              <Activity className="size-5 text-pink-600" />
              BMI
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{healthMetrics.bmi}</p>
            <p className="text-sm text-gray-600 mt-1 font-medium">{healthMetrics.bmiCategory}</p>
            
            {/* Progress Bar */}
            <div className="mt-4 h-2 bg-gray-100 rounded-full overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-pink-500 to-purple-600 transition-all duration-1000" 
                style={{ width: `${bmiProgress}%` }}
              />
            </div>
            <p className="text-xs text-gray-400 mt-2">Tính từ chiều cao & cân nặng</p>
          </CardContent>
        </Card>

        {/* BMR Card */}
        <Card className="hover:shadow-md transition-shadow border-2 border-dashed border-blue-200">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              <TrendingUp className="size-5 text-cyan-600" />
              BMR
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{healthMetrics.bmr}</p>
            <p className="text-sm text-gray-600 mt-1">kcal/ngày</p>
            <p className="text-xs text-gray-500 mt-4 leading-relaxed">
              Lượng calories cơ thể tiêu hao khi nghỉ ngơi hoàn toàn
            </p>
          </CardContent>
        </Card>

        {/* TDEE Card */}
        <Card className="hover:shadow-md transition-shadow border-2 border-dashed border-blue-200">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              <Target className="size-5 text-purple-600" />
              TDEE
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{healthMetrics.tdee}</p>
            <p className="text-sm text-gray-600 mt-1">kcal/ngày</p>
            <p className="text-xs text-gray-500 mt-4 leading-relaxed">
              Tổng lượng calories tiêu hao hàng ngày bao gồm hoạt động
            </p>
          </CardContent>
        </Card>
      </div>

      {/* ==================== BODY STATS SECTION ==================== */}
      <Card>
        <CardHeader>
          <CardTitle>Số đo cơ thể</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="p-4 bg-gray-50 rounded-xl border border-gray-100">
              <p className="text-sm text-gray-500 mb-1">Chiều cao</p>
              <p className="text-2xl font-bold">{bodyStats.height} cm</p>
            </div>
            <div className="p-4 bg-gray-50 rounded-xl border border-gray-100">
              <p className="text-sm text-gray-500 mb-1">Cân nặng hiện tại</p>
              <p className="text-2xl font-bold">{bodyStats.currentWeight.toFixed(1)} kg</p>
            </div>
            <div className="p-4 bg-gray-50 rounded-xl border border-gray-100">
              <p className="text-sm text-gray-500 mb-1">Cân nặng mục tiêu</p>
              <p className="text-2xl font-bold">{bodyStats.targetWeight} kg</p>
            </div>
            <div className="p-4 bg-gray-50 rounded-xl border border-gray-100">
              <p className="text-sm text-gray-500 mb-1">Cần giảm</p>
              <p className={`text-2xl font-bold ${bodyStats.weightToLose > 0 ? 'text-pink-600' : 'text-green-600'}`}>
                {bodyStats.weightToLose > 0 ? `+${bodyStats.weightToLose.toFixed(1)}` : bodyStats.weightToLose.toFixed(1)} kg
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* ==================== WEIGHT TREND CHART ==================== */}
      <Card>
        <CardHeader>
          <CardTitle>Xu hướng cân nặng</CardTitle>
        </CardHeader>
        <CardContent>
          {weightHistory.length > 0 ? (
            <>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={weightHistory}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5e7eb" />
                  <XAxis 
                    dataKey="date" 
                    tickLine={false} 
                    axisLine={false} 
                    dy={10} 
                    style={{ fontSize: '12px' }} 
                  />
                  <YAxis 
                    domain={[chartMin, chartMax]} 
                    hide 
                  />
                  <Tooltip 
                    contentStyle={{ 
                      borderRadius: '8px', 
                      border: 'none', 
                      boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' 
                    }}
                    formatter={(value: any) => [`${value} kg`, 'Cân nặng']}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="weight" 
                    stroke="url(#colorGradient)" 
                    strokeWidth={3}
                    dot={{ fill: '#ec4899', r: 4, strokeWidth: 2, stroke: '#fff' }}
                    activeDot={{ r: 6 }}
                  />
                  <defs>
                    <linearGradient id="colorGradient" x1="0" y1="0" x2="1" y2="0">
                      <stop offset="0%" stopColor="#ec4899" />
                      <stop offset="100%" stopColor="#9333ea" />
                    </linearGradient>
                  </defs>
                </LineChart>
              </ResponsiveContainer>
              <div className="mt-6 grid grid-cols-3 gap-4 text-center border-t pt-4">
                <div>
                  <p className="text-xs text-gray-500 uppercase">Cao nhất</p>
                  <p className="font-bold">{Math.max(...weights).toFixed(1)} kg</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500 uppercase">Trung bình</p>
                  <p className="font-bold">
                    {(weights.reduce((a, b) => a + b, 0) / weights.length).toFixed(1)} kg
                  </p>
                </div>
                <div>
                  <p className="text-xs text-gray-500 uppercase">Thấp nhất</p>
                  <p className="font-bold">{Math.min(...weights).toFixed(1)} kg</p>
                </div>
              </div>
            </>
          ) : (
            <div className="h-[200px] flex items-center justify-center text-gray-500">
              Chưa có dữ liệu cân nặng. Hãy cập nhật chỉ số cơ thể.
            </div>
          )}
        </CardContent>
      </Card>

      {/* ==================== DAILY SUMMARY SECTION ==================== */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="hover:shadow-md transition-shadow">
          <CardContent className="pt-6">
            <p className="text-sm text-gray-500 mb-2">Bữa ăn ghi nhận</p>
            <p className="text-3xl font-bold text-pink-600">{dailySummary.mealsLogged}</p>
          </CardContent>
        </Card>
        <Card className="hover:shadow-md transition-shadow">
          <CardContent className="pt-6">
            <p className="text-sm text-gray-500 mb-2">Bài tập hoàn thành</p>
            <p className="text-3xl font-bold text-blue-600">{dailySummary.workoutsCompleted}</p>
          </CardContent>
        </Card>
        <Card className="hover:shadow-md transition-shadow">
          <CardContent className="pt-6">
            <p className="text-sm text-gray-500 mb-2">Đã giảm</p>
            <p className="text-3xl font-bold text-pink-600">
              {dailySummary.weightLost > 0 ? `-${dailySummary.weightLost.toFixed(1)}` : '0.0'} kg
            </p>
          </CardContent>
        </Card>
        <Card className="hover:shadow-md transition-shadow">
          <CardContent className="pt-6">
            <p className="text-sm text-gray-500 mb-2">Ngày streak</p>
            <p className="text-3xl font-bold text-orange-600">{dailySummary.streak}</p>
          </CardContent>
        </Card>
      </div>

      {/* ==================== ACCOUNT MANAGEMENT SECTION ==================== */}
      <div className="space-y-4">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Lock className="size-5 text-gray-600" />
              Bảo mật tài khoản
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Dialog open={showPasswordDialog} onOpenChange={setShowPasswordDialog}>
              <DialogTrigger asChild>
                <Button variant="outline" className="w-full md:w-auto">
                  <Lock className="size-4 mr-2" />
                  Đổi mật khẩu
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Đổi mật khẩu</DialogTitle>
                  <DialogDescription>
                    Nhập mật khẩu hiện tại và mật khẩu mới của bạn
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4 mt-4">
                  <div className="space-y-2">
                    <Label htmlFor="currentPassword">Mật khẩu hiện tại</Label>
                    <Input
                      id="currentPassword"
                      type="password"
                      value={currentPassword}
                      onChange={(e) => setCurrentPassword(e.target.value)}
                      placeholder="Nhập mật khẩu hiện tại"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="newPassword">Mật khẩu mới</Label>
                    <Input
                      id="newPassword"
                      type="password"
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                      placeholder="Nhập mật khẩu mới"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="confirmPassword">Xác nhận mật khẩu mới</Label>
                    <Input
                      id="confirmPassword"
                      type="password"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      placeholder="Xác nhận mật khẩu mới"
                    />
                  </div>
                  <div className="flex gap-2 justify-end">
                    <Button variant="outline" onClick={() => setShowPasswordDialog(false)}>
                      Hủy
                    </Button>
                    <Button 
                      onClick={handleChangePassword} 
                      disabled={changingPassword}
                      className="bg-gradient-to-r from-pink-500 to-purple-600"
                    >
                      {changingPassword ? 'Đang xử lý...' : 'Đổi mật khẩu'}
                    </Button>
                  </div>
                </div>
              </DialogContent>
            </Dialog>
          </CardContent>
        </Card>

        {/* Logout Button */}
        {onLogout && (
          <Card>
            <CardContent className="pt-6">
              <Button
                variant="destructive"
                className="w-full flex items-center justify-center gap-2"
                onClick={onLogout}
              >
                <LogOut className="size-4" />
                Đăng xuất
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}

