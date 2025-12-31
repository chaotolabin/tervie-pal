import { useState } from 'react';
import { Search, Plus } from 'lucide-react';
import { Input } from '../../ui/input';
import { Button } from '../../ui/button';
import { Label } from '../../ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../ui/select';
import { Card, CardContent } from '../../ui/card';
import { toast } from 'sonner';

interface FoodQuickAddProps {
  onClose: () => void;
}

const popularFoods = [
  { id: 1, name: 'Cơm trắng', calories: 130, protein: 2.7, carbs: 28, fat: 0.3, unit: '100g' },
  { id: 2, name: 'Thịt gà luộc', calories: 165, protein: 31, carbs: 0, fat: 3.6, unit: '100g' },
  { id: 3, name: 'Trứng gà luộc', calories: 155, protein: 13, carbs: 1.1, fat: 11, unit: '1 quả' },
  { id: 4, name: 'Chuối', calories: 89, protein: 1.1, carbs: 23, fat: 0.3, unit: '1 quả' },
  { id: 5, name: 'Sữa tươi', calories: 61, protein: 3.2, carbs: 4.8, fat: 3.3, unit: '100ml' },
];

export default function FoodQuickAdd({ onClose }: FoodQuickAddProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFood, setSelectedFood] = useState<any>(null);
  const [quantity, setQuantity] = useState('1');
  const [mealType, setMealType] = useState('breakfast');

  const filteredFoods = popularFoods.filter(food =>
    food.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleAddFood = () => {
    if (!selectedFood) {
      toast.error('Vui lòng chọn thực phẩm');
      return;
    }

    const multiplier = parseFloat(quantity) || 1;
    const totalCalories = Math.round(selectedFood.calories * multiplier);

    toast.success(`Đã thêm ${selectedFood.name} (${totalCalories} kcal)`);
    onClose();
  };

  return (
    <div className="space-y-4">
      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-gray-400" />
        <Input
          placeholder="Tìm kiếm thực phẩm..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="pl-10"
        />
      </div>

      {/* Food List */}
      <div className="space-y-2 max-h-64 overflow-y-auto">
        {filteredFoods.map((food) => (
          <Card
            key={food.id}
            className={`cursor-pointer transition-colors ${
              selectedFood?.id === food.id ? 'border-green-500 bg-green-50' : ''
            }`}
            onClick={() => setSelectedFood(food)}
          >
            <CardContent className="p-4">
              <div className="flex justify-between items-start">
                <div>
                  <p className="font-semibold">{food.name}</p>
                  <p className="text-sm text-gray-600">{food.unit}</p>
                </div>
                <div className="text-right">
                  <p className="font-bold text-green-600">{food.calories} kcal</p>
                  <p className="text-xs text-gray-500">
                    P: {food.protein}g | C: {food.carbs}g | F: {food.fat}g
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Details Form */}
      {selectedFood && (
        <div className="space-y-4 pt-4 border-t">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="quantity">Số lượng</Label>
              <Input
                id="quantity"
                type="number"
                value={quantity}
                onChange={(e) => setQuantity(e.target.value)}
                min="0.1"
                step="0.1"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="mealType">Bữa ăn</Label>
              <Select value={mealType} onValueChange={setMealType}>
                <SelectTrigger id="mealType">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="breakfast">Sáng</SelectItem>
                  <SelectItem value="lunch">Trưa</SelectItem>
                  <SelectItem value="dinner">Tối</SelectItem>
                  <SelectItem value="snack">Ăn phụ</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="bg-gray-50 p-4 rounded-lg">
            <p className="text-sm text-gray-600 mb-2">Tổng cộng:</p>
            <p className="text-2xl font-bold text-green-600">
              {Math.round(selectedFood.calories * (parseFloat(quantity) || 1))} kcal
            </p>
          </div>

          <div className="flex gap-2">
            <Button onClick={handleAddFood} className="flex-1">
              <Plus className="size-4 mr-2" />
              Thêm vào nhật ký
            </Button>
            <Button variant="outline" onClick={onClose}>
              Hủy
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
