import React, { useState, useEffect } from 'react';
import { Users, Loader2, TrendingUp, Activity, AlertCircle } from 'lucide-react';
import { Card, CardContent } from '../ui/card';
import { toast } from 'sonner';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';

interface DashboardStats {
  totalUsers: number;
  activeToday: number;
  growthRate: number;
  postsCount: number;
  openTickets: number;
}

interface DailyStat {
  date_log: string;
  total_users: number;
  new_users: number;
  active_users: number;
  new_posts: number;
}

export default function AdminHome() {
  const [stats, setStats] = useState<DashboardStats>({ 
    totalUsers: 0, 
    activeToday: 0,
    growthRate: 0,
    postsCount: 0,
    openTickets: 0
  });
  const [dailyStats, setDailyStats] = useState<DailyStat[]>([]);
  const [loading, setLoading] = useState(true);
  const [range, setRange] = useState<'7d' | '30d' | '90d'>('30d');

  useEffect(() => {
    const fetchDashboardStats = async () => {
      try {
        setLoading(true);
        const { AdminService } = await import('../../../service/admin.service');
        
        // Fetch dashboard summary, core dashboard (for DAU), và daily stats
        const [dashboardData, coreData, dailyData] = await Promise.all([
          AdminService.getDashboard(),
          AdminService.getCoreDashboard('7d'), // Lấy DAU từ retention metrics
          AdminService.getDailyStats(range === '7d' ? 7 : range === '30d' ? 30 : 90)
        ]);
        
        // Calculate growth rate from daily stats
        let growthRate = 0;
        if (dailyData.items && dailyData.items.length >= 2) {
          const sorted = [...dailyData.items].sort((a, b) => 
            new Date(a.date_log).getTime() - new Date(b.date_log).getTime()
          );
          const first = sorted[0];
          const last = sorted[sorted.length - 1];
          if (first.total_users > 0) {
            growthRate = ((last.total_users - first.total_users) / first.total_users) * 100;
          }
        }
        
        // Get active today (DAU - Daily Active Users trong 24h qua)
        const activeToday = coreData?.retention_metrics?.dau || 0;
        
        setStats({
          totalUsers: dashboardData.users_count || 0,
          activeToday: activeToday,
          growthRate: Math.round(growthRate * 10) / 10,
          postsCount: dashboardData.posts_count || 0,
          openTickets: dashboardData.open_tickets_count || 0
        });
        
        // Format daily stats for charts

        const formatted = (dailyData.items || [])
          .map((item: any) => ({
            date_log: new Date(item.date_log).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit' }),
            total_users: item.total_users || 0,
            new_users: item.new_users || 0,
            active_users: item.active_users || 0,
            new_posts: item.new_posts || 0
          }));
        setDailyStats(formatted);
      } catch (error: any) {
        console.error("Fetch Error:", error);
        toast.error(error.response?.data?.detail || "Không thể kết nối đến máy chủ để lấy dữ liệu");
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardStats();
  }, [range]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] gap-2">
        <Loader2 className="animate-spin text-green-600 size-10" />
        <p className="text-gray-500 animate-pulse">Đang tải dữ liệu hệ thống...</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Tervie Pal Dashboard</h1>
        <p className="text-gray-500 mt-1">Chào mừng quay trở lại, đây là tình hình hệ thống hôm nay.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
        {/* Tổng người dùng */}
        <Card className="bg-white hover:shadow-md transition-shadow border-none ring-1 ring-gray-200">
          <CardContent className="pt-6">
            <div className="flex justify-between items-center">
              <div>
                <p className="text-xs text-gray-400 uppercase font-black tracking-wider">Tổng người dùng</p>
                <p className="text-3xl font-extrabold text-gray-900 mt-1">
                  {stats.totalUsers.toLocaleString()}
                </p>
              </div>
              <div className="bg-blue-50 p-3 rounded-xl">
                <Users className="text-blue-600 size-6" />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Hoạt động hôm nay */}
        <Card className="bg-white hover:shadow-md transition-shadow border-none ring-1 ring-gray-200">
          <CardContent className="pt-6">
            <div className="flex justify-between items-center">
              <div>
                <p className="text-xs text-gray-400 uppercase font-black tracking-wider">Hoạt động hôm nay</p>
                <p className="text-3xl font-extrabold text-gray-900 mt-1">
                  {stats.activeToday.toLocaleString()}
                </p>
              </div>
              <div className="bg-green-50 p-3 rounded-xl">
                <Activity className="text-green-600 size-6" />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Tăng trưởng */}
        <Card className="bg-white hover:shadow-md transition-shadow border-none ring-1 ring-gray-200">
          <CardContent className="pt-6">
            <div className="flex justify-between items-center">
              <div>
                <p className="text-xs text-gray-400 uppercase font-black tracking-wider">Tăng trưởng</p>
                <p className="text-3xl font-extrabold text-gray-900 mt-1">
                  {stats.growthRate > 0 ? '+' : ''}{stats.growthRate}%
                </p>
              </div>
              <div className="bg-orange-50 p-3 rounded-xl">
                <TrendingUp className="text-orange-600 size-6" />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Tổng bài viết */}
        <Card className="bg-white hover:shadow-md transition-shadow border-none ring-1 ring-gray-200">
          <CardContent className="pt-6">
            <div className="flex justify-between items-center">
              <div>
                <p className="text-xs text-gray-400 uppercase font-black tracking-wider">Tổng bài viết</p>
                <p className="text-3xl font-extrabold text-gray-900 mt-1">
                  {stats.postsCount.toLocaleString()}
                </p>
              </div>
              <div className="bg-purple-50 p-3 rounded-xl">
                <AlertCircle className="text-purple-600 size-6" />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Tickets đang mở */}
        <Card className="bg-white hover:shadow-md transition-shadow border-none ring-1 ring-gray-200">
          <CardContent className="pt-6">
            <div className="flex justify-between items-center">
              <div>
                <p className="text-xs text-gray-400 uppercase font-black tracking-wider">Tickets mở</p>
                <p className="text-3xl font-extrabold text-gray-900 mt-1">
                  {stats.openTickets.toLocaleString()}
                </p>
              </div>
              <div className="bg-red-50 p-3 rounded-xl">
                <AlertCircle className="text-red-600 size-6" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Range selector */}
      <div className="flex gap-2 mb-4">
        <button
          onClick={() => setRange('7d')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            range === '7d' 
              ? 'bg-blue-600 text-white' 
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          7 ngày
        </button>
        <button
          onClick={() => setRange('30d')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            range === '30d' 
              ? 'bg-blue-600 text-white' 
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          30 ngày
        </button>
        <button
          onClick={() => setRange('90d')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            range === '90d' 
              ? 'bg-blue-600 text-white' 
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          90 ngày
        </button>
      </div>

      {/* Biểu đồ */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-8">
        {/* Biểu đồ tăng trưởng người dùng */}
        <Card className="bg-white">
          <CardContent className="pt-6">
            <h3 className="text-lg font-semibold mb-4">Tăng trưởng người dùng</h3>
            {dailyStats.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={dailyStats}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="date_log" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="total_users" 
                    name="Tổng người dùng" 
                    stroke="#3b82f6" 
                    strokeWidth={2}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="new_users" 
                    name="Người dùng mới" 
                    stroke="#10b981" 
                    strokeWidth={2}
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-64 flex items-center justify-center text-gray-400">
                Chưa có dữ liệu
              </div>
            )}
          </CardContent>
        </Card>

        {/* Biểu đồ hoạt động */}
        <Card className="bg-white">
          <CardContent className="pt-6">
            <h3 className="text-lg font-semibold mb-4">Hoạt động hàng ngày</h3>
            {dailyStats.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={dailyStats}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="date_log" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="active_users" name="Người dùng hoạt động" fill="#10b981" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="new_posts" name="Bài viết mới" fill="#f59e0b" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-64 flex items-center justify-center text-gray-400">
                Chưa có dữ liệu
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}