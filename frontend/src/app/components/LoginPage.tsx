import React, { useState } from 'react';
import { ArrowLeft } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { toast } from 'sonner';
import api from './lib/api'; // Import axios instance

interface LoginPageProps {
  onLogin: (role?: 'user' | 'admin') => void;
  onBack: () => void;
  onSignup: () => void;
  onForgotPassword: () => void;
}

export default function LoginPage({ onLogin, onBack, onSignup, onForgotPassword }: LoginPageProps) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      // Gọi API thực tế từ auth.py
      const formData = new URLSearchParams();
      formData.append('username', email); // OAuth2PasswordRequestForm dùng username field cho email
      formData.append('password', password);

      // Lưu ý: Nếu backend dùng OAuth2PasswordRequestForm thì endpoint thường là /token hoặc /auth/login trả về token
      // Dựa trên auth.py của bạn: POST /auth/login nhận LoginRequest (JSON body)
      const res = await api.post('/auth/login', {
        email_or_username: email,
        password: password
      });

      // Lưu token vào localStorage
      localStorage.setItem('access_token', res.data.access_token);
      localStorage.setItem('refresh_token', res.data.refresh_token);
      
      toast.success('Đăng nhập thành công!');
      
      // Chuyển role từ response backend
      onLogin(res.data.user.role); 
    } catch (error: any) {
      console.error(error);
      const msg = error.response?.data?.detail || 'Đăng nhập thất bại';
      toast.error(msg);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-pink-50 to-white flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <Button variant="ghost" onClick={onBack} className="mb-4">
          <ArrowLeft className="mr-2 h-4 w-4" /> Quay lại
        </Button>

        <Card>
          <div className="p-6">
            <h2 className="text-2xl font-bold text-center mb-2">Chào mừng trở lại</h2>
            <p className="text-center text-gray-600 mb-6">Đăng nhập để tiếp tục hành trình</p>
          </div>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">Email hoặc Username</Label>
                <Input
                  id="email"
                  type="text"
                  placeholder="your@email.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  disabled={isLoading}
                />
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="password">Mật khẩu</Label>
                  <button
                    type="button"
                    onClick={onForgotPassword}
                    className="text-sm text-pink-600 hover:underline"
                  >
                    Quên mật khẩu?
                  </button>
                </div>
                <Input
                  id="password"
                  type="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  disabled={isLoading}
                />
              </div>

              <Button 
                type="submit" 
                className="w-full bg-gradient-to-r from-pink-500 to-purple-600"
                disabled={isLoading}
              >
                {isLoading ? "Đang xử lý..." : "Đăng nhập"}
              </Button>
            </form>

            <div className="mt-4 text-center text-sm text-gray-600">
              Chưa có tài khoản?{' '}
              <button onClick={onSignup} className="text-pink-600 hover:underline">
                Đăng ký ngay
              </button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}