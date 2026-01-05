import { Activity, TrendingUp, Target, Heart, AudioLines } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';

interface LandingPageProps {
  onLogin: () => void;
  onSignup: () => void;
}

export default function LandingPage({ onLogin, onSignup }: LandingPageProps) {
  return (
    <div className="min-h-screen bg-gradient-to-b from-pink-50 to-white">
      {/* Header */}
      <header className="container mx-auto px-4 py-6 flex justify-between items-center">
        <div className="flex items-center gap-2">
          <AudioLines className="size-8 text-pink-600" />
          <span className="text-2xl font-bold text-gray-900">Tervie Pal</span>
        </div>
        <div className="flex gap-3">
          <Button variant="ghost" onClick={onLogin}>Đăng nhập</Button>
          <Button onClick={onSignup} className="bg-gradient-to-r from-pink-500 to-purple-600">Đăng ký</Button>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20 text-center">
        <h1 className="text-5xl font-bold text-gray-900 mb-6">
          Tervie Pal
        </h1>
        <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
          Ghi nhận calories, theo dõi cân nặng, quản lý chế độ ăn uống và tập luyện của bạn một cách dễ dàng
        </p>
        <div className="flex gap-4 justify-center">
          <Button size="lg" onClick={onSignup} className="text-lg px-8 bg-gradient-to-r from-pink-500 to-purple-600">
            Bắt đầu ngay
          </Button>
          <Button size="lg" variant="outline" onClick={onLogin} className="text-lg px-8">
            Đăng nhập
          </Button>
        </div>
      </section>

      {/* Features */}
      <section className="container mx-auto px-4 py-16">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <CardContent className="pt-6">
              <div className="size-12 bg-pink-100 rounded-full flex items-center justify-center mb-4">
                <Activity className="size-6 text-pink-600" />
              </div>
              <h3 className="font-semibold mb-2">Theo dõi calories</h3>
              <p className="text-sm text-gray-600">
                Ghi nhận chi tiết thực phẩm và calories hàng ngày
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="size-12 bg-cyan-100 rounded-full flex items-center justify-center mb-4">
                <TrendingUp className="size-6 text-cyan-600" />
              </div>
              <h3 className="font-semibold mb-2">Biểu đồ tiến độ</h3>
              <p className="text-sm text-gray-600">
                Xem biểu đồ cân nặng và thống kê chi tiết
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="size-12 bg-purple-100 rounded-full flex items-center justify-center mb-4">
                <Target className="size-6 text-purple-600" />
              </div>
              <h3 className="font-semibold mb-2">Đặt mục tiêu</h3>
              <p className="text-sm text-gray-600">
                Thiết lập và theo dõi mục tiêu sức khỏe của bạn
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="size-12 bg-rose-100 rounded-full flex items-center justify-center mb-4">
                <Heart className="size-6 text-rose-600" />
              </div>
              <h3 className="font-semibold mb-2">Theo dõi tập luyện</h3>
              <p className="text-sm text-gray-600">
                Ghi nhận các bài tập và calories tiêu hao
              </p>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Footer */}
      <footer className="container mx-auto px-4 py-8 text-center text-gray-600 border-t mt-20">
        <p>© 2025 terviepal. Tất cả các quyền được bảo lưu.</p>
      </footer>
    </div>
  );
}