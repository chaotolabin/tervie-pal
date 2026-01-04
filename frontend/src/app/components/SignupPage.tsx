import React, { useState } from 'react';
import { ArrowLeft } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';
import { Input } from './ui/input';
import { Label } from './ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from './ui/select';
import { toast } from 'sonner';
import api from './lib/api';

interface SignupPageProps {
  onSignup: (role: string) => void;
  onBack: () => void;
  onLogin: () => void;
}

export default function SignupPage({ onSignup, onBack, onLogin }: SignupPageProps) {
  const [formData, setFormData] = useState({
    // Basic auth
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    
    // Profile
    full_name: '',
    gender: 'male' as 'male' | 'female',
    date_of_birth: '',
    
    // Biometric
    height_cm: '',
    weight_kg: '',
    goal_weight_kg: '',
    
    // Goals
    goal_type: 'maintain_weight' as 'lose_weight' | 'gain_weight' | 'maintain_weight' | 'build_muscle' | 'improve_health',
    baseline_activity: 'sedentary' as 'sedentary' | 'low_active' | 'moderately_active' | 'very_active' | 'extremely_active',
    weekly_goal: '0.5',
    weekly_exercise_min: '',
  });
  
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (field: string, value: string) => {
    setFormData({ ...formData, [field]: value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validation
    if (!formData.username || !formData.email || !formData.password) {
      toast.error('Vui lòng điền đầy đủ thông tin đăng nhập');
      return;
    }

    if (formData.username.length < 3 || formData.username.length > 32) {
      toast.error('Tên đăng nhập phải từ 3-32 ký tự');
      return;
    }

    if (formData.password.length < 8) {
      toast.error('Mật khẩu phải có ít nhất 8 ký tự');
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      toast.error('Mật khẩu xác nhận không khớp');
      return;
    }

    if (!formData.full_name) {
      toast.error('Vui lòng nhập họ và tên');
      return;
    }

    if (!formData.date_of_birth) {
      toast.error('Vui lòng chọn ngày sinh');
      return;
    }

    if (!formData.height_cm || parseFloat(formData.height_cm) <= 0) {
      toast.error('Vui lòng nhập chiều cao hợp lệ');
      return;
    }

    if (!formData.weight_kg || parseFloat(formData.weight_kg) <= 0) {
      toast.error('Vui lòng nhập cân nặng hợp lệ');
      return;
    }

    // Validate goal_weight_kg nếu cần
    if ((formData.goal_type === 'lose_weight' || formData.goal_type === 'gain_weight') && !formData.goal_weight_kg) {
      toast.error('Vui lòng nhập cân nặng mục tiêu');
      return;
    }

    const weeklyGoal = parseFloat(formData.weekly_goal);
    if (isNaN(weeklyGoal) || weeklyGoal <= 0 || weeklyGoal > 1.0) {
      toast.error('Mục tiêu tuần phải từ 0.25 đến 1.0 kg/tuần');
      return;
    }

    setIsLoading(true);

    try {
      const payload: any = {
        username: formData.username,
        email: formData.email,
        password: formData.password,
        full_name: formData.full_name,
        gender: formData.gender,
        date_of_birth: formData.date_of_birth,
        height_cm: parseFloat(formData.height_cm),
        weight_kg: parseFloat(formData.weight_kg),
        goal_type: formData.goal_type,
        baseline_activity: formData.baseline_activity,
        weekly_goal: weeklyGoal,
      };

      // Optional fields
      if (formData.goal_weight_kg) {
        payload.goal_weight_kg = parseFloat(formData.goal_weight_kg);
      }

      if (formData.weekly_exercise_min) {
        const exerciseMin = parseInt(formData.weekly_exercise_min);
        if (exerciseMin >= 0) {
          payload.weekly_exercise_min = exerciseMin;
        }
      }

      const res = await api.post('/auth/register', payload);

      // Lưu token
      localStorage.setItem('access_token', res.data.access_token);
      localStorage.setItem('refresh_token', res.data.refresh_token);

      toast.success('Đăng ký tài khoản thành công!');
      onSignup(res.data.user.role);

    } catch (error: any) {
      console.error(error);
      const msg = error.response?.data?.detail || 'Đăng ký thất bại. Vui lòng thử lại.';
      toast.error(msg);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-pink-50 to-white flex items-center justify-center p-4 py-8">
      <div className="w-full max-w-2xl">
        <Button variant="ghost" onClick={onBack} className="mb-4">
          <ArrowLeft className="mr-2 h-4 w-4" /> Quay lại
        </Button>
        
        <Card>
          <div className="p-6">
            <h2 className="text-2xl font-bold text-center mb-2">Tạo tài khoản mới</h2>
            <p className="text-center text-gray-600 mb-6">Điền thông tin để bắt đầu hành trình sức khỏe của bạn</p>
          </div>
          
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Basic Auth Section */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-800 border-b pb-2">Thông tin đăng nhập</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="username">Tên đăng nhập *</Label>
                    <Input
                      id="username"
                      placeholder="username"
                      value={formData.username}
                      onChange={(e) => handleChange('username', e.target.value)}
                      disabled={isLoading}
                      required
                      minLength={3}
                      maxLength={32}
                    />
                    <p className="text-xs text-gray-500">3-32 ký tự</p>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="email">Email *</Label>
                    <Input
                      id="email"
                      type="email"
                      placeholder="your@email.com"
                      value={formData.email}
                      onChange={(e) => handleChange('email', e.target.value)}
                      disabled={isLoading}
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="password">Mật khẩu *</Label>
                    <Input
                      id="password"
                      type="password"
                      placeholder="••••••••"
                      value={formData.password}
                      onChange={(e) => handleChange('password', e.target.value)}
                      disabled={isLoading}
                      required
                      minLength={8}
                    />
                    <p className="text-xs text-gray-500">Tối thiểu 8 ký tự</p>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="confirmPassword">Xác nhận mật khẩu *</Label>
                    <Input
                      id="confirmPassword"
                      type="password"
                      placeholder="••••••••"
                      value={formData.confirmPassword}
                      onChange={(e) => handleChange('confirmPassword', e.target.value)}
                      disabled={isLoading}
                      required
                      minLength={8}
                    />
                  </div>
                </div>
              </div>

              {/* Profile Section */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-800 border-b pb-2">Thông tin cá nhân</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="space-y-2 md:col-span-3">
                    <Label htmlFor="full_name">Họ và tên *</Label>
                    <Input
                      id="full_name"
                      placeholder="Nguyễn Văn A"
                      value={formData.full_name}
                      onChange={(e) => handleChange('full_name', e.target.value)}
                      disabled={isLoading}
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="gender">Giới tính *</Label>
                    <Select
                      value={formData.gender}
                      onValueChange={(value) => handleChange('gender', value)}
                      disabled={isLoading}
                      required
                    >
                      <SelectTrigger id="gender">
                        <SelectValue placeholder="Chọn giới tính" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="male">Nam</SelectItem>
                        <SelectItem value="female">Nữ</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2 md:col-span-2">
                    <Label htmlFor="date_of_birth">Ngày sinh *</Label>
                    <Input
                      id="date_of_birth"
                      type="date"
                      value={formData.date_of_birth}
                      onChange={(e) => handleChange('date_of_birth', e.target.value)}
                      disabled={isLoading}
                      required
                      max={new Date().toISOString().split('T')[0]}
                    />
                  </div>
                </div>
              </div>

              {/* Biometric Section */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-800 border-b pb-2">Chỉ số cơ thể</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="height_cm">Chiều cao (cm) *</Label>
                    <Input
                      id="height_cm"
                      type="number"
                      step="0.01"
                      placeholder="170.00"
                      value={formData.height_cm}
                      onChange={(e) => handleChange('height_cm', e.target.value)}
                      disabled={isLoading}
                      required
                      min="1"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="weight_kg">Cân nặng hiện tại (kg) *</Label>
                    <Input
                      id="weight_kg"
                      type="number"
                      step="0.01"
                      placeholder="60.00"
                      value={formData.weight_kg}
                      onChange={(e) => handleChange('weight_kg', e.target.value)}
                      disabled={isLoading}
                      required
                      min="1"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="goal_weight_kg">
                      Cân nặng mục tiêu (kg)
                      {(formData.goal_type === 'lose_weight' || formData.goal_type === 'gain_weight') && ' *'}
                    </Label>
                    <Input
                      id="goal_weight_kg"
                      type="number"
                      step="0.01"
                      placeholder="55.00"
                      value={formData.goal_weight_kg}
                      onChange={(e) => handleChange('goal_weight_kg', e.target.value)}
                      disabled={isLoading}
                      required={formData.goal_type === 'lose_weight' || formData.goal_type === 'gain_weight'}
                      min="1"
                    />
                  </div>
                </div>
              </div>

              {/* Goals Section */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-800 border-b pb-2">Mục tiêu sức khỏe</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="goal_type">Loại mục tiêu *</Label>
                    <Select
                      value={formData.goal_type}
                      onValueChange={(value) => handleChange('goal_type', value)}
                      disabled={isLoading}
                      required
                    >
                      <SelectTrigger id="goal_type">
                        <SelectValue placeholder="Chọn mục tiêu" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="lose_weight">Giảm cân</SelectItem>
                        <SelectItem value="gain_weight">Tăng cân</SelectItem>
                        <SelectItem value="maintain_weight">Duy trì cân nặng</SelectItem>
                        <SelectItem value="build_muscle">Xây dựng cơ bắp</SelectItem>
                        <SelectItem value="improve_health">Cải thiện sức khỏe</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="baseline_activity">Mức độ hoạt động *</Label>
                    <Select
                      value={formData.baseline_activity}
                      onValueChange={(value) => handleChange('baseline_activity', value)}
                      disabled={isLoading}
                      required
                    >
                      <SelectTrigger id="baseline_activity">
                        <SelectValue placeholder="Chọn mức độ hoạt động" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="sedentary">Ít vận động (ngồi nhiều)</SelectItem>
                        <SelectItem value="low_active">Vận động nhẹ (1-3 lần/tuần)</SelectItem>
                        <SelectItem value="moderately_active">Vận động vừa (3-5 lần/tuần)</SelectItem>
                        <SelectItem value="very_active">Vận động nhiều (6-7 lần/tuần)</SelectItem>
                        <SelectItem value="extremely_active">Vận động rất nhiều (2 lần/ngày)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="weekly_goal">Mục tiêu tuần (kg/tuần) *</Label>
                    <Select
                      value={formData.weekly_goal}
                      onValueChange={(value) => handleChange('weekly_goal', value)}
                      disabled={isLoading}
                      required
                    >
                      <SelectTrigger id="weekly_goal">
                        <SelectValue placeholder="Chọn mục tiêu tuần" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="0.25">0.25 kg/tuần</SelectItem>
                        <SelectItem value="0.5">0.5 kg/tuần</SelectItem>
                        <SelectItem value="0.75">0.75 kg/tuần</SelectItem>
                        <SelectItem value="1.0">1.0 kg/tuần</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="weekly_exercise_min">Phút tập luyện/tuần (tùy chọn)</Label>
                    <Input
                      id="weekly_exercise_min"
                      type="number"
                      placeholder="150"
                      value={formData.weekly_exercise_min}
                      onChange={(e) => handleChange('weekly_exercise_min', e.target.value)}
                      disabled={isLoading}
                      min="0"
                    />
                    <p className="text-xs text-gray-500">Ví dụ: 150 phút/tuần</p>
                  </div>
                </div>
              </div>

              <Button 
                type="submit" 
                disabled={isLoading}
                className="w-full bg-gradient-to-r from-pink-500 to-purple-600"
              >
                {isLoading ? "Đang đăng ký..." : "Đăng ký"}
              </Button>
            </form>
            
            <div className="mt-4 text-center text-sm text-gray-600">
              Đã có tài khoản?{' '}
              <button onClick={onLogin} className="text-pink-600 hover:underline">
                Đăng nhập ngay
              </button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
