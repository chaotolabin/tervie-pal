import { useState, useEffect } from 'react';
import { User, Activity, TrendingUp, Target, Edit, Loader2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import api from '../../lib/api'; // Import api client
import { toast } from 'sonner';

// --- Helper tính toán sức khỏe (Nếu bạn chưa có file utils) ---
const calculateAge = (dobString: string | null) => {
  if (!dobString) return 25; // Default age
  const diff = Date.now() - new Date(dobString).getTime();
  return Math.abs(new Date(diff).getUTCFullYear() - 1970);
};

const calculateBMI = (weight: number, heightCm: number) => {
  if (!weight || !heightCm) return 0;
  return parseFloat((weight / ((heightCm / 100) ** 2)).toFixed(1));
};

// Harris-Benedict BMR Formula
const calculateBMR = (gender: string, weight: number, height: number, age: number) => {
  if (!weight || !height) return 0;
  if (gender === 'male') {
    return Math.round(88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age));
  }
  return Math.round(447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age));
};

// TDEE Multipliers
const activityMultipliers: Record<string, number> = {
  sedentary: 1.2,
  low_active: 1.375,
  moderately_active: 1.55,
  very_active: 1.725,
  extremely_active: 1.9,
};

export default function ProfilePage() {
  const [loading, setLoading] = useState(true);
  const [userData, setUserData] = useState<any>(null);
  const [biometrics, setBiometrics] = useState<any[]>([]);
  const [goal, setGoal] = useState<any>(null);
  const [streak, setStreak] = useState<any>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Gọi song song 4 API để lấy toàn bộ dữ liệu Profile
        const [userRes, bioRes, goalRes, streakRes] = await Promise.allSettled([
          api.get('/users/me'),
          api.get('/biometrics?limit=10'), // Lấy 10 lần cân gần nhất
          api.get('/goals'),
          api.get('/streak')
        ]);

        // Xử lý kết quả từng API (dùng allSettled để 1 cái lỗi không chết cả trang)
        if (userRes.status === 'fulfilled') setUserData(userRes.value.data);
        if (bioRes.status === 'fulfilled') setBiometrics(bioRes.value.data.items || []);
        if (goalRes.status === 'fulfilled') setGoal(goalRes.value.data);
        if (streakRes.status === 'fulfilled') setStreak(streakRes.value.data);

      } catch (error) {
        console.error("Lỗi tải profile:", error);
        toast.error("Không thể tải đầy đủ thông tin cá nhân");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex h-[50vh] items-center justify-center">
        <Loader2 className="size-8 animate-spin text-pink-600" />
      </div>
    );
  }

  // --- Chế biến dữ liệu để hiển thị ---
  
  // 1. Thông tin cơ bản
  const currentWeight = biometrics.length > 0 ? biometrics[0].weight_kg : (userData?.profile?.weight_kg || 0);
  const height = userData?.profile?.height_cm_default || 170;
  const age = calculateAge(userData?.profile?.date_of_birth);
  const gender = userData?.profile?.gender || 'male';
  
  // 2. Tính toán chỉ số
  const bmi = calculateBMI(currentWeight, height);
  let bmiCategory = 'Bình thường';
  if (bmi < 18.5) bmiCategory = 'Thiếu cân';
  else if (bmi >= 25) bmiCategory = 'Thừa cân';

  const bmr = calculateBMR(gender, currentWeight, height, age);
  const activityLevel = goal?.baseline_activity || 'sedentary';
  const tdee = Math.round(bmr * (activityMultipliers[activityLevel] || 1.2));

  // 3. Dữ liệu biểu đồ (Đảo ngược để hiển thị cũ -> mới)
  const chartData = [...biometrics].reverse().map(log => ({
    date: new Date(log.logged_at).toLocaleDateString('vi-VN', {day: '2-digit', month: '2-digit'}),
    weight: log.weight_kg
  }));

  // 4. Mục tiêu
  const goalWeight = 68; // TODO: Backend chưa trả về goal_weight trong API /goals, tạm hardcode hoặc lấy từ logic khác
  const weightDiff = currentWeight - goalWeight;

  return (
    <div className="space-y-6">
      {/* Profile Header */}
      <Card className="bg-gradient-to-br from-pink-500 to-purple-600 text-white border-none shadow-lg">
        <CardContent className="pt-6">
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center gap-4">
              <div className="size-20 bg-white/20 rounded-full flex items-center justify-center text-3xl font-bold backdrop-blur-sm">
                {userData?.user?.username?.charAt(0).toUpperCase() || <User />}
              </div>
              <div>
                <h2 className="text-2xl font-bold">{userData?.profile?.full_name || userData?.user?.username}</h2>
                <p className="text-sm opacity-90">{userData?.user?.email}</p>
                <Badge className="mt-2 bg-white/20 text-white border-white/30 hover:bg-white/30">
                  Streak: {streak?.current_streak || 0} ngày 🔥
                </Badge>
              </div>
            </div>
            <Button variant="ghost" size="icon" className="text-white hover:bg-white/20 rounded-full">
              <Edit className="size-5" />
            </Button>
          </div>

          <div className="grid grid-cols-3 gap-4 pt-4 border-t border-white/20">
            <div>
              <p className="text-xs opacity-80 uppercase tracking-wider">Tham gia</p>
              <p className="font-semibold">
                {userData?.user?.created_at ? new Date(userData.user.created_at).toLocaleDateString('vi-VN') : '---'}
              </p>
            </div>
            <div>
              <p className="text-xs opacity-80 uppercase tracking-wider">Mục tiêu</p>
              <p className="font-semibold capitalize">
                {goal?.goal_type?.replace('_', ' ') || 'Chưa đặt'}
              </p>
            </div>
            <div>
              <p className="text-xs opacity-80 uppercase tracking-wider">Hoạt động</p>
              <p className="font-semibold capitalize">
                {activityLevel.replace('_', ' ')}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Health Metrics (Calculated Live) */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="hover:shadow-md transition-shadow">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              <Activity className="size-5 text-pink-600" />
              BMI
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{bmi}</p>
            <p className="text-sm text-gray-600 mt-1 font-medium">{bmiCategory}</p>
            
            <div className="mt-4 h-2 bg-gray-100 rounded-full overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-pink-500 to-purple-600 transition-all duration-1000" 
                style={{ width: `${Math.min((bmi / 40) * 100, 100)}%` }} // Scale 0-40 BMI
              />
            </div>
            <p className="text-xs text-gray-400 mt-2">Dựa trên Chiều cao & Cân nặng</p>
          </CardContent>
        </Card>

        <Card className="hover:shadow-md transition-shadow">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              <TrendingUp className="size-5 text-cyan-600" />
              BMR
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{bmr}</p>
            <p className="text-sm text-gray-600 mt-1">kcal/ngày</p>
            <p className="text-xs text-gray-500 mt-4 leading-relaxed">
              Năng lượng tiêu hao khi nghỉ ngơi hoàn toàn (Trao đổi chất cơ bản)
            </p>
          </CardContent>
        </Card>

        <Card className="hover:shadow-md transition-shadow">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              <Target className="size-5 text-purple-600" />
              TDEE
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{tdee}</p>
            <p className="text-sm text-gray-600 mt-1">kcal/ngày</p>
            <p className="text-xs text-gray-500 mt-4 leading-relaxed">
              Tổng năng lượng tiêu hao thực tế dựa trên mức độ vận động "{activityLevel}"
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Body Stats */}
      <Card>
        <CardHeader>
          <CardTitle>Số đo cơ thể</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="p-4 bg-gray-50 rounded-xl border border-gray-100">
              <p className="text-sm text-gray-500 mb-1">Chiều cao</p>
              <p className="text-2xl font-bold">{height} cm</p>
            </div>
            <div className="p-4 bg-gray-50 rounded-xl border border-gray-100">
              <p className="text-sm text-gray-500 mb-1">Cân nặng hiện tại</p>
              <p className="text-2xl font-bold">{currentWeight} kg</p>
            </div>
            <div className="p-4 bg-gray-50 rounded-xl border border-gray-100">
              <p className="text-sm text-gray-500 mb-1">Mục tiêu (Giả định)</p>
              <p className="text-2xl font-bold">{goalWeight} kg</p>
            </div>
            <div className="p-4 bg-gray-50 rounded-xl border border-gray-100">
              <p className="text-sm text-gray-500 mb-1">Chênh lệch</p>
              <p className={`text-2xl font-bold ${weightDiff > 0 ? 'text-pink-600' : 'text-green-600'}`}>
                {weightDiff > 0 ? `+${weightDiff.toFixed(1)}` : weightDiff.toFixed(1)} kg
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Weight Trend Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Lịch sử cân nặng</CardTitle>
        </CardHeader>
        <CardContent>
          {chartData.length > 0 ? (
            <>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5e7eb" />
                  <XAxis dataKey="date" tickLine={false} axisLine={false} dy={10} style={{ fontSize: '12px' }} />
                  <YAxis domain={['dataMin - 1', 'dataMax + 1']} hide />
                  <Tooltip 
                    contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
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
                  <p className="font-bold">{Math.max(...biometrics.map(b => b.weight_kg))} kg</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500 uppercase">Thấp nhất</p>
                  <p className="font-bold">{Math.min(...biometrics.map(b => b.weight_kg))} kg</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500 uppercase">Gần nhất</p>
                  <p className="font-bold text-pink-600">{currentWeight} kg</p>
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
    </div>
  );
}