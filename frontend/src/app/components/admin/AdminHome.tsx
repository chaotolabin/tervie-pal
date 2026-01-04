import { useState, useEffect } from 'react';
import { Users, Loader2, TrendingUp, Activity, AlertCircle } from 'lucide-react';
import { Card, CardContent } from '../ui/card';
import { toast } from 'sonner';


interface DashboardStats {
  totalUsers: number;
  activeToday: number;
  growthRate: number; // Ví dụ thêm tỉ lệ tăng trưởng
}

export default function AdminHome() {
  const [stats, setStats] = useState<DashboardStats>({ 
    totalUsers: 0, 
    activeToday: 0,
    growthRate: 0 
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardStats = async () => {
      try {
        const response = await fetch('/api/v1/admin/stats'); 
        
        if (!response.ok) {
          throw new Error('Lỗi mạng hoặc server không phản hồi');
        }

        const data = await response.json();
        
        
        setStats({
          totalUsers: data.total_users || 0,
          activeToday: data.active_today || 0,
          growthRate: data.growth_rate || 0
        });
      } catch (error) {
        console.error("Fetch Error:", error);
        toast.error("Không thể kết nối đến máy chủ để lấy dữ liệu");
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardStats();
  }, []);

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

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
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
                  {stats.growthRate}%
                </p>
              </div>
              <div className="bg-orange-50 p-3 rounded-xl">
                <TrendingUp className="text-orange-600 size-6" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Placeholder cho các biểu đồ API sau này */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-8">
         <div className="h-64 bg-gray-100 rounded-2xl border-2 border-dashed border-gray-200 flex items-center justify-center">
            <p className="text-gray-400 text-sm">Biểu đồ tăng trưởng (Đang đợi API dữ liệu lịch sử)</p>
         </div>
         <div className="h-64 bg-gray-100 rounded-2xl border-2 border-dashed border-gray-200 flex items-center justify-center">
            <p className="text-gray-400 text-sm">Phân bố người dùng (Đang đợi API dữ liệu vùng miền)</p>
         </div>
      </div>
    </div>
  );
}