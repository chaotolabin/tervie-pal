import { useState } from 'react';
import { Search, Plus, Filter } from 'lucide-react';
import { Input } from '../ui/input';
import { Button } from '../ui/button';
import { Card, CardContent } from '../ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Badge } from '../ui/badge';

const foodHistory = [
  { id: 1, name: 'Cơm trắng', calories: 130, time: '07:30', meal: 'Sáng', date: 'Hôm nay' },
  { id: 2, name: 'Thịt gà luộc', calories: 165, time: '12:00', meal: 'Trưa', date: 'Hôm nay' },
  { id: 3, name: 'Trứng gà', calories: 155, time: '07:00', meal: 'Sáng', date: 'Hôm qua' },
];

const foodCategories = [
  { id: 'all', label: 'Tất cả', count: 50 },
  { id: 'breakfast', label: 'Sáng', count: 12 },
  { id: 'lunch', label: 'Trưa', count: 15 },
  { id: 'dinner', label: 'Tối', count: 18 },
  { id: 'snack', label: 'Phụ', count: 5 },
];

export default function FoodLogging() {
  const [searchQuery, setSearchQuery] = useState('');
  const [activeCategory, setActiveCategory] = useState('all');

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Thực phẩm</h2>
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
            placeholder="Tìm kiếm thực phẩm..."
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
        {foodCategories.map((category) => (
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
          {foodHistory.map((food) => (
            <Card key={food.id} className="hover:shadow-md transition-shadow cursor-pointer">
              <CardContent className="p-4">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-start gap-2 mb-1">
                      <h3 className="font-semibold">{food.name}</h3>
                      <Badge variant="outline" className="text-xs">
                        {food.meal}
                      </Badge>
                    </div>
                    <p className="text-sm text-gray-600">
                      {food.date} • {food.time}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-bold text-green-600">{food.calories} kcal</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </TabsContent>

        <TabsContent value="custom" className="mt-4">
          <div className="text-center py-12">
            <p className="text-gray-600 mb-4">Chưa có thực phẩm tự tạo</p>
            <Button>
              <Plus className="size-4 mr-2" />
              Tạo thực phẩm mới
            </Button>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
