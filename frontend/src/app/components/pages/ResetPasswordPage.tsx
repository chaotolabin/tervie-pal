import React, { useState, useEffect } from 'react';
import { Activity, ArrowLeft, Lock, CheckCircle, AlertCircle } from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { toast } from 'sonner';

interface ResetPasswordPageProps {
  onBack: () => void;
  onSuccess: () => void;
  token?: string; // Token từ URL query parameter
}

export default function ResetPasswordPage({ onBack, onSuccess, token }: ResetPasswordPageProps) {
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isTokenValid, setIsTokenValid] = useState(true);
  const [isCheckingToken, setIsCheckingToken] = useState(true);
  const [isSuccess, setIsSuccess] = useState(false);

  useEffect(() => {
    // Verify token when component mounts
    const verifyToken = async () => {
      setIsCheckingToken(true);
      
      // Simulate token verification API call
      setTimeout(() => {
        // For demo, accept any token that looks valid
        const valid = !!(token && token.length > 10);
        setIsTokenValid(valid);
        setIsCheckingToken(false);
        
        if (!valid) {
          toast.error('Link đặt lại mật khẩu không hợp lệ hoặc đã hết hạn');
        }
      }, 1000);
    };

    verifyToken();
  }, [token]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!password || !confirmPassword) {
      toast.error('Vui lòng điền đầy đủ thông tin');
      return;
    }

    if (password.length < 6) {
      toast.error('Mật khẩu phải có ít nhất 6 ký tự');
      return;
    }

    if (password !== confirmPassword) {
      toast.error('Mật khẩu xác nhận không khớp');
      return;
    }

    setIsLoading(true);
    
    try {
      const { AuthService } = await import('../../../service/auth.sevice');
      if (!token) {
        toast.error('Token không hợp lệ');
        return;
      }
      await AuthService.resetPassword(token, password);
      setIsSuccess(true);
      toast.success('Đặt lại mật khẩu thành công!');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Không thể đặt lại mật khẩu');
    } finally {
      setIsLoading(false);
    }
  };

  // Loading state while checking token
  if (isCheckingToken) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-pink-50 to-white flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardContent className="pt-6 text-center">
            <div className="size-16 bg-pink-100 rounded-full flex items-center justify-center mx-auto mb-4 animate-pulse">
              <Lock className="size-8 text-pink-600" />
            </div>
            <p className="text-gray-600">Đang xác thực link...</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Invalid token state
  if (!isTokenValid) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-pink-50 to-white flex items-center justify-center p-4">
        <div className="w-full max-w-md">
          <Card>
            <CardContent className="pt-6 text-center">
              <div className="size-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <AlertCircle className="size-8 text-red-600" />
              </div>
              
              <h2 className="text-xl font-bold mb-2">Link không hợp lệ</h2>
              <p className="text-gray-600 mb-6">
                Link đặt lại mật khẩu không hợp lệ hoặc đã hết hạn. Vui lòng yêu cầu link mới.
              </p>

              <div className="space-y-3">
                <Button 
                  onClick={onBack}
                  className="w-full bg-gradient-to-r from-pink-500 to-purple-600"
                >
                  Quay lại đăng nhập
                </Button>
                <Button 
                  variant="outline"
                  className="w-full"
                  onClick={onBack}
                >
                  Gửi lại link đặt lại mật khẩu
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  // Success state
  if (isSuccess) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-pink-50 to-white flex items-center justify-center p-4">
        <div className="w-full max-w-md">
          <Card>
            <CardContent className="pt-6 text-center">
              <div className="size-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <CheckCircle className="size-8 text-green-600" />
              </div>
              
              <h2 className="text-xl font-bold mb-2">Đặt lại mật khẩu thành công!</h2>
              <p className="text-gray-600 mb-6">
                Mật khẩu của bạn đã được cập nhật. Bạn có thể đăng nhập bằng mật khẩu mới.
              </p>

              <Button 
                onClick={onSuccess}
                className="w-full bg-gradient-to-r from-pink-500 to-purple-600"
              >
                Đăng nhập ngay
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  // Reset password form
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
                <Lock className="size-8 text-pink-600" />
              </div>
            </div>
            <CardTitle>Đặt lại mật khẩu</CardTitle>
            <CardDescription>
              Nhập mật khẩu mới cho tài khoản của bạn
            </CardDescription>
          </CardHeader>

          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="password">Mật khẩu mới</Label>
                <Input
                  id="password"
                  type="password"
                  placeholder="Ít nhất 6 ký tự"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="confirmPassword">Xác nhận mật khẩu</Label>
                <Input
                  id="confirmPassword"
                  type="password"
                  placeholder="Nhập lại mật khẩu mới"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                />
              </div>

              {/* Password strength indicator */}
              {password && (
                <div className="space-y-2">
                  <div className="flex gap-2">
                    <div className={`h-1 flex-1 rounded ${password.length >= 6 ? 'bg-green-500' : 'bg-gray-200'}`} />
                    <div className={`h-1 flex-1 rounded ${password.length >= 8 ? 'bg-green-500' : 'bg-gray-200'}`} />
                    <div className={`h-1 flex-1 rounded ${password.length >= 10 && /[A-Z]/.test(password) && /[0-9]/.test(password) ? 'bg-green-500' : 'bg-gray-200'}`} />
                  </div>
                  <p className="text-xs text-gray-600">
                    {password.length < 6 ? 'Mật khẩu yếu' : password.length < 8 ? 'Mật khẩu trung bình' : 'Mật khẩu mạnh'}
                  </p>
                </div>
              )}

              <Button 
                type="submit" 
                className="w-full bg-gradient-to-r from-pink-500 to-purple-600"
                disabled={isLoading}
              >
                {isLoading ? 'Đang xử lý...' : 'Đặt lại mật khẩu'}
              </Button>
            </form>

            <div className="mt-6 p-4 bg-blue-50 rounded-lg text-sm">
              <p className="font-semibold mb-2">Yêu cầu mật khẩu:</p>
              <ul className="space-y-1 text-gray-700 text-xs">
                <li className={password.length >= 6 ? 'text-green-600' : ''}>
                  • Ít nhất 6 ký tự
                </li>
                <li className={password.length >= 8 ? 'text-green-600' : ''}>
                  • Nên có ít nhất 8 ký tự
                </li>
                <li className={/[A-Z]/.test(password) ? 'text-green-600' : ''}>
                  • Nên có chữ hoa
                </li>
                <li className={/[0-9]/.test(password) ? 'text-green-600' : ''}>
                  • Nên có số
                </li>
              </ul>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
