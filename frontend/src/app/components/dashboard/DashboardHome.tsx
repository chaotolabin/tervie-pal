import React, { useState, useEffect } from 'react';
import { Calendar, Flame, TrendingDown, Apple, Loader2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import MacroSummary from './MacroSummary';
import QuickAddBar from './QuickAddBar';
import api from '../lib/api'; // Đảm bảo import đúng đường dẫn api client
import { toast } from 'sonner';

interface DashboardHomeProps {
  onQuickAdd: () => void;
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

export default function DashboardHome({ onQuickAdd }: DashboardHomeProps) {
  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState<DailySummary | null>(null);
  const [goal, setGoal] = useState<UserGoal | null>(null);
  const [weightHistory, setWeightHistory] = useState<any[]>([]);
  const [currentWeight, setCurrentWeight] = useState<number>(0);

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
      {/* Date Range Selector & Welcome */}
      <div className="flex justify-between items-center">
        <div className="flex items-center gap-2">
          <Calendar className="size-5 text-gray-600" />
          <h2 className="text-xl font-semibold">Hôm nay</h2>
        </div>
        <Select defaultValue="today">
          <SelectTrigger className="w-32 bg-white">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="today">Hôm nay</SelectItem>
            {/* Các option khác cần xử lý logic filter sau */}
          </SelectContent>
        </Select>
      </div>

      {/* Quick Add Bar - Positioned before Calories Net card */}
      <QuickAddBar onClick={onQuickAdd} />

      {/* Calories Summary Card */}
      <Card className="bg-gradient-to-br from-pink-500 to-purple-600 text-white border-none shadow-lg">
        <CardHeader className="pb-2">
          <CardTitle className="flex items-center gap-2 text-white/90 text-lg font-medium">
            <Flame className="size-5" />
            Calories ròng (Net)
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
              <div className="flex items-center justify-center h-full text-gray-400 bg-gray-50 rounded-lg">
                Chưa có dữ liệu cân nặng
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Macros Summary */}
      {/* Truyền dữ liệu thật vào component MacroSummary */}
      <MacroSummary
        protein={{ current: Number(summary?.total_protein_g) || 0, goal: goal?.protein_grams || 150 }}
        carbs={{ current: Number(summary?.total_carbs_g) || 0, goal: goal?.carb_grams || 200 }}
        fat={{ current: Number(summary?.total_fat_g) || 0, goal: goal?.fat_grams || 70 }}
      />

      {/* Today's Activity Card */}
      <Card className="bg-gradient-to-br from-orange-500 to-amber-500 text-white border-none shadow-md">
        <CardContent className="pt-6 flex flex-col h-full justify-between">
           <div>
              <p className="text-sm opacity-90 mb-2 font-medium">Hoạt động hôm nay</p>
              <div className="space-y-1">
                 {/* Dữ liệu này có thể lấy chi tiết hơn nếu cần, tạm thời dùng summary */}
                 <p className="font-bold text-lg flex items-center gap-2">
                    <Apple className="size-4 opacity-80" /> 
                    {/* Backend không trả về count món ăn trong summary, có thể bổ sung sau */}
                    Đã ghi nhận dinh dưỡng
                 </p>
                 <p className="font-bold text-lg flex items-center gap-2">
                     <TrendingDown className="size-4 opacity-80" />
                     {caloriesBurned > 0 ? 'Đã có tập luyện' : 'Chưa tập luyện'}
                 </p>
              </div>
           </div>
           <div className="mt-4 pt-4 border-t border-white/20 text-xs opacity-80">
              Tiếp tục phát huy nhé!
           </div>
        </CardContent>
      </Card>
    </div>
  );
}