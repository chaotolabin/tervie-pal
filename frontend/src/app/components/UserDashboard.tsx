import { useState } from 'react';
import { Home, Utensils, Activity, TrendingUp, HelpCircle, LogOut, Plus } from 'lucide-react';
import { Button } from './ui/button';
import DashboardHome from './dashboard/DashboardHome';
import FoodLogging from './dashboard/FoodLogging';
import ExerciseLogging from './dashboard/ExerciseLogging';
import Progress from './dashboard/Progress';
import HelpSupport from './dashboard/HelpSupport';
import QuickAddModal from './dashboard/QuickAddModal';

interface UserDashboardProps {
  onLogout: () => void;
}

type Tab = 'home' | 'food' | 'exercise' | 'progress' | 'help';

export default function UserDashboard({ onLogout }: UserDashboardProps) {
  const [activeTab, setActiveTab] = useState<Tab>('home');
  const [showQuickAdd, setShowQuickAdd] = useState(false);

  const tabs = [
    { id: 'home', label: 'Trang chủ', icon: Home },
    { id: 'food', label: 'Thực phẩm', icon: Utensils },
    { id: 'exercise', label: 'Tập luyện', icon: Activity },
    { id: 'progress', label: 'Tiến độ', icon: TrendingUp },
    { id: 'help', label: 'Trợ giúp', icon: HelpCircle },
  ];

  const renderContent = () => {
    switch (activeTab) {
      case 'home':
        return <DashboardHome onQuickAdd={() => setShowQuickAdd(true)} />;
      case 'food':
        return <FoodLogging />;
      case 'exercise':
        return <ExerciseLogging />;
      case 'progress':
        return <Progress />;
      case 'help':
        return <HelpSupport />;
      default:
        return <DashboardHome onQuickAdd={() => setShowQuickAdd(true)} />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top App Bar */}
      <header className="bg-white border-b sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <Activity className="size-6 text-green-600" />
            <span className="text-xl font-bold">HealthTrack</span>
          </div>
          <Button variant="ghost" size="sm" onClick={onLogout}>
            <LogOut className="size-4 mr-2" />
            Đăng xuất
          </Button>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6 pb-24">
        {renderContent()}
      </main>

      {/* Quick Add FAB */}
      <button
        onClick={() => setShowQuickAdd(true)}
        className="fixed bottom-20 right-6 size-14 bg-green-600 hover:bg-green-700 text-white rounded-full shadow-lg flex items-center justify-center transition-transform hover:scale-110"
      >
        <Plus className="size-6" />
      </button>

      {/* Bottom Navigation */}
      <nav className="fixed bottom-0 left-0 right-0 bg-white border-t">
        <div className="container mx-auto px-4">
          <div className="flex justify-around">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as Tab)}
                  className={`flex flex-col items-center py-3 px-4 ${
                    isActive ? 'text-green-600' : 'text-gray-500'
                  }`}
                >
                  <Icon className={`size-6 mb-1 ${isActive ? 'text-green-600' : 'text-gray-500'}`} />
                  <span className="text-xs">{tab.label}</span>
                </button>
              );
            })}
          </div>
        </div>
      </nav>

      {/* Quick Add Modal */}
      <QuickAddModal open={showQuickAdd} onClose={() => setShowQuickAdd(false)} />
    </div>
  );
}
