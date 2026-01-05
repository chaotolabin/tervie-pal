import React, { useState, useEffect } from 'react';
import { Calendar, Flame, TrendingDown, Apple, Loader2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';
import MacroSummary from './MacroSummary';
import QuickAddBar from './QuickAddBar';
import api from '../lib/api'; // Đảm bảo import đúng đường dẫn api client
import { toast } from 'sonner';

interface DashboardHomeProps {
  onQuickAdd: () => void;
  fullName?: string;
}

// Định nghĩa kiểu dữ liệu cho State
interface DailySummary {
  total_calories_consumed: number;
  total_calories_burned: number;
  net_calories: number;
  total_protein_g: number;
  total_carbs_g: number;
  total_fat_g: number;
}

interface UserGoal {
  daily_calorie_target: number;
  protein_grams?: number;
  carb_grams?: number;
  fat_grams?: number;
  goal_type: string;
}

interface BiometricLog {
  logged_at: string;
  weight_kg: number;
}

export default function DashboardHome({ onQuickAdd, fullName }: DashboardHomeProps) {
  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState<DailySummary | null>(null);
  const [goal, setGoal] = useState<UserGoal | null>(null);
  const [weightHistory, setWeightHistory] = useState<any[]>([]);
  const [currentWeight, setCurrentWeight] = useState<number>(0);
  const [caloriesHistory, setCaloriesHistory] = useState<any[]>([]);

  const fetchDashboardData = async () => {
    try {
      const today = new Date().toISOString().split('T')[0];

      // Gọi song song 3 API để tối ưu tốc độ
      const [logsRes, goalsRes, bioRes] = await Promise.all([
        api.get(`/logs/summary/${today}`), // Lấy dinh dưỡng hôm nay
        api.get('/goals'),                 // Lấy mục tiêu (để so sánh)
        api.get('/biometrics?limit=7')     // Lấy 7 lần cân gần nhất
      ]);

      setSummary(logsRes.data);
      setGoal(goalsRes.data);

      // Xử lý dữ liệu cân nặng cho biểu đồ
      const bioLogs: BiometricLog[] = bioRes.data.items || [];
      // Đảo ngược mảng để hiển thị từ cũ đến mới trên biểu đồ
      const chartData = [...bioLogs].reverse().map(log => ({
        date: new Date(log.logged_at).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit' }),
        weight: log.weight_kg
      }));
      
      setWeightHistory(chartData);
      if (bioLogs.length > 0) {
        setCurrentWeight(bioLogs[0].weight_kg); // Lấy cân nặng mới nhất
      }

      // Fetch calories data for last 30 days
      const caloriesData = [];
      const currentDate = new Date();
      for (let i = 29; i >= 0; i--) {
        const date = new Date(currentDate);
        date.setDate(date.getDate() - i);
        const dateStr = date.toISOString().split('T')[0];
        try {
          const response = await api.get(`/logs/summary/${dateStr}`);
          caloriesData.push({
            date: date.toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit' }),
            calories: Math.round(response.data.net_calories || 0)
          });
        } catch (error) {
          // Nếu không có dữ liệu cho ngày đó, thêm 0
          caloriesData.push({
            date: date.toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit' }),
            calories: 0
          });
        }
      }
      setCaloriesHistory(caloriesData);

    } catch (error) {
      console.error("Dashboard data error:", error);
      // Không toast lỗi chặn dòng chảy, chỉ log
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
    
    // Lắng nghe event refresh từ các component con (ExerciseLogging, FoodLoggingPage)
    const handleRefresh = () => {
      fetchDashboardData();
    };
    
    window.addEventListener('refreshDashboard', handleRefresh);
    
    return () => {
      window.removeEventListener('refreshDashboard', handleRefresh);
    };
  }, []);

  if (loading) {
    return (
      <div className="flex h-[50vh] items-center justify-center">
        <Loader2 className="size-8 animate-spin text-pink-600" />
      </div>
    );
  }

  // Tính toán % Calo
  const calorieTarget = goal?.daily_calorie_target || 2000;
  const caloriesConsumed = summary?.total_calories_consumed || 0;
  const caloriesBurned = summary?.total_calories_burned || 0;
  const netCalories = summary?.net_calories || 0; // Backend đã tính (consumed - burned)
  
  // Logic hiển thị: Nếu muốn hiển thị (Consumed) vs Target hay (Net) vs Target tùy logic app
  // Ở đây dùng Net Calories (thực nhận) vs Target
  const caloriePercent = Math.min(Math.round((netCalories / calorieTarget) * 100), 100);

  return (
    <div className="space-y-6">
      {/* Top Section: 2 Columns Layout */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Left Column: Welcome Message + QuickAddBar */}
        <div className="space-y-4 md:col-span-2">
          {/* Welcome Message */}
          {fullName && (
            <div>
              <p className="text-lg text-gray-600">Xin chào, <span className="font-semibold text-pink-600">{fullName}</span></p>
            </div>
          )}
          
          {/* Quick Add Bar */}
          <QuickAddBar onClick={onQuickAdd} />
        </div>

        {/* Right Column: Today's Activity Summary */}
        <Card className="bg-[#f8c6d8] border-none shadow-md">
          <CardContent className="pt-6 pb-6">
             <div>
                <p className="text-sm text-gray-700 mb-3 font-medium">Tiến độ hôm nay</p>
                <div className="space-y-2">
                   <p className="font-semibold text-base flex items-center gap-2 text-gray-800">
                      <Apple className="size-4 text-gray-700" /> 
                      {caloriesConsumed > 0 ? `Đã ghi nhận ${Math.round(caloriesConsumed)} kcal` : 'Chưa ghi nhận dinh dưỡng'}
                   </p>
                   <p className="font-semibold text-base flex items-center gap-2 text-gray-800">
                       <TrendingDown className="size-4 text-gray-700" />
                       {caloriesBurned > 0 ? `Đã đốt ${Math.round(caloriesBurned)} kcal` : 'Chưa có hoạt động tập luyện'}
                   </p>
                </div>
             </div>
          </CardContent>
        </Card>
      </div>

      {/* Calories Summary Card */}
      <Card className="bg-[#f8c6d8] text-gray-800 border-none shadow-lg">
        <CardHeader className="pb-2">
          <CardTitle className="flex items-center gap-2 text-white/90 text-lg font-medium">
            <Flame className="size-5" />
            Calories
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex justify-between items-end">
            <div>
              <p className="text-5xl font-bold tracking-tight">{Math.round(netCalories)}</p>
              <p className="text-sm opacity-80 mt-1">/ {Math.round(calorieTarget)} kcal mục tiêu</p>
            </div>
            <div className="text-right">
              <div className="size-20 rounded-full border-4 border-white/30 flex items-center justify-center relative">
                 {/* Vòng tròn tiến độ đơn giản bằng SVG hoặc CSS */}
                 <svg className="absolute inset-0 size-full -rotate-90" viewBox="0 0 36 36">
                    <path
                      className="text-white/20"
                      d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="3"
                    />
                    <path
                      className="text-white drop-shadow-md"
                      strokeDasharray={`${caloriePercent}, 100`}
                      d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="3"
                    />
                 </svg>
                <span className="text-xl font-bold">{caloriePercent}%</span>
              </div>
            </div>
          </div>
          
          <div className="mt-6 grid grid-cols-3 gap-4 pt-4 border-t border-white/20">
            <div>
              <p className="text-xs opacity-70 uppercase tracking-wider">Đã ăn</p>
              <p className="font-bold text-lg">{Math.round(caloriesConsumed)}</p>
            </div>
            <div>
              <p className="text-xs opacity-70 uppercase tracking-wider">Tập luyện</p>
              <p className="font-bold text-lg">-{Math.round(caloriesBurned)}</p>
            </div>
            <div>
              <p className="text-xs opacity-70 uppercase tracking-wider">Còn lại</p>
              <p className="font-bold text-lg">{Math.max(0, Math.round(calorieTarget - netCalories))}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Charts Section: Weight & Calories */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Weight Chart */}
        <Card className="shadow-sm">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-gray-700">
              <TrendingDown className="size-5 text-cyan-600" />
              Theo dõi cân nặng
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="mb-6">
              <p className="text-3xl font-bold text-gray-900">{currentWeight > 0 ? `${currentWeight} kg` : '-- kg'}</p>
              <p className="text-sm text-gray-500">Biểu đồ 7 lần cân gần nhất</p>
            </div>
            
            <div className="h-[200px] w-full">
              {weightHistory.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={weightHistory}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5e7eb" />
                    <XAxis 
                      dataKey="date" 
                      axisLine={false} 
                      tickLine={false} 
                      tick={{fontSize: 12, fill: '#9ca3af'}} 
                      dy={10}
                    />
                    <YAxis 
                      domain={['dataMin - 1', 'dataMax + 1']} 
                      hide 
                    />
                    <Tooltip 
                      contentStyle={{borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'}}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="weight" 
                      stroke="#06b6d4" 
                      strokeWidth={3} 
                      dot={{fill: '#06b6d4', strokeWidth: 2, r: 4, stroke: '#fff'}}
                      activeDot={{r: 6}}
                    />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex items-center justify-center h-full text-gray-400 bg-gray-50">
                  Chưa có dữ liệu cân nặng
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Calories Chart - Last 30 Days */}
        <Card className="shadow-sm">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-gray-700">
              <Flame className="size-5 text-orange-600" />
              Dietary Energy
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="mb-6">
              <div className="flex items-center gap-6">
                <p className="text-xl font-bold text-gray-900">Last 30 Days</p>
                <div className="flex items-center gap-1">
                  <p className="text-xs text-gray-500">Daily Average:</p>
                  <p className="text-base font-bold" style={{color: '#F97316'}}>
                    {Math.round(caloriesHistory.reduce((sum, item) => sum + item.calories, 0) / caloriesHistory.length)} kcal
                  </p>
                </div>
                <div className="flex items-center gap-1">
                  <p className="text-xs text-gray-500">Goal:</p>
                  <p className="text-base font-bold" style={{color: '#84CC16'}}>
                    {calorieTarget} kcal
                  </p>
                </div>
              </div>
            </div>
            
            <div className="h-[250px] w-full">
              {caloriesHistory.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={caloriesHistory}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f3f4f6" />
                    <XAxis 
                      dataKey="date" 
                      axisLine={false} 
                      tickLine={false} 
                      tick={{fontSize: 11, fill: '#9ca3af'}} 
                      dy={10}
                      interval="preserveStartEnd"
                    />
                    <YAxis 
                      axisLine={false}
                      tickLine={false}
                      tick={{fontSize: 11, fill: '#9ca3af'}}
                      domain={[0, 1500]}
                      ticks={[0, 500, 1000, 1500]}
                    />
                    <Tooltip 
                      contentStyle={{borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)', fontSize: '12px'}}
                      formatter={(value: any) => [`${value} kcal`, 'Calories']}
                    />
                    <Bar 
                      dataKey="calories" 
                      fill="#F97316" 
                      radius={[6, 6, 0, 0]}
                      maxBarSize={30}
                    />
                    <ReferenceLine 
                      y={calorieTarget} 
                      stroke="#84CC16" 
                      strokeWidth={3}
                      ifOverflow="extendDomain"
                    />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex items-center justify-center h-full text-gray-400 bg-gray-50">
                  Chưa có dữ liệu calories
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Macros Summary */}
      {/* Truyền dữ liệu thật vào component MacroSummary */}
      <MacroSummary
        protein={{ current: Number(summary?.total_protein_g) || 0, goal: goal?.protein_grams || 150 }}
        carbs={{ current: Number(summary?.total_carbs_g) || 0, goal: goal?.carb_grams || 200 }}
        fat={{ current: Number(summary?.total_fat_g) || 0, goal: goal?.fat_grams || 70 }}
      />
    </div>
  );
}