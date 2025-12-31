import { Calendar, Flame, TrendingDown, Apple, Dumbbell, Target } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface DashboardHomeProps {
  onQuickAdd: () => void;
}

const weightData = [
  { date: '01/12', weight: 75 },
  { date: '08/12', weight: 74.5 },
  { date: '15/12', weight: 74 },
  { date: '22/12', weight: 73.5 },
  { date: '29/12', weight: 73 },
];

export default function DashboardHome({ onQuickAdd }: DashboardHomeProps) {
  return (
    <div className="space-y-6">
      {/* Date Range Selector */}
      <div className="flex justify-between items-center">
        <div className="flex items-center gap-2">
          <Calendar className="size-5 text-gray-600" />
          <h2 className="text-xl font-semibold">Tổng quan</h2>
        </div>
        <Select defaultValue="today">
          <SelectTrigger className="w-32">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="today">Hôm nay</SelectItem>
            <SelectItem value="7d">7 ngày</SelectItem>
            <SelectItem value="1m">1 tháng</SelectItem>
            <SelectItem value="3m">3 tháng</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Calories Summary */}
      <Card className="bg-gradient-to-br from-green-500 to-green-600 text-white">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-white">
            <Flame className="size-5" />
            Calories hôm nay
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex justify-between items-end">
            <div>
              <p className="text-4xl font-bold">1,850</p>
              <p className="text-sm opacity-90">/ 2,000 kcal mục tiêu</p>
            </div>
            <div className="text-right">
              <div className="size-20 rounded-full border-4 border-white/30 flex items-center justify-center">
                <span className="text-xl font-bold">93%</span>
              </div>
            </div>
          </div>
          <div className="mt-4 grid grid-cols-3 gap-4 pt-4 border-t border-white/20">
            <div>
              <p className="text-xs opacity-80">Đã ăn</p>
              <p className="font-semibold">1,850</p>
            </div>
            <div>
              <p className="text-xs opacity-80">Tập luyện</p>
              <p className="font-semibold">-350</p>
            </div>
            <div>
              <p className="text-xs opacity-80">Còn lại</p>
              <p className="font-semibold">500</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Weight Chart */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingDown className="size-5 text-blue-600" />
            Cân nặng
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="mb-4">
            <p className="text-3xl font-bold">73.0 kg</p>
            <p className="text-sm text-gray-600">-2.0 kg trong tháng này</p>
          </div>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={weightData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis domain={[72, 76]} />
              <Tooltip />
              <Line type="monotone" dataKey="weight" stroke="#3b82f6" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Macros Summary */}
      <div className="grid grid-cols-3 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600">Protein</span>
              <span className="font-semibold">85g</span>
            </div>
            <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
              <div className="h-full bg-red-500" style={{ width: '75%' }} />
            </div>
            <p className="text-xs text-gray-500 mt-1">75% / 110g</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600">Carbs</span>
              <span className="font-semibold">220g</span>
            </div>
            <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
              <div className="h-full bg-blue-500" style={{ width: '88%' }} />
            </div>
            <p className="text-xs text-gray-500 mt-1">88% / 250g</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600">Fat</span>
              <span className="font-semibold">52g</span>
            </div>
            <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
              <div className="h-full bg-yellow-500" style={{ width: '65%' }} />
            </div>
            <p className="text-xs text-gray-500 mt-1">65% / 80g</p>
          </CardContent>
        </Card>
      </div>

      {/* Streak & Quick Actions */}
      <div className="grid grid-cols-2 gap-4">
        <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white">
          <CardContent className="pt-6">
            <Target className="size-8 mb-2 opacity-80" />
            <p className="text-2xl font-bold">7 ngày</p>
            <p className="text-sm opacity-90">Streak hiện tại 🔥</p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-orange-500 to-orange-600 text-white">
          <CardContent className="pt-6 flex flex-col h-full">
            <div className="flex-1">
              <p className="text-sm opacity-90 mb-1">Hôm nay</p>
              <p className="font-semibold">3 bữa ăn</p>
              <p className="font-semibold">1 bài tập</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Add CTA */}
      <Card className="border-2 border-dashed border-gray-300 hover:border-green-500 transition-colors cursor-pointer" onClick={onQuickAdd}>
        <CardContent className="pt-6 text-center">
          <div className="size-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
            <Apple className="size-6 text-green-600" />
          </div>
          <p className="font-semibold mb-1">Thêm nhanh</p>
          <p className="text-sm text-gray-600">Ghi nhận thực phẩm hoặc bài tập</p>
        </CardContent>
      </Card>
    </div>
  );
}
