import { useState } from 'react';
import { User, Lock, Bell, Globe, Target, Database, Shield } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Switch } from '../components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { toast } from 'sonner';

export default function SettingsPage() {
  const [settings, setSettings] = useState({
    // Goals
    dailyCalories: 2000,
    goalType: 'lose',
    weeklyWeightGoal: 0.5,
    
    // Notifications
    mealReminders: true,
    exerciseReminders: true,
    streakReminders: true,
    
    // Security
    twoFactorEnabled: false,
    
    // Preferences
    language: 'vi',
    units: 'metric',
    theme: 'light'
  });

  const handleSave = () => {
    toast.success('Đã lưu cài đặt!');
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Cài đặt</h2>
        <p className="text-gray-600">Quản lý tài khoản và tùy chỉnh ứng dụng</p>
      </div>

      <Tabs defaultValue="goals" className="w-full">
        <TabsList className="grid w-full grid-cols-3 lg:grid-cols-6">
          <TabsTrigger value="goals">
            <Target className="size-4 mr-2" />
            Mục tiêu
          </TabsTrigger>
          <TabsTrigger value="account">
            <User className="size-4 mr-2" />
            Tài khoản
          </TabsTrigger>
          <TabsTrigger value="security">
            <Lock className="size-4 mr-2" />
            Bảo mật
          </TabsTrigger>
          <TabsTrigger value="notifications">
            <Bell className="size-4 mr-2" />
            Thông báo
          </TabsTrigger>
          <TabsTrigger value="preferences">
            <Globe className="size-4 mr-2" />
            Tùy chỉnh
          </TabsTrigger>
          <TabsTrigger value="data">
            <Database className="size-4 mr-2" />
            Dữ liệu
          </TabsTrigger>
        </TabsList>

        {/* Goals Tab */}
        <TabsContent value="goals" className="space-y-6 mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Mục tiêu calories</CardTitle>
              <CardDescription>Đặt mục tiêu calories hàng ngày của bạn</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="dailyCalories">Calories mục tiêu (kcal/ngày)</Label>
                <Input
                  id="dailyCalories"
                  type="number"
                  value={settings.dailyCalories}
                  onChange={(e) => setSettings({ ...settings, dailyCalories: parseInt(e.target.value) })}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="goalType">Loại mục tiêu</Label>
                <Select value={settings.goalType} onValueChange={(value) => setSettings({ ...settings, goalType: value })}>
                  <SelectTrigger id="goalType">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="lose">Giảm cân</SelectItem>
                    <SelectItem value="maintain">Duy trì</SelectItem>
                    <SelectItem value="gain">Tăng cân</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="weeklyGoal">Thay đổi cân nặng mục tiêu (kg/tuần)</Label>
                <Select 
                  value={settings.weeklyWeightGoal.toString()} 
                  onValueChange={(value) => setSettings({ ...settings, weeklyWeightGoal: parseFloat(value) })}
                >
                  <SelectTrigger id="weeklyGoal">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="0.25">0.25 kg/tuần (Chậm)</SelectItem>
                    <SelectItem value="0.5">0.5 kg/tuần (Vừa phải)</SelectItem>
                    <SelectItem value="0.75">0.75 kg/tuần (Nhanh)</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <Button onClick={handleSave} className="bg-gradient-to-r from-pink-500 to-purple-600">
                Lưu mục tiêu
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Account Tab */}
        <TabsContent value="account" className="space-y-6 mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Thông tin tài khoản</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Họ và tên</Label>
                <Input id="name" defaultValue="Nguyễn Văn A" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input id="email" type="email" defaultValue="nguyenvana@email.com" disabled />
              </div>
              <Button onClick={handleSave} className="bg-gradient-to-r from-pink-500 to-purple-600">
                Cập nhật thông tin
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Đổi mật khẩu</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="currentPassword">Mật khẩu hiện tại</Label>
                <Input id="currentPassword" type="password" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="newPassword">Mật khẩu mới</Label>
                <Input id="newPassword" type="password" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="confirmPassword">Xác nhận mật khẩu mới</Label>
                <Input id="confirmPassword" type="password" />
              </div>
              <Button variant="outline">Đổi mật khẩu</Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Security Tab */}
        <TabsContent value="security" className="space-y-6 mt-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="size-5 text-pink-600" />
                Xác thực hai yếu tố (2FA)
              </CardTitle>
              <CardDescription>
                Tăng cường bảo mật tài khoản với xác thực hai yếu tố
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-semibold">Bật 2FA</p>
                  <p className="text-sm text-gray-600">Yêu cầu mã xác thực khi đăng nhập</p>
                </div>
                <Switch
                  checked={settings.twoFactorEnabled}
                  onCheckedChange={(checked) => setSettings({ ...settings, twoFactorEnabled: checked })}
                />
              </div>
              {settings.twoFactorEnabled && (
                <div className="p-4 bg-blue-50 rounded-lg">
                  <p className="text-sm text-blue-700">2FA đã được kích hoạt. Bạn sẽ cần mã xác thực khi đăng nhập.</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Notifications Tab */}
        <TabsContent value="notifications" className="space-y-6 mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Thông báo</CardTitle>
              <CardDescription>Quản lý các loại thông báo bạn muốn nhận</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-semibold">Nhắc nhở bữa ăn</p>
                  <p className="text-sm text-gray-600">Nhận thông báo nhắc nhở ghi nhận bữa ăn</p>
                </div>
                <Switch
                  checked={settings.mealReminders}
                  onCheckedChange={(checked) => setSettings({ ...settings, mealReminders: checked })}
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <p className="font-semibold">Nhắc nhở tập luyện</p>
                  <p className="text-sm text-gray-600">Nhận thông báo nhắc nhở về lịch tập</p>
                </div>
                <Switch
                  checked={settings.exerciseReminders}
                  onCheckedChange={(checked) => setSettings({ ...settings, exerciseReminders: checked })}
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <p className="font-semibold">Nhắc nhở Streak</p>
                  <p className="text-sm text-gray-600">Nhận thông báo để duy trì streak hàng ngày</p>
                </div>
                <Switch
                  checked={settings.streakReminders}
                  onCheckedChange={(checked) => setSettings({ ...settings, streakReminders: checked })}
                />
              </div>

              <Button onClick={handleSave} className="bg-gradient-to-r from-pink-500 to-purple-600">
                Lưu cài đặt
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Preferences Tab */}
        <TabsContent value="preferences" className="space-y-6 mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Tùy chỉnh</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="language">Ngôn ngữ</Label>
                <Select value={settings.language} onValueChange={(value) => setSettings({ ...settings, language: value })}>
                  <SelectTrigger id="language">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="vi">Tiếng Việt</SelectItem>
                    <SelectItem value="en">English</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="units">Đơn vị đo lường</Label>
                <Select value={settings.units} onValueChange={(value) => setSettings({ ...settings, units: value })}>
                  <SelectTrigger id="units">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="metric">Metric (kg, cm)</SelectItem>
                    <SelectItem value="imperial">Imperial (lbs, inch)</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <Button onClick={handleSave} className="bg-gradient-to-r from-pink-500 to-purple-600">
                Lưu cài đặt
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Data Tab */}
        <TabsContent value="data" className="space-y-6 mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Quản lý dữ liệu</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h4 className="font-semibold mb-2">Xuất dữ liệu</h4>
                <p className="text-sm text-gray-600 mb-4">Tải xuống toàn bộ dữ liệu của bạn dưới dạng CSV</p>
                <Button variant="outline">Xuất dữ liệu</Button>
              </div>

              <div className="pt-4 border-t">
                <h4 className="font-semibold mb-2 text-red-600">Xóa tài khoản</h4>
                <p className="text-sm text-gray-600 mb-4">
                  Xóa vĩnh viễn tài khoản và toàn bộ dữ liệu của bạn. Hành động này không thể hoàn tác.
                </p>
                <Button variant="destructive">Xóa tài khoản</Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
