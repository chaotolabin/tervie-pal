import React, { useState } from 'react';
import { FoodService } from '../../../../service/food.service';
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
import { X, Plus, Trash2 } from 'lucide-react';

interface CreateCustomFoodModalProps {
  open: boolean;
  onClose: () => void;
  onSuccess?: (foodId: number, foodName: string) => void;
}

interface Nutrient {
  nutrient_name: string;
  unit: string;
  amount_per_100g: string;
}

interface Portion {
  amount: string;
  unit: string;
  grams: string;
}

export default function CreateCustomFoodModal({
  open,
  onClose,
  onSuccess,
}: CreateCustomFoodModalProps) {
  const [submitting, setSubmitting] = useState(false);
  const [name, setName] = useState('');
  const [foodGroup, setFoodGroup] = useState('');
  const [nutrients, setNutrients] = useState<Nutrient[]>([
    { nutrient_name: 'calories', unit: 'kcal', amount_per_100g: '' },
    { nutrient_name: 'protein', unit: 'g', amount_per_100g: '' },
    { nutrient_name: 'carbs', unit: 'g', amount_per_100g: '' },
    { nutrient_name: 'fat', unit: 'g', amount_per_100g: '' },
  ]);
  const [portions, setPortions] = useState<Portion[]>([]);

  const addNutrient = () => {
    setNutrients([...nutrients, { nutrient_name: '', unit: 'g', amount_per_100g: '' }]);
  };

  const removeNutrient = (index: number) => {
    setNutrients(nutrients.filter((_, i) => i !== index));
  };

  const updateNutrient = (index: number, field: keyof Nutrient, value: string) => {
    const updated = [...nutrients];
    updated[index] = { ...updated[index], [field]: value };
    setNutrients(updated);
  };

  const addPortion = () => {
    setPortions([...portions, { amount: '', unit: '', grams: '' }]);
  };

  const removePortion = (index: number) => {
    setPortions(portions.filter((_, i) => i !== index));
  };

  const updatePortion = (index: number, field: keyof Portion, value: string) => {
    const updated = [...portions];
    updated[index] = { ...updated[index], [field]: value };
    setPortions(updated);
  };

  const handleSubmit = async () => {
    // Validation
    if (!name.trim()) {
      toast.error('Vui lòng nhập tên món ăn');
      return;
    }

    const validNutrients = nutrients.filter(
      n => n.nutrient_name.trim() && n.amount_per_100g && parseFloat(n.amount_per_100g) >= 0
    );

    if (validNutrients.length === 0) {
      toast.error('Vui lòng nhập ít nhất 1 chất dinh dưỡng');
      return;
    }

    // Validate portions
    const validPortions = portions.filter(
      p => p.amount && p.unit.trim() && p.grams && parseFloat(p.grams) > 0
    );

    setSubmitting(true);
    try {
      const payload: any = {
        name: name.trim(),
        food_group: foodGroup.trim() || null,
        nutrients: validNutrients.map(n => ({
          nutrient_name: n.nutrient_name.trim().toLowerCase(),
          unit: n.unit.trim(),
          amount_per_100g: parseFloat(n.amount_per_100g),
        })),
      };

      if (validPortions.length > 0) {
        payload.portions = validPortions.map(p => ({
          amount: parseFloat(p.amount),
          unit: p.unit.trim(),
          grams: parseFloat(p.grams),
        }));
      }

      const createdFood = await FoodService.createCustomFood(payload);
      toast.success('Đã tạo món ăn mới!');
      
      if (onSuccess) {
        onSuccess(createdFood.id, createdFood.name);
      }
      
      // Reset form
      setName('');
      setFoodGroup('');
      setNutrients([
        { nutrient_name: 'calories', unit: 'kcal', amount_per_100g: '' },
        { nutrient_name: 'protein', unit: 'g', amount_per_100g: '' },
        { nutrient_name: 'carbs', unit: 'g', amount_per_100g: '' },
        { nutrient_name: 'fat', unit: 'g', amount_per_100g: '' },
      ]);
      setPortions([]);
      onClose();
    } catch (error: any) {
      let errorMsg = 'Không thể tạo món ăn';
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

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center justify-between">
            <span>Tạo món ăn mới</span>
            <Button
              variant="ghost"
              size="icon"
              onClick={onClose}
              className="h-6 w-6"
            >
              <X className="h-4 w-4" />
            </Button>
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-6 mt-4">
          {/* Basic Info */}
          <div className="space-y-4">
            <div>
              <Label htmlFor="name">Tên món ăn *</Label>
              <Input
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Ví dụ: Cơm trắng tự nấu"
              />
            </div>
            <div>
              <Label htmlFor="foodGroup">Nhóm thực phẩm (tùy chọn)</Label>
              <Input
                id="foodGroup"
                value={foodGroup}
                onChange={(e) => setFoodGroup(e.target.value)}
                placeholder="Ví dụ: Grains, Vegetables, Fruits..."
              />
            </div>
          </div>

          {/* Nutrients */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <Label>Chất dinh dưỡng (per 100g) *</Label>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={addNutrient}
              >
                <Plus size={16} className="mr-1" />
                Thêm chất dinh dưỡng
              </Button>
            </div>
            
            <div className="space-y-2 max-h-60 overflow-y-auto">
              {nutrients.map((nutrient, index) => (
                <div key={index} className="flex gap-2 items-end p-2 bg-gray-50 rounded">
                  <div className="flex-1">
                    <Label className="text-xs">Tên chất dinh dưỡng</Label>
                    <Input
                      value={nutrient.nutrient_name}
                      onChange={(e) => updateNutrient(index, 'nutrient_name', e.target.value)}
                      placeholder="calories, protein, carbs..."
                    />
                  </div>
                  <div className="w-24">
                    <Label className="text-xs">Đơn vị</Label>
                    <Input
                      value={nutrient.unit}
                      onChange={(e) => updateNutrient(index, 'unit', e.target.value)}
                      placeholder="kcal, g, mg..."
                    />
                  </div>
                  <div className="w-32">
                    <Label className="text-xs">Lượng (per 100g)</Label>
                    <Input
                      type="number"
                      step="0.1"
                      min="0"
                      value={nutrient.amount_per_100g}
                      onChange={(e) => updateNutrient(index, 'amount_per_100g', e.target.value)}
                      placeholder="0"
                    />
                  </div>
                  {nutrients.length > 1 && (
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      onClick={() => removeNutrient(index)}
                      className="text-red-600"
                    >
                      <Trash2 size={16} />
                    </Button>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Portions */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <Label>Khẩu phần (tùy chọn)</Label>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={addPortion}
              >
                <Plus size={16} className="mr-1" />
                Thêm khẩu phần
              </Button>
            </div>
            
            {portions.length > 0 && (
              <div className="space-y-2 max-h-40 overflow-y-auto">
                {portions.map((portion, index) => (
                  <div key={index} className="flex gap-2 items-end p-2 bg-gray-50 rounded">
                    <div className="w-24">
                      <Label className="text-xs">Số lượng</Label>
                      <Input
                        type="number"
                        step="0.1"
                        min="0"
                        value={portion.amount}
                        onChange={(e) => updatePortion(index, 'amount', e.target.value)}
                        placeholder="1"
                      />
                    </div>
                    <div className="flex-1">
                      <Label className="text-xs">Đơn vị</Label>
                      <Input
                        value={portion.unit}
                        onChange={(e) => updatePortion(index, 'unit', e.target.value)}
                        placeholder="cup, serving, piece..."
                      />
                    </div>
                    <div className="w-32">
                      <Label className="text-xs">Gram tương đương</Label>
                      <Input
                        type="number"
                        step="1"
                        min="1"
                        value={portion.grams}
                        onChange={(e) => updatePortion(index, 'grams', e.target.value)}
                        placeholder="100"
                      />
                    </div>
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      onClick={() => removePortion(index)}
                      className="text-red-600"
                    >
                      <Trash2 size={16} />
                    </Button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Submit Button */}
          <div className="flex gap-2 pt-4">
            <Button
              onClick={handleSubmit}
              disabled={submitting}
              className="flex-1 bg-green-600 hover:bg-green-700"
            >
              {submitting ? 'Đang tạo...' : 'Tạo món ăn'}
            </Button>
            <Button
              variant="outline"
              onClick={onClose}
              disabled={submitting}
            >
              Hủy
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

