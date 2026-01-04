import { useState } from 'react';
import { Activity, ArrowLeft } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { toast } from 'sonner';

interface LoginPageProps {
  onLogin: (role?: 'user' | 'admin') => void;
  onBack: () => void;
  onSignup: () => void;
}

export default function LoginPage({ onLogin, onBack, onSignup }: LoginPageProps) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Demo login logic
    if (email === 'admin@healthtrack.com' && password === 'admin123') {
      toast.success('Đăng nhập Admin thành công!');
      onLogin('admin');
    } else if (email && password) {
      toast.success('Đăng nhập thành công!');
      onLogin('user');
    } else {
      toast.error('Vui lòng nhập email và mật khẩu');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-green-50 to-white flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <Button variant="ghost" onClick={onBack} className="mb-4">
          <ArrowLeft className="size-4 mr-2" />
          Quay lại
        </Button>

        <Card>
          <CardHeader className="text-center">
            <div className="flex justify-center mb-4">
              <div className="size-16 bg-green-100 rounded-full flex items-center justify-center">
                <Activity className="size-8 text-green-600" />
              </div>
            </div>
            <CardTitle>Đăng nhập</CardTitle>
            <CardDescription>
              Nhập thông tin để truy cập tài khoản của bạn
            </CardDescription>
          </CardHeader>

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
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">Mật khẩu</Label>
                <Input
                  id="password"
                  type="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>

              <Button type="submit" className="w-full">
                Đăng nhập
              </Button>
            </form>

            <div className="mt-4 text-center text-sm text-gray-600">
              Chưa có tài khoản?{' '}
              <button onClick={onSignup} className="text-green-600 hover:underline">
                Đăng ký ngay
              </button>
            </div>

            <div className="mt-6 p-4 bg-blue-50 rounded-lg text-sm">
              <p className="font-semibold mb-2">Demo accounts:</p>
              <p>👤 User: any email + password</p>
              <p>👨‍💼 Admin: admin@healthtrack.com / admin123</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
