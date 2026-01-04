import React, { useState } from 'react';
import { ArrowLeft } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { toast } from 'sonner';
import api from './lib/api';

interface ForgotPasswordPageProps {
  onBack: () => void;
}

export default function ForgotPasswordPage({ onBack }: ForgotPasswordPageProps) {
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const frontendUrl = window.location.origin;
      await api.post('/auth/forgot-password', {
        email: email,
        frontend_url: frontendUrl
      });

      toast.success('Nếu email tồn tại, link đặt lại mật khẩu đã được gửi đến email của bạn');
      setIsSubmitted(true);
    } catch (error: any) {
      console.error(error);
      // Backend luôn trả về message generic để bảo mật
      const msg = error.response?.data?.message || error.response?.data?.detail || 'Có lỗi xảy ra';
      toast.success(msg); // Dùng success vì backend trả về generic message
      setIsSubmitted(true);
    } finally {
      setIsLoading(false);
    }
  };

  if (isSubmitted) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-pink-50 to-white flex items-center justify-center p-4">
        <div className="w-full max-w-md">
          <Button variant="ghost" onClick={onBack} className="mb-4">
            <ArrowLeft className="mr-2 h-4 w-4" /> Quay lại
          </Button>

          <Card>
            <div className="p-6">
              <h2 className="text-2xl font-bold text-center mb-2">Kiểm tra email của bạn</h2>
              <p className="text-center text-gray-600 mb-6">
                Nếu email tồn tại trong hệ thống, chúng tôi đã gửi link đặt lại mật khẩu đến <strong>{email}</strong>
              </p>
              <p className="text-center text-sm text-gray-500 mb-6">
                Vui lòng kiểm tra hộp thư đến và làm theo hướng dẫn trong email. Link sẽ hết hạn sau 15 phút.
              </p>
              <Button 
                onClick={onBack}
                className="w-full bg-gradient-to-r from-pink-500 to-purple-600"
              >
                Quay lại đăng nhập
              </Button>
            </div>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-pink-50 to-white flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <Button variant="ghost" onClick={onBack} className="mb-4">
          <ArrowLeft className="mr-2 h-4 w-4" /> Quay lại
        </Button>

        <Card>
          <div className="p-6">
            <h2 className="text-2xl font-bold text-center mb-2">Quên mật khẩu</h2>
            <p className="text-center text-gray-600 mb-6">
              Nhập email của bạn để nhận link đặt lại mật khẩu
            </p>
          </div>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="your@email.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  disabled={isLoading}
                  required
                />
              </div>

              <Button 
                type="submit" 
                className="w-full bg-gradient-to-r from-pink-500 to-purple-600"
                disabled={isLoading}
              >
                {isLoading ? "Đang gửi..." : "Gửi link đặt lại mật khẩu"}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

