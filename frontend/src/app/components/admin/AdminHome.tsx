import { Users, UserCheck, Utensils, Dumbbell, TrendingUp } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

const growthData = [
  { date: '01/12', users: 1200, active: 850 },
  { date: '08/12', users: 1350, active: 920 },
  { date: '15/12', users: 1520, active: 1050 },
  { date: '22/12', users: 1680, active: 1150 },
  { date: '29/12', users: 1850, active: 1280 },
];

const activityData = [
  { date: 'T2', meals: 4250, exercises: 1820 },
  { date: 'T3', meals: 4380, exercises: 1950 },
  { date: 'T4', meals: 4520, exercises: 2100 },
  { date: 'T5', meals: 4680, exercises: 2050 },
  { date: 'T6', meals: 4850, exercises: 2200 },
  { date: 'T7', meals: 3920, exercises: 1680 },
  { date: 'CN', meals: 3650, exercises: 1520 },
];

export default function AdminHome() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Tổng quan hệ thống</h1>
        <p className="text-gray-600 mt-1">Thống kê và phân tích tổng thể</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white">
          <CardContent className="pt-6">
            <div className="flex items-start justify-between mb-2">
              <div>
                <p className="text-sm opacity-90">Tổng người dùng</p>
                <p className="text-3xl font-bold mt-1">1,850</p>
              </div>
              <Users className="size-10 opacity-80" />
            </div>
            <p className="text-sm opacity-90">+170 so với tháng trước</p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-green-500 to-green-600 text-white">
          <CardContent className="pt-6">
            <div className="flex items-start justify-between mb-2">
              <div>
                <p className="text-sm opacity-90">Người dùng hoạt động</p>
                <p className="text-3xl font-bold mt-1">1,280</p>
              </div>
              <UserCheck className="size-10 opacity-80" />
            </div>
            <p className="text-sm opacity-90">69% tổng số người dùng</p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white">
          <CardContent className="pt-6">
            <div className="flex items-start justify-between mb-2">
              <div>
                <p className="text-sm opacity-90">Bữa ăn ghi nhận</p>
                <p className="text-3xl font-bold mt-1">32,500</p>
              </div>
              <Utensils className="size-10 opacity-80" />
            </div>
            <p className="text-sm opacity-90">Tuần này</p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-orange-500 to-orange-600 text-white">
          <CardContent className="pt-6">
            <div className="flex items-start justify-between mb-2">
              <div>
                <p className="text-sm opacity-90">Bài tập ghi nhận</p>
                <p className="text-3xl font-bold mt-1">13,320</p>
              </div>
              <Dumbbell className="size-10 opacity-80" />
            </div>
            <p className="text-sm opacity-90">Tuần này</p>
          </CardContent>
        </Card>
      </div>

      {/* Growth Chart */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="size-5 text-green-600" />
            Tăng trưởng người dùng
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={growthData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="users" stroke="#3b82f6" strokeWidth={2} name="Tổng người dùng" />
              <Line type="monotone" dataKey="active" stroke="#10b981" strokeWidth={2} name="Người dùng hoạt động" />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Activity Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Hoạt động tuần này</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={activityData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="meals" fill="#8b5cf6" name="Bữa ăn" />
              <Bar dataKey="exercises" fill="#f97316" name="Bài tập" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-gray-600 mb-1">DAU (Daily Active Users)</p>
            <p className="text-3xl font-bold">856</p>
            <p className="text-sm text-green-600 mt-1">+5.2% so với hôm qua</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-gray-600 mb-1">WAU (Weekly Active Users)</p>
            <p className="text-3xl font-bold">1,280</p>
            <p className="text-sm text-green-600 mt-1">+8.1% so với tuần trước</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-gray-600 mb-1">MAU (Monthly Active Users)</p>
            <p className="text-3xl font-bold">1,650</p>
            <p className="text-sm text-green-600 mt-1">+12.5% so với tháng trước</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
