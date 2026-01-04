import React, { useState } from 'react';
import { Activity, ArrowLeft, Mail, CheckCircle } from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { toast } from 'sonner';

interface ForgotPasswordPageProps {
  onBack: () => void;
}

export default function ForgotPasswordPage({ onBack }: ForgotPasswordPageProps) {
  const [email, setEmail] = useState('');
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!email) {
      toast.error('Vui lòng nhập email');
      return;
    }

    setIsLoading(true);
    
    // Simulate API call
    setTimeout(() => {
      setIsLoading(false);
      setIsSubmitted(true);
      toast.success('Email đã được gửi!');
    }, 1500);
  };

  if (isSubmitted) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-pink-50 to-white flex items-center justify-center p-4">
        <div className="w-full max-w-md">
          <Button variant="ghost" onClick={onBack} className="mb-4">
            <ArrowLeft className="size-4 mr-2" />
            Quay lại đăng nhập
          </Button>

          <Card>
            <CardContent className="pt-6 text-center">
              <div className="size-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <CheckCircle className="size-8 text-green-600" />
              </div>
              
              <h2 className="text-xl font-bold mb-2">Kiểm tra email của bạn</h2>
              <p className="text-gray-600 mb-6">
                Chúng tôi đã gửi link đặt lại mật khẩu đến email:
              </p>
              <p className="font-semibold text-pink-600 mb-6">{email}</p>
              
              <div className="p-4 bg-blue-50 rounded-lg text-sm text-left mb-6">
                <p className="font-semibold mb-2">Lưu ý:</p>
                <ul className="space-y-1 text-gray-700">
                  <li>• Link sẽ hết hạn sau 24 giờ</li>
                  <li>• Kiểm tra cả thư mục spam nếu không thấy email</li>
                  <li>• Link chỉ có thể sử dụng một lần</li>
                </ul>
              </div>

              <Button 
                onClick={onBack} 
                className="w-full bg-gradient-to-r from-pink-500 to-purple-600"
              >
                Quay lại đăng nhập
              </Button>

              <button
                onClick={() => {
                  setIsSubmitted(false);
                  setEmail('');
                }}
                className="text-sm text-pink-600 hover:underline mt-4"
              >
                Gửi lại email
              </button>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-pink-50 to-white flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <Button variant="ghost" onClick={onBack} className="mb-4">
          <ArrowLeft className="size-4 mr-2" />
          Quay lại
        </Button>

        <Card>
          <CardHeader className="text-center">
            <div className="flex justify-center mb-4">
              <div className="size-16 bg-pink-100 rounded-full flex items-center justify-center">
                <Activity className="size-8 text-pink-600" />
              </div>
            </div>
            <CardTitle>Quên mật khẩu?</CardTitle>
            <CardDescription>
              Nhập email của bạn và chúng tôi sẽ gửi link để đặt lại mật khẩu
            </CardDescription>
          </CardHeader>

          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-gray-400" />
                  <Input
                    id="email"
                    type="email"
                    placeholder="your@email.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>

              <Button 
                type="submit" 
                className="w-full bg-gradient-to-r from-pink-500 to-purple-600"
                disabled={isLoading}
              >
                {isLoading ? 'Đang gửi...' : 'Gửi link đặt lại mật khẩu'}
              </Button>
            </form>

            <div className="mt-6 p-4 bg-gray-50 rounded-lg text-sm">
              <p className="text-gray-600">
                <strong>Demo:</strong> Nhập bất kỳ email nào để xem flow reset mật khẩu
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
