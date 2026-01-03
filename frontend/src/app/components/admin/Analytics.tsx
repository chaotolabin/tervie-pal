import { TrendingUp, Users, Activity, Target } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

const userGrowthData = [
  { month: 'T7', newUsers: 120, totalUsers: 850 },
  { month: 'T8', newUsers: 150, totalUsers: 1000 },
  { month: 'T9', newUsers: 180, totalUsers: 1180 },
  { month: 'T10', newUsers: 220, totalUsers: 1400 },
  { month: 'T11', newUsers: 280, totalUsers: 1680 },
  { month: 'T12', newUsers: 170, totalUsers: 1850 },
];

const retentionData = [
  { cohort: 'Tuần 1', day1: 100, day7: 45, day30: 22 },
  { cohort: 'Tuần 2', day1: 100, day7: 48, day30: 25 },
  { cohort: 'Tuần 3', day1: 100, day7: 52, day30: 28 },
  { cohort: 'Tuần 4', day1: 100, day7: 55, day30: 30 },
];

const activityData = [
  { date: '25/12', meals: 4250, exercises: 1820, biometrics: 850 },
  { date: '26/12', meals: 4380, exercises: 1950, biometrics: 920 },
  { date: '27/12', meals: 4520, exercises: 2100, biometrics: 980 },
  { date: '28/12', meals: 4680, exercises: 2050, biometrics: 1020 },
  { date: '29/12', meals: 4850, exercises: 2200, biometrics: 1150 },
  { date: '30/12', meals: 3920, exercises: 1680, biometrics: 850 },
  { date: '31/12', meals: 3650, exercises: 1520, biometrics: 720 },
];

export default function Analytics() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Phân tích & Thống kê</h1>
          <p className="text-gray-600 mt-1">Dữ liệu chi tiết về người dùng và hoạt động</p>
        </div>
        <Select defaultValue="30d">
          <SelectTrigger className="w-40">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="7d">7 ngày</SelectItem>
            <SelectItem value="30d">30 ngày</SelectItem>
            <SelectItem value="90d">90 ngày</SelectItem>
            <SelectItem value="1y">1 năm</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between mb-2">
              <div>
                <p className="text-sm text-gray-600">DAU</p>
                <p className="text-3xl font-bold">856</p>
              </div>
              <Users className="size-10 text-blue-500" />
            </div>
            <p className="text-sm text-green-600">+5.2% vs hôm qua</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between mb-2">
              <div>
                <p className="text-sm text-gray-600">WAU</p>
                <p className="text-3xl font-bold">1,280</p>
              </div>
              <Activity className="size-10 text-green-500" />
            </div>
            <p className="text-sm text-green-600">+8.1% vs tuần trước</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between mb-2">
              <div>
                <p className="text-sm text-gray-600">MAU</p>
                <p className="text-3xl font-bold">1,650</p>
              </div>
              <TrendingUp className="size-10 text-purple-500" />
            </div>
            <p className="text-sm text-green-600">+12.5% vs tháng trước</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between mb-2">
              <div>
                <p className="text-sm text-gray-600">Retention</p>
                <p className="text-3xl font-bold">30%</p>
              </div>
              <Target className="size-10 text-orange-500" />
            </div>
            <p className="text-sm text-gray-600">30-day retention</p>
          </CardContent>
        </Card>
      </div>

      {/* User Growth Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Tăng trưởng người dùng</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={350}>
            <LineChart data={userGrowthData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis yAxisId="left" />
              <YAxis yAxisId="right" orientation="right" />
              <Tooltip />
              <Legend />
              <Line yAxisId="left" type="monotone" dataKey="newUsers" stroke="#3b82f6" strokeWidth={2} name="Người dùng mới" />
              <Line yAxisId="right" type="monotone" dataKey="totalUsers" stroke="#10b981" strokeWidth={2} name="Tổng người dùng" />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Activity Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Hoạt động người dùng - 7 ngày qua</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={350}>
            <BarChart data={activityData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="meals" fill="#8b5cf6" name="Bữa ăn" />
              <Bar dataKey="exercises" fill="#f97316" name="Bài tập" />
              <Bar dataKey="biometrics" fill="#06b6d4" name="Chỉ số" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Retention Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Retention (Tỷ lệ giữ chân)</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={retentionData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="cohort" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="day1" stroke="#3b82f6" strokeWidth={2} name="Day 1" />
              <Line type="monotone" dataKey="day7" stroke="#10b981" strokeWidth={2} name="Day 7" />
              <Line type="monotone" dataKey="day30" stroke="#f59e0b" strokeWidth={2} name="Day 30" />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Additional Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-gray-600 mb-1">Avg. Sessions/User</p>
            <p className="text-3xl font-bold">4.2</p>
            <p className="text-sm text-green-600 mt-1">+0.3 vs tháng trước</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-gray-600 mb-1">Avg. Session Duration</p>
            <p className="text-3xl font-bold">5:32</p>
            <p className="text-sm text-gray-600 mt-1">phút</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-gray-600 mb-1">Churn Rate</p>
            <p className="text-3xl font-bold">8.5%</p>
            <p className="text-sm text-red-600 mt-1">-1.2% vs tháng trước</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
