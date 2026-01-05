import React, { useState, useEffect } from 'react';
import { Home, Utensils, Activity, TrendingUp, MessageCircle, HelpCircle, User as UserIcon, AudioLines } from 'lucide-react';
import { Button } from './ui/button';
import DashboardHome from './dashboard/DashboardHome';
import StreakNavbarWidget from './dashboard/StreakNavbarWidget';
import NotificationBell from './dashboard/NotificationBell';
import UserDropdown from './dashboard/UserDropdown';
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
  const [sidebarCollapsed, setSidebarCollapsed] = useState(true);
  
  // State dữ liệu thực
  const [userData, setUserData] = useState<UserMeResponse | null>(userDataProp || null);
  const [streakData, setStreakData] = useState<StreakResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Fetch streak data
  const fetchStreakData = async () => {
    try {
      const streakRes = await api.get('/streak');
      setStreakData(streakRes.data);
    } catch (error) {
      console.error("Lỗi tải streak:", error);
    }
  };

  // Fetch dữ liệu khi load Dashboard (chỉ streak, không fetch lại user)
  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        // Chỉ fetch streak nếu chưa có userData từ props
        if (userDataProp) {
          setUserData(userDataProp);
          await fetchStreakData();
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

    // Lắng nghe event refresh streak từ các component log
    const handleRefreshStreak = () => {
      fetchStreakData();
    };

    window.addEventListener('refreshStreak', handleRefreshStreak);
    window.addEventListener('refreshDashboard', handleRefreshStreak);

    return () => {
      window.removeEventListener('refreshStreak', handleRefreshStreak);
      window.removeEventListener('refreshDashboard', handleRefreshStreak);
    };
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
    // { id: 'progress', label: 'Tiến độ', icon: TrendingUp }, // Commented out
    { id: 'blog', label: 'Tervie Blog', icon: MessageCircle },
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
        return <DashboardHome onQuickAdd={() => setShowQuickAdd(true)} fullName={userData?.profile.full_name || userData?.user.username} />;
      
      case 'food':
        return <FoodLoggingPage />;
      
      case 'exercise':
        return <ExerciseLogging />;
      
      // case 'progress':
      //   return <Progress />; // Commented out
      
      case 'blog':
        return <BlogPage />;
      
      case 'help':
        return <HelpSupport />;
        
      default:
        return <div className="p-8 text-center text-gray-500">Tính năng đang phát triển</div>;
    }
  };

  return (
    <div className="flex h-screen bg-gray-100 flex-col">
      {/* Top Header/Navbar */}
      <header className="bg-white border-b border-gray-200 px-6 py-2.5 flex items-center justify-between relative z-10">
        <div className="flex items-center gap-3">
          <AudioLines className="h-5 w-5 text-pink-600" />
          <h1 className="text-lg font-bold bg-gradient-to-r from-pink-600 to-purple-600 bg-clip-text text-transparent">
            Tervie Pal
          </h1>
        </div>
        
        <div className="flex items-center gap-3 relative">
          {/* Streak Widget */}
          <div className="relative z-20">
            <StreakNavbarWidget streakData={streakData} />
          </div>
          
          {/* Notification Bell */}
          <div className="relative z-20">
            <NotificationBell onNavigate={(tab) => setActiveTab(tab as Tab)} />
          </div>
          
          {/* User Dropdown */}
          <div className="relative z-20">
            <UserDropdown
              username={userData?.user.username || 'User'}
              email={userData?.user.email}
              onProfileClick={() => setActiveTab('profile')}
              onLogoutClick={handleLogout}
            />
          </div>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <nav 
          className={`${sidebarCollapsed ? 'w-20' : 'w-50'} bg-white border-r hidden md:block overflow-y-auto transition-all duration-300`}
          onMouseEnter={() => setSidebarCollapsed(false)}
          onMouseLeave={() => setSidebarCollapsed(true)}
        >
          <div className="space-y-1 px-3 pt-6">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as Tab)}
                className={`flex items-center ${sidebarCollapsed ? 'justify-center' : ''} w-full p-3 rounded-lg transition-colors ${
                  activeTab === tab.id 
                    ? 'bg-pink-50 text-pink-600 font-medium' 
                    : 'text-gray-600 hover:bg-gray-50'
                }`}
                title={sidebarCollapsed ? tab.label : ''}
              >
                <tab.icon className={`h-5 w-5 ${!sidebarCollapsed ? 'mr-3' : ''} transition-all duration-300`} />
                <span className={`whitespace-nowrap overflow-hidden transition-all duration-300 ${
                  sidebarCollapsed ? 'w-0 opacity-0' : 'w-auto opacity-100'
                }`}>
                  {tab.label}
                </span>
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

      {/* Quick Add Modal */}
      <QuickAddModal open={showQuickAdd} onClose={() => setShowQuickAdd(false)} />
    </div>
  );
}