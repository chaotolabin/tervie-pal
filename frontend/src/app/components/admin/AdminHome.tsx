import { useState, useEffect } from 'react';
import { Users, Loader2, TrendingUp } from 'lucide-react';
import { Card, CardContent } from '../ui/card';
import { toast } from 'sonner';

export default function AdminHome() {
  const [stats, setStats] = useState({ totalUsers: 0, activeToday: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardStats = async () => {
      try {
        const response = await fetch('/api/v1/admin/stats'); 
        const data = await response.json();
        setStats({
          totalUsers: data.total_users,
          activeToday: data.active_today
        });
      } catch (error) {
        toast.error("Không thể lấy dữ liệu thống kê");
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardStats();
  }, []);

  if (loading) return <div className="flex justify-center p-10"><Loader2 className="animate-spin" /></div>;

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-800">Tervie Pal Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="bg-white border-l-4 border-blue-500">
          <CardContent className="pt-6">
            <div className="flex justify-between items-center">
              <div>
                <p className="text-sm text-gray-500 uppercase font-bold">Tổng người dùng</p>
                <p className="text-3xl font-bold">{stats.totalUsers.toLocaleString()}</p>
              </div>
              <Users className="text-blue-500 size-10" />
            </div>
          </CardContent>
        </Card>
        {}
      </div>
    </div>
  );
}