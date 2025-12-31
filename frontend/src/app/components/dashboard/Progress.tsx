import { TrendingDown, Calendar, Target } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

const weightData = [
  { date: '01/12', weight: 75, goal: 73 },
  { date: '05/12', weight: 74.8, goal: 73 },
  { date: '10/12', weight: 74.3, goal: 73 },
  { date: '15/12', weight: 74, goal: 73 },
  { date: '20/12', weight: 73.5, goal: 73 },
  { date: '25/12', weight: 73.2, goal: 73 },
  { date: '31/12', weight: 73, goal: 73 },
];

const caloriesData = [
  { date: '25/12', calories: 1850, target: 2000 },
  { date: '26/12', calories: 1950, target: 2000 },
  { date: '27/12', calories: 1780, target: 2000 },
  { date: '28/12', calories: 2100, target: 2000 },
  { date: '29/12', calories: 1920, target: 2000 },
  { date: '30/12', calories: 1850, target: 2000 },
  { date: '31/12', calories: 1850, target: 2000 },
];

export default function Progress() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Tiến độ</h2>
        <Select defaultValue="1m">
          <SelectTrigger className="w-32">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="7d">7 ngày</SelectItem>
            <SelectItem value="1m">1 tháng</SelectItem>
            <SelectItem value="3m">3 tháng</SelectItem>
            <SelectItem value="1y">1 năm</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="bg-gradient-to-br from-green-500 to-green-600 text-white">
          <CardContent className="pt-6">
            <div className="flex items-start justify-between mb-2">
              <div>
                <p className="text-sm opacity-90">Cân nặng hiện tại</p>
                <p className="text-3xl font-bold mt-1">73.0 kg</p>
              </div>
              <TrendingDown className="size-8 opacity-80" />
            </div>
            <p className="text-sm opacity-90">-2.0 kg trong tháng này 🎉</p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white">
          <CardContent className="pt-6">
            <div className="flex items-start justify-between mb-2">
              <div>
                <p className="text-sm opacity-90">Trung bình/ngày</p>
                <p className="text-3xl font-bold mt-1">1,920</p>
              </div>
              <Calendar className="size-8 opacity-80" />
            </div>
            <p className="text-sm opacity-90">kcal (96% mục tiêu)</p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white">
          <CardContent className="pt-6">
            <div className="flex items-start justify-between mb-2">
              <div>
                <p className="text-sm opacity-90">Streak</p>
                <p className="text-3xl font-bold mt-1">7 ngày</p>
              </div>
              <Target className="size-8 opacity-80" />
            </div>
            <p className="text-sm opacity-90">Tiếp tục phát huy! 🔥</p>
          </CardContent>
        </Card>
      </div>

      {/* Weight Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Biểu đồ cân nặng</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={weightData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis domain={[72, 76]} />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="weight" stroke="#3b82f6" strokeWidth={2} name="Cân nặng" />
              <Line type="monotone" dataKey="goal" stroke="#10b981" strokeWidth={2} strokeDasharray="5 5" name="Mục tiêu" />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Calories Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Calories 7 ngày qua</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={caloriesData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="calories" fill="#3b82f6" name="Đã ăn" />
              <Bar dataKey="target" fill="#cbd5e1" name="Mục tiêu" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 gap-4">
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-gray-600 mb-1">Tổng bữa ăn</p>
            <p className="text-3xl font-bold">89 bữa</p>
            <p className="text-sm text-green-600 mt-1">+12 so với tháng trước</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-gray-600 mb-1">Tổng bài tập</p>
            <p className="text-3xl font-bold">23 bài</p>
            <p className="text-sm text-green-600 mt-1">+5 so với tháng trước</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-gray-600 mb-1">Calories tiêu hao</p>
            <p className="text-3xl font-bold">8,250</p>
            <p className="text-sm text-blue-600 mt-1">kcal tập luyện</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-gray-600 mb-1">Ngày đạt mục tiêu</p>
            <p className="text-3xl font-bold">22/31</p>
            <p className="text-sm text-purple-600 mt-1">71% tháng này</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
