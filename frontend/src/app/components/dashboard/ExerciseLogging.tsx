import { useState } from 'react';
import { Search, Plus, Filter, Clock } from 'lucide-react';
import { Input } from '../ui/input';
import { Button } from '../ui/button';
import { Card, CardContent } from '../ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Badge } from '../ui/badge';

const exerciseHistory = [
  { id: 1, name: 'Chạy bộ', duration: 30, calories: 300, time: '06:00', date: 'Hôm nay', intensity: 'Trung bình' },
  { id: 2, name: 'Yoga', duration: 45, calories: 135, time: '18:00', date: 'Hôm qua', intensity: 'Nhẹ' },
  { id: 3, name: 'Đạp xe', duration: 60, calories: 480, time: '07:00', date: '2 ngày trước', intensity: 'Cao' },
];

const categories = [
  { id: 'all', label: 'Tất cả', count: 25 },
  { id: 'cardio', label: 'Cardio', count: 10 },
  { id: 'strength', label: 'Sức mạnh', count: 8 },
  { id: 'flexibility', label: 'Linh hoạt', count: 7 },
];

export default function ExerciseLogging() {
  const [searchQuery, setSearchQuery] = useState('');
  const [activeCategory, setActiveCategory] = useState('all');

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Tập luyện</h2>
        <Button>
          <Plus className="size-4 mr-2" />
          Thêm mới
        </Button>
      </div>

      {/* Search and Filter */}
      <div className="flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-gray-400" />
          <Input
            placeholder="Tìm kiếm bài tập..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>
        <Button variant="outline" size="icon">
          <Filter className="size-4" />
        </Button>
      </div>

      {/* Category Tabs */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        {categories.map((category) => (
          <Button
            key={category.id}
            variant={activeCategory === category.id ? 'default' : 'outline'}
            onClick={() => setActiveCategory(category.id)}
            className="whitespace-nowrap"
          >
            {category.label}
            <Badge variant="secondary" className="ml-2">
              {category.count}
            </Badge>
          </Button>
        ))}
      </div>

      {/* Tabs */}
      <Tabs defaultValue="history" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="history">Lịch sử</TabsTrigger>
          <TabsTrigger value="custom">Tự tạo</TabsTrigger>
        </TabsList>

        <TabsContent value="history" className="space-y-3 mt-4">
          {exerciseHistory.map((exercise) => (
            <Card key={exercise.id} className="hover:shadow-md transition-shadow cursor-pointer">
              <CardContent className="p-4">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-start gap-2 mb-1">
                      <h3 className="font-semibold">{exercise.name}</h3>
                      <Badge variant="outline" className="text-xs">
                        {exercise.intensity}
                      </Badge>
                    </div>
                    <div className="flex items-center gap-3 text-sm text-gray-600">
                      <span className="flex items-center gap-1">
                        <Clock className="size-3" />
                        {exercise.duration} phút
                      </span>
                      <span>•</span>
                      <span>{exercise.date} • {exercise.time}</span>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-bold text-blue-600">-{exercise.calories} kcal</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </TabsContent>

        <TabsContent value="custom" className="mt-4">
          <div className="text-center py-12">
            <p className="text-gray-600 mb-4">Chưa có bài tập tự tạo</p>
            <Button>
              <Plus className="size-4 mr-2" />
              Tạo bài tập mới
            </Button>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
