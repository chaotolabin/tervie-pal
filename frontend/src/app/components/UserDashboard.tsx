import { useState, useEffect } from 'react';
import { Home, Utensils, Activity, TrendingUp, HelpCircle, User as UserIcon, LogOut } from 'lucide-react';
import { Button } from './ui/button';
import DashboardHome from './dashboard/DashboardHome';
import api from '../lib/api';

// Interface khớp với backend schemas (users.py, streak.py)
interface UserMeResponse {
  user: {
    id: string;
    username: string;
    email: string;
    role: string;
  };
  profile: {
    full_name: string | null;
    gender: string | null;
    height_cm_default: number | null;
  };
}

interface StreakResponse {
  current_streak: number;
  longest_streak: number;
  week: { day: string; status: 'green' | 'yellow' | 'gray' }[];
}

interface UserDashboardProps {
  onLogout: () => void;
}

type Tab = 'home' | 'food' | 'exercise' | 'progress' | 'help' | 'profile';

export default function UserDashboard({ onLogout }: UserDashboardProps) {
  const [activeTab, setActiveTab] = useState<Tab>('home');
  const [showQuickAdd, setShowQuickAdd] = useState(false);
  
  // State dữ liệu thực
  const [userData, setUserData] = useState<UserMeResponse | null>(null);
  const [streakData, setStreakData] = useState<StreakResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Fetch dữ liệu khi load Dashboard
  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        // Gọi song song các API cần thiết
        const [userRes, streakRes] = await Promise.all([
          api.get('/users/me'),
          api.get('/streak')
        ]);

        setUserData(userRes.data);
        setStreakData(streakRes.data);
      } catch (error) {
        console.error("Lỗi tải dữ liệu dashboard:", error);
        // Nếu lỗi 401 (Unauthorized) thì logout
        // onLogout(); 
      } finally {
        setIsLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    onLogout();
  };

  const tabs = [
    { id: 'home', label: 'Tổng quan', icon: Home },
    { id: 'food', label: 'Dinh dưỡng', icon: Utensils },
    { id: 'exercise', label: 'Tập luyện', icon: Activity },
    { id: 'progress', label: 'Tiến độ', icon: TrendingUp },
    { id: 'help', label: 'Trợ giúp', icon: HelpCircle },
    { id: 'profile', label: 'Cá nhân', icon: UserIcon },
  ];

  const renderContent = () => {
    if (isLoading) {
      return <div className="p-8 text-center">Đang tải dữ liệu...</div>;
    }

    switch (activeTab) {
      case 'profile':
        return (
          <div className="p-6 bg-white rounded-lg shadow">
            <h2 className="text-2xl font-bold mb-4">Hồ sơ người dùng</h2>
            <div className="space-y-3">
              <div className="p-4 bg-gray-50 rounded">
                <p className="text-sm text-gray-500">Họ và tên</p>
                <p className="font-medium">{userData?.profile.full_name || 'Chưa cập nhật'}</p>
              </div>
              <div className="p-4 bg-gray-50 rounded">
                <p className="text-sm text-gray-500">Email</p>
                <p className="font-medium">{userData?.user.email}</p>
              </div>
              <div className="p-4 bg-blue-50 rounded border border-blue-100">
                <p className="text-sm text-blue-600">Chuỗi ngày (Streak)</p>
                <p className="text-2xl font-bold text-blue-700">{streakData?.current_streak || 0} Ngày 🔥</p>
              </div>
            </div>
            <Button onClick={handleLogout} variant="destructive" className="mt-6 w-full flex gap-2">
               <LogOut size={16} /> Đăng xuất
            </Button>
          </div>
        );
      
      case 'home':
        // Truyền dữ liệu xuống DashboardHome nếu component đó hỗ trợ props
        return <DashboardHome onQuickAdd={() => setShowQuickAdd(true)} />;
        
      default:
        return <div className="p-8 text-center text-gray-500">Tính năng đang phát triển</div>;
    }
  };

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <nav className="w-64 bg-white border-r hidden md:block">
        <div className="p-6">
          <h1 className="text-2xl font-bold bg-gradient-to-r from-pink-600 to-purple-600 bg-clip-text text-transparent">
            terviepal
          </h1>
          <p className="text-sm text-gray-500 mt-1">Xin chào, {userData?.user.username}</p>
        </div>
        <div className="space-y-1 px-3">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as Tab)}
              className={`flex items-center w-full p-3 rounded-lg transition-colors ${
                activeTab === tab.id 
                  ? 'bg-pink-50 text-pink-600 font-medium' 
                  : 'text-gray-600 hover:bg-gray-50'
              }`}
            >
              <tab.icon className="mr-3 h-5 w-5" />
              {tab.label}
            </button>
          ))}
        </div>
      </nav>

      {/* Main Content */}
      <main className="flex-1 overflow-auto p-8">
        <div className="max-w-5xl mx-auto">
          {renderContent()}
        </div>
      </main>
    </div>
  );
}