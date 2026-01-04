import React, { useState, useEffect } from 'react';
import { Home, Utensils, Activity, TrendingUp, MessageCircle, HelpCircle, User as UserIcon, LogOut } from 'lucide-react';
import { Button } from './ui/button';
import DashboardHome from './dashboard/DashboardHome';
import FoodLoggingPage from './dashboard/FoodLoggingPage';
import ExerciseLogging from './dashboard/ExerciseLogging';
import Progress from './dashboard/Progress';
import BlogPage from './pages/BlogPage';
import HelpSupport from './dashboard/HelpSupport';
import QuickAddModal from './dashboard/QuickAddModal';
import UserProfileDashboard from './pages/UserProfileDashboard';
import api from './lib/api';

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
  userData?: UserMeResponse | null;
}

type Tab = 'home' | 'food' | 'exercise' | 'progress' | 'blog' | 'help' | 'profile';

export default function UserDashboard({ onLogout, userData: userDataProp }: UserDashboardProps) {
  const [activeTab, setActiveTab] = useState<Tab>('home');
  const [showQuickAdd, setShowQuickAdd] = useState(false);
  
  // State dữ liệu thực
  const [userData, setUserData] = useState<UserMeResponse | null>(userDataProp || null);
  const [streakData, setStreakData] = useState<StreakResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Fetch dữ liệu khi load Dashboard (chỉ streak, không fetch lại user)
  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        // Chỉ fetch streak nếu chưa có userData từ props
        if (userDataProp) {
          setUserData(userDataProp);
          const streakRes = await api.get('/streak');
          setStreakData(streakRes.data);
        } else {
          // Fallback: nếu không có userData từ props, fetch cả hai
          const [userRes, streakRes] = await Promise.all([
            api.get('/users/me'),
            api.get('/streak')
          ]);
          setUserData(userRes.data);
          setStreakData(streakRes.data);
        }
      } catch (error) {
        console.error("Lỗi tải dữ liệu dashboard:", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchDashboardData();
  }, [userDataProp]);

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
    { id: 'blog', label: 'Blog', icon: MessageCircle },
    { id: 'help', label: 'Trợ giúp', icon: HelpCircle },
    { id: 'profile', label: 'Cá nhân', icon: UserIcon },
  ];

  const renderContent = () => {
    if (isLoading) {
      return <div className="p-8 text-center">Đang tải dữ liệu...</div>;
    }

    switch (activeTab) {
      case 'profile':
        return <UserProfileDashboard onLogout={handleLogout} />;
      
      case 'home':
        // Truyền dữ liệu xuống DashboardHome nếu component đó hỗ trợ props
        return <DashboardHome onQuickAdd={() => setShowQuickAdd(true)} />;
      
      case 'food':
        return <FoodLoggingPage />;
      
      case 'exercise':
        return <ExerciseLogging />;
      
      case 'progress':
        return <Progress />;
      
      case 'blog':
        return <BlogPage />;
      
      case 'help':
        return <HelpSupport />;
        
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

      {/* Quick Add Modal */}
      <QuickAddModal open={showQuickAdd} onClose={() => setShowQuickAdd(false)} />
    </div>
  );
}