import { useState } from 'react';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { toast } from 'sonner';
import api from '../lib/api';

interface SignupPageProps {
  onSignup: (role: string) => void;
  onBack: () => void;
  onLogin: () => void;
}

export default function SignupPage({ onSignup, onBack, onLogin }: SignupPageProps) {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.name || !formData.email || !formData.password) {
      toast.error('Vui lòng điền đầy đủ thông tin');
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      toast.error('Mật khẩu xác nhận không khớp');
      return;
    }

    setIsLoading(true);

    try {
      // Backend yêu cầu RegisterRequest với nhiều trường thông tin sức khỏe.
      // Tạm thời gửi giá trị mặc định để pass qua validation của backend.
      // TODO: Cần thêm các bước nhập liệu (Steps) cho chiều cao, cân nặng, v.v.
      const payload = {
        username: formData.email.split('@')[0], // Tự tạo username từ email
        email: formData.email,
        password: formData.password,
        full_name: formData.name,
        
        // Dữ liệu mặc định (CẦN CẬP NHẬT UI ĐỂ NGƯỜI DÙNG NHẬP)
        gender: "male",
        date_of_birth: "2000-01-01",
        height_cm: 170,
        weight_kg: 60,
        goal_type: "maintain_weight",
        baseline_activity: "sedentary",
        weekly_goal: 0.5
      };

      const res = await api.post('/auth/register', payload);

      // Lưu token
      localStorage.setItem('access_token', res.data.access_token);
      localStorage.setItem('refresh_token', res.data.refresh_token);

      toast.success('Đăng ký tài khoản thành công!');
      onSignup(res.data.user.role);

    } catch (error: any) {
      console.error(error);
      const msg = error.response?.data?.detail || 'Đăng ký thất bại. Kiểm tra lại email.';
      toast.error(msg);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-pink-50 to-white flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <Button variant="ghost" onClick={onBack} className="mb-4">Quay lại</Button>
        <Card>
          <div className="p-6">
             <h2 className="text-2xl font-bold text-center">Tạo tài khoản mới</h2>
          </div>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Họ và tên</Label>
                <Input
                  id="name"
                  placeholder="Nguyễn Văn A"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="your@email.com"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">Mật khẩu</Label>
                <Input
                  id="password"
                  type="password"
                  placeholder="••••••••"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="confirmPassword">Xác nhận mật khẩu</Label>
                <Input
                  id="confirmPassword"
                  type="password"
                  placeholder="••••••••"
                  value={formData.confirmPassword}
                  onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                />
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