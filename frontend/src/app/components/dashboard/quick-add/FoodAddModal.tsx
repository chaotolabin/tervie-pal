import React, { useState, useEffect } from 'react';
import { FoodService } from '../../../../service/food.service';
import { LogService } from '../../../../service/log.service';
import { FoodDetail, FoodPortion } from '../../../../types/food';
import { toast } from 'sonner';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '../../ui/dialog';
import { Button } from '../../ui/button';
import { Input } from '../../ui/input';
import { Label } from '../../ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../../ui/select';
import { Calendar } from 'lucide-react';

interface FoodAddModalProps {
  foodId: number;
  foodName: string;
  open: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

export default function FoodAddModal({
  foodId,
  foodName,
  open,
  onClose,
  onSuccess,
}: FoodAddModalProps) {
  const [foodDetail, setFoodDetail] = useState<FoodDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  
  // Form state
  const [mealType, setMealType] = useState<string>('snacks');
  const [selectedDate, setSelectedDate] = useState<string>(new Date().toISOString().split('T')[0]);
  const [usePortion, setUsePortion] = useState<boolean>(true);
  const [selectedPortionId, setSelectedPortionId] = useState<number | null>(null);
  const [quantity, setQuantity] = useState<string>('1');
  const [grams, setGrams] = useState<string>('100');

  // Load food detail when modal opens
  useEffect(() => {
    if (open && foodId) {
      loadFoodDetail();
    }
  }, [open, foodId]);

  // Auto-detect meal type based on current time and reset date when modal opens
  useEffect(() => {
    if (open) {
      // Reset date to today when modal opens
      setSelectedDate(new Date().toISOString().split('T')[0]);
      
      const currentHour = new Date().getHours();
      if (currentHour >= 5 && currentHour < 10) {
        setMealType('breakfast');
      } else if (currentHour >= 10 && currentHour < 14) {
        setMealType('lunch');
      } else if (currentHour >= 14 && currentHour < 20) {
        setMealType('dinner');
      } else {
        setMealType('snacks');
      }
    }
  }, [open]);

  // Set default portion when food detail loads
  useEffect(() => {
    if (foodDetail?.portions && foodDetail.portions.length > 0) {
      setSelectedPortionId(foodDetail.portions[0].id);
      setUsePortion(true);
    } else {
      setUsePortion(false);
    }
  }, [foodDetail]);

  const loadFoodDetail = async () => {
    setLoading(true);
    try {
      const detail = await FoodService.getDetail(foodId);
      setFoodDetail(detail);
    } catch (error: any) {
      toast.error('Không thể tải thông tin món ăn');
      console.error('Error loading food detail:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (!foodDetail) return;

    setSubmitting(true);
    try {
      // Validate inputs
      if (usePortion && !selectedPortionId) {
        toast.error('Vui lòng chọn khẩu phần');
        return;
      }
      if (!usePortion && (!grams || parseFloat(grams) <= 0)) {
        toast.error('Vui lòng nhập số gram hợp lệ');
        return;
      }
      if (usePortion && (!quantity || parseFloat(quantity) <= 0)) {
        toast.error('Vui lòng nhập số lượng hợp lệ');
        return;
      }

      // Create log item
      const items = usePortion && selectedPortionId ? [
        {
          food_id: foodId,
          portion_id: selectedPortionId,
          quantity: parseFloat(quantity),
        }
      ] : [
        {
          food_id: foodId,
          grams: parseFloat(grams),
        }
      ];

      // Create datetime from selected date with current time
      const selectedDateTime = new Date(selectedDate);
      const now = new Date();
      selectedDateTime.setHours(now.getHours());
      selectedDateTime.setMinutes(now.getMinutes());
      selectedDateTime.setSeconds(now.getSeconds());

      await LogService.addFoodLog({
        logged_at: selectedDateTime.toISOString(),
        meal_type: mealType,
        items: items,
      });

      toast.success('Đã thêm món ăn vào nhật ký!');
      onClose();
      if (onSuccess) onSuccess();
      
      // Trigger refresh dashboard, food logs và streak
      window.dispatchEvent(new CustomEvent('refreshDashboard'));
      window.dispatchEvent(new CustomEvent('refreshFoodLogs'));
      window.dispatchEvent(new CustomEvent('refreshStreak'));
    } catch (error: any) {
      let errorMsg = 'Không thể thêm món ăn';
      if (error.response?.data?.detail) {
        const detail = error.response.data.detail;
        if (typeof detail === 'string') {
          errorMsg = detail;
        } else if (Array.isArray(detail) && detail.length > 0) {
          errorMsg = detail.map((err: any) => err.msg || JSON.stringify(err)).join(', ');
        } else if (typeof detail === 'object') {
          errorMsg = JSON.stringify(detail);
        }
      }
      toast.error(errorMsg);
    } finally {
      setSubmitting(false);
    }
  };

  // Calculate nutrition for selected serving
  const calculateNutrition = () => {
    if (!foodDetail) return null;

    let multiplier = 1;
    if (usePortion && selectedPortionId) {
      const portion = foodDetail.portions.find(p => p.id === selectedPortionId);
      if (portion) {
        const qty = parseFloat(quantity) || 0;
        if (qty <= 0) return null;
        multiplier = (qty * portion.grams) / 100;
      } else {
        return null;
      }
    } else {
      const gramsValue = parseFloat(grams) || 0;
      if (gramsValue <= 0) return null;
      multiplier = gramsValue / 100;
    }

    if (isNaN(multiplier) || multiplier <= 0) return null;

    // Backend normalizes nutrient_name to lowercase
    // Try to find calories from nutrients first, fallback to calories_100g
    const caloriesNutrient = foodDetail.nutrients.find(n => 
      n.nutrient_name.toLowerCase() === 'calories' || 
      n.nutrient_name.toLowerCase() === 'calorie' ||
      n.nutrient_name.toLowerCase() === 'energy'
    );
    const caloriesPer100g = caloriesNutrient?.amount_per_100g || foodDetail.calories_100g || 0;
    const calories = caloriesPer100g * multiplier;
    
    const protein = foodDetail.nutrients.find(n => n.nutrient_name.toLowerCase() === 'protein')?.amount_per_100g || 0;
    const carbs = foodDetail.nutrients.find(n => 
      n.nutrient_name.toLowerCase() === 'carbs' || 
      n.nutrient_name.toLowerCase() === 'carbohydrate' ||
      n.nutrient_name.toLowerCase() === 'carbohydrates'
    )?.amount_per_100g || 0;
    const fat = foodDetail.nutrients.find(n => n.nutrient_name.toLowerCase() === 'fat')?.amount_per_100g || 0;

    return {
      calories: calories.toFixed(1),
      protein: (protein * multiplier).toFixed(1),
      carbs: (carbs * multiplier).toFixed(1),
      fat: (fat * multiplier).toFixed(1),
    };
  };

  const nutrition = calculateNutrition();

  const mealTypeLabels: Record<string, string> = {
    breakfast: 'Bữa sáng',
    lunch: 'Bữa trưa',
    dinner: 'Bữa tối',
    snacks: 'Đồ ăn vặt',
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{foodName}</DialogTitle>
        </DialogHeader>

        {loading ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-pink-600"></div>
          </div>
        ) : foodDetail ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-4">
            {/* Left: Nutrition Info */}
            <div className="space-y-4">
              <h3 className="font-bold text-lg">Thông tin dinh dưỡng</h3>
              
              {nutrition && (
                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="text-center mb-4">
                    <div className="text-3xl font-bold text-pink-600">
                      {nutrition.calories} kcal
                    </div>
                    <div className="text-sm text-gray-500 mt-1">
                      {usePortion && selectedPortionId
                        ? `${quantity} ${foodDetail.portions.find(p => p.id === selectedPortionId)?.unit || ''}`
                        : `${grams} g`}
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Protein:</span>
                      <span className="font-medium text-green-600">{nutrition.protein} g</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Carbs:</span>
                      <span className="font-medium text-blue-600">{nutrition.carbs} g</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Fat:</span>
                      <span className="font-medium text-red-600">{nutrition.fat} g</span>
                    </div>
                  </div>
                </div>
              )}

              {/* Nutrients list */}
              {foodDetail.nutrients && foodDetail.nutrients.length > 0 && (
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm font-medium mb-2">
                    Bảng dinh dưỡng
                  </p>
                  <div className="max-h-40 overflow-y-auto space-y-1">
                    {foodDetail.nutrients.slice(0, 10).map((nutrient, idx) => (
                      <div key={idx} className="flex justify-between text-xs">
                        <span className="text-gray-600">{nutrient.nutrient_name}:</span>
                        <span className="font-medium">
                          {nutrient.amount_per_100g} {nutrient.unit}
                        </span>
                      </div>
                    ))}
                    {foodDetail.nutrients.length > 10 && (
                      <p className="text-xs text-gray-400 mt-2">
                        +{foodDetail.nutrients.length - 10} chất dinh dưỡng khác
                      </p>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Right: Logging Options */}
            <div className="space-y-4">
              <h3 className="font-bold text-lg">Tùy chọn ghi nhận</h3>

              {/* Meal Type */}
              <div className="space-y-2">
                <Label htmlFor="meal-type">Bữa ăn</Label>
                <Select value={mealType} onValueChange={setMealType}>
                  <SelectTrigger id="meal-type">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="breakfast">Bữa sáng</SelectItem>
                    <SelectItem value="lunch">Bữa trưa</SelectItem>
                    <SelectItem value="dinner">Bữa tối</SelectItem>
                    <SelectItem value="snacks">Đồ ăn vặt</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Date Picker */}
              <div className="space-y-2">
                <Label htmlFor="log-date">Ngày ghi nhận</Label>
                <div className="flex items-center gap-2">
                  <Calendar className="size-4 text-gray-500" />
                  <Input
                    id="log-date"
                    type="date"
                    value={selectedDate}
                    onChange={(e) => setSelectedDate(e.target.value)}
                    className="flex-1"
                  />
                </div>
              </div>

              {/* Serving Size */}
              <div className="space-y-2">
                <Label>Khẩu phần</Label>
                <div className="flex gap-2">
                  <Button
                    type="button"
                    variant={usePortion ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setUsePortion(true)}
                    disabled={!foodDetail.portions || foodDetail.portions.length === 0}
                  >
                    Dùng khẩu phần
                  </Button>
                  <Button
                    type="button"
                    variant={!usePortion ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setUsePortion(false)}
                  >
                    Nhập gram
                  </Button>
                </div>

                {usePortion && foodDetail.portions && foodDetail.portions.length > 0 ? (
                  <div className="space-y-2">
                    <Select
                      value={selectedPortionId?.toString() || ''}
                      onValueChange={(value) => setSelectedPortionId(parseInt(value))}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Chọn khẩu phần" />
                      </SelectTrigger>
                      <SelectContent>
                        {foodDetail.portions.map((portion: FoodPortion) => (
                          <SelectItem key={portion.id} value={portion.id.toString()}>
                            {portion.amount} {portion.unit} ({portion.grams} g)
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <div>
                      <Label htmlFor="quantity">Số lượng</Label>
                      <Input
                        id="quantity"
                        type="number"
                        min="0.1"
                        step="0.1"
                        value={quantity}
                        onChange={(e) => setQuantity(e.target.value)}
                        placeholder="1"
                      />
                    </div>
                  </div>
                ) : (
                  <div>
                    <Label htmlFor="grams">Số gram</Label>
                    <Input
                      id="grams"
                      type="number"
                      min="1"
                      step="1"
                      value={grams}
                      onChange={(e) => setGrams(e.target.value)}
                      placeholder="100"
                    />
                  </div>
                )}
              </div>

              {/* Submit Button */}
              <Button
                onClick={handleSubmit}
                disabled={submitting}
                className="w-full bg-green-600 hover:bg-green-700 text-white"
                size="lg"
              >
                {submitting ? 'Đang thêm...' : 'THÊM VÀO NHẬT KÝ'}
              </Button>
            </div>
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            Không thể tải thông tin món ăn
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}

