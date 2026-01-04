import React, { useState } from 'react';
import { Scale, Ruler, Plus } from 'lucide-react';
import { Input } from '../../ui/input';
import { Button } from '../../ui/button';
import { Label } from '../../ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../ui/select';
import { Card, CardContent } from '../../ui/card';
import { toast } from 'sonner';

interface BiometricsQuickAddProps {
  onClose: () => void;
}

export default function BiometricsQuickAdd({ onClose }: BiometricsQuickAddProps) {
  const [weight, setWeight] = useState('');
  const [height, setHeight] = useState('');
  const [weightUnit, setWeightUnit] = useState('kg');
  const [heightUnit, setHeightUnit] = useState('cm');

  const calculateBMI = () => {
    if (!weight || !height) return null;
    const weightKg = weightUnit === 'kg' ? parseFloat(weight) : parseFloat(weight) * 0.453592;
    const heightM = heightUnit === 'cm' ? parseFloat(height) / 100 : parseFloat(height) * 0.0254;
    return (weightKg / (heightM * heightM)).toFixed(1);
  };

  const handleSave = async () => {
    if (!weight) {
      toast.error('Vui lòng nhập cân nặng');
      return;
    }

    if (!height) {
      toast.error('Vui lòng nhập chiều cao');
      return;
    }

    try {
      const weightKg = weightUnit === 'kg' ? parseFloat(weight) : parseFloat(weight) * 0.453592;
      const heightCm = heightUnit === 'cm' ? parseFloat(height) : parseFloat(height) * 0.0254 * 100;
      
      if (!heightCm || heightCm <= 0) {
        toast.error('Chiều cao không hợp lệ');
        return;
      }
      
      const { BiometricService } = await import('../../../../service/biometric.service');
      await BiometricService.createLog({
        logged_at: new Date().toISOString(),
        weight_kg: weightKg,
        height_cm: heightCm
      });
      
      toast.success('Đã cập nhật chỉ số cơ thể!');
      onClose();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Không thể lưu chỉ số');
    }
  };

  const bmi = calculateBMI();

  return (
    <div className="space-y-6">
      {/* Weight */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center gap-2 mb-4">
            <Scale className="size-5 text-blue-600" />
            <h3 className="font-semibold">Cân nặng</h3>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="weight">Cân nặng</Label>
              <Input
                id="weight"
                type="number"
                value={weight}
                onChange={(e) => setWeight(e.target.value)}
                placeholder="73.0"
                step="0.1"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="weightUnit">Đơn vị</Label>
              <Select value={weightUnit} onValueChange={setWeightUnit}>
                <SelectTrigger id="weightUnit">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="kg">kg</SelectItem>
                  <SelectItem value="lbs">lbs</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Height */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center gap-2 mb-4">
            <Ruler className="size-5 text-purple-600" />
            <h3 className="font-semibold">Chiều cao</h3>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="height">Chiều cao</Label>
              <Input
                id="height"
                type="number"
                value={height}
                onChange={(e) => setHeight(e.target.value)}
                placeholder="170"
                step="0.1"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="heightUnit">Đơn vị</Label>
              <Select value={heightUnit} onValueChange={setHeightUnit}>
                <SelectTrigger id="heightUnit">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="cm">cm</SelectItem>
                  <SelectItem value="in">inch</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* BMI Calculation */}
      {bmi && (
        <div className="bg-gradient-to-br from-green-500 to-green-600 text-white p-6 rounded-lg">
          <p className="text-sm opacity-90 mb-1">Chỉ số BMI của bạn</p>
          <p className="text-4xl font-bold mb-2">{bmi}</p>
          <p className="text-sm">
            {parseFloat(bmi) < 18.5 && 'Thiếu cân'}
            {parseFloat(bmi) >= 18.5 && parseFloat(bmi) < 25 && 'Bình thường'}
            {parseFloat(bmi) >= 25 && parseFloat(bmi) < 30 && 'Thừa cân'}
            {parseFloat(bmi) >= 30 && 'Béo phì'}
          </p>
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-2">
        <Button onClick={handleSave} className="flex-1">
          <Plus className="size-4 mr-2" />
          Lưu chỉ số
        </Button>
        <Button variant="outline" onClick={onClose}>
          Hủy
        </Button>
      </div>
    </div>
  );
}
