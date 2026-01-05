import React, { useState, useEffect } from 'react';
import { Flame, Trophy, Activity, Users, Calendar, Loader2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';

interface StreakSummary {
  avg_current_streak: number;
  max_longest_streak: number;
  total_users_active: number;
}

interface StreakDistribution {
  range: string;
  count: number;
}

interface ActivityStatus {
  date: string;
  green_count: number;  // Status: green (đúng hạn)
  yellow_count: number; // Status: yellow (trễ)
}

export default function Analytics() {
  const [summary, setSummary] = useState<StreakSummary | null>(null);
  const [distribution, setDistribution] = useState<StreakDistribution[]>([]);
  const [activity, setActivity] = useState<ActivityStatus[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAdminData = async () => {
      setLoading(true);
      try {
        const { AdminService } = await import('../../../service/admin.service');
        // Lấy tất cả users (top_n = 0) để tính phân bổ chính xác
        const data = await AdminService.getStreakDashboard('30d', 0);
        
        // Map backend response to frontend format
        const streakStats = data.streak_stats;
        setSummary({
          avg_current_streak: streakStats?.average_streak || streakStats?.avg_current_streak || 0,
          max_longest_streak: streakStats?.highest_streak || 0,
          total_users_active: streakStats?.users_with_streak || 0
        });
        
        // Create distribution from all streak users 
        if (streakStats?.top_streak_users && streakStats.top_streak_users.length > 0) {
          const dist: StreakDistribution[] = [
            { range: '0-3 ngày', count: 0 },
            { range: '3-7 ngày', count: 0 },
            { range: '7-21 ngày', count: 0 },
            { range: '21+ ngày', count: 0 }
          ];
          
          streakStats.top_streak_users.forEach((user: any) => {
            const streak = user.current_streak || 0;
            if (streak < 3) dist[0].count++;
            else if (streak < 7) dist[1].count++;
            else if (streak < 21) dist[2].count++;
            else dist[3].count++;
          });
          
          setDistribution(dist);
        } else {
          setDistribution([]);
        }
        
        // Activity data - get from daily stats
        try {
          const dailyData = await AdminService.getDailyStats(7);
          if (dailyData.items && dailyData.items.length > 0) {
            const activityData = dailyData.items.map((item: any) => ({
              date: new Date(item.date_log).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit' }),
              green_count: item.users_hit_calorie_target || 0,
              yellow_count: (item.active_users || 0) - (item.users_hit_calorie_target || 0)
            }));
            setActivity(activityData);
          } else {
            setActivity([]);
          }
        } catch (e) {
          console.error("Error fetching daily stats:", e);
          setActivity([]);
        }
      } catch (error) {
        console.error("Lỗi lấy dữ liệu từ Backend:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchAdminData();
  }, []);

  // Hàm lấy màu dựa trên range
  const getColorByRange = (range: string): string => {
    if (range === '0-3 ngày') return '#94a3b8'; // Xám
    if (range === '3-7 ngày') return '#eab308'; // Vàng
    if (range === '7-21 ngày') return '#22c55e'; // Xanh
    if (range === '21+ ngày') return '#3b82f6'; // Xanh dương
    return '#94a3b8'; // Default: xám
  };

  if (loading) return (
    <div className="flex flex-col items-center justify-center h-96">
      <Loader2 className="animate-spin text-blue-500 size-10 mb-4" />
      <p className="text-slate-500">Đang tải dữ liệu từ hệ thống...</p>
    </div>
  );

  return (
    <div className="space-y-6 p-6">
      <header>
        <h1 className="text-3xl font-bold tracking-tight">Thống kê hệ thống</h1>
        <p className="text-muted-foreground">Dữ liệu tổng hợp từ UserStreakState và StreakDayCache</p>
      </header>

      {/* 1. Metric Cards: Lấy từ UserStreakState */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="border-orange-100 bg-orange-50/30">
          <CardContent className="pt-6">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-sm font-medium text-orange-600 uppercase">Số streak trung bình</p>
                <h3 className="text-3xl font-bold text-orange-700 mt-1">{summary?.avg_current_streak.toFixed(0)}</h3>
              </div>
              <Flame className="size-8 text-orange-500 fill-orange-500" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-yellow-100 bg-yellow-50/30">
          <CardContent className="pt-6">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-sm font-medium text-yellow-600 uppercase">Kỷ lục hệ thống</p>
                <h3 className="text-3xl font-bold text-yellow-700 mt-1">{summary?.max_longest_streak} ngày</h3>
              </div>
              <Trophy className="size-8 text-yellow-500 fill-yellow-500" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-blue-100 bg-blue-50/30">
          <CardContent className="pt-6">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-sm font-medium text-blue-600 uppercase">User đang hoạt động</p>
                <h3 className="text-3xl font-bold text-blue-700 mt-1">{summary?.total_users_active}</h3>
              </div>
              <Users className="size-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 2. Biểu đồ phân bổ Streak: Dựa trên current_streak của users */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg font-semibold flex items-center gap-2">
              <Activity className="size-5" /> Phân bổ độ chăm chỉ
            </CardTitle>
          </CardHeader>
          <CardContent className="h-[350px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={distribution}
                  cx="50%"
                  cy="50%"
                  innerRadius={70}
                  outerRadius={100}
                  paddingAngle={5}
                  dataKey="count"
                  nameKey="range"
                >
                  {distribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={getColorByRange(entry.range)} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend verticalAlign="bottom" height={36}/>
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* 3. Biểu đồ Trạng thái: Dựa trên StreakDayCache (Green vs Yellow) */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg font-semibold flex items-center gap-2">
              <Calendar className="size-5" /> Chất lượng hoàn thành 7 ngày qua
            </CardTitle>
          </CardHeader>
          <CardContent className="h-[350px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={activity}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="green_count" name="Đúng hạn (Green)" fill="#22c55e" radius={[4, 4, 0, 0]} />
                <Bar dataKey="yellow_count" name="Trễ hạn (Yellow)" fill="#eab308" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}