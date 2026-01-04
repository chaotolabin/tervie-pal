import { useState } from 'react';
import { LayoutDashboard, Users, BarChart3, Shield, HelpCircle, LogOut, Menu } from 'lucide-react';
import { Button } from '../ui/button';
import AdminHome from './AdminHome';
import UserManagement from './UserManagement';
import Analytics from './Analytics';
import Moderation from './Moderation';
import SupportManagement from './SupportManagement';

interface AdminDashboardProps {
  onLogout: () => void;
}


type Tab = 'home' | 'users' | 'analytics' | 'moderation' | 'support';

export default function AdminDashboard({ onLogout }: AdminDashboardProps) {
  const [activeTab, setActiveTab] = useState<Tab>('home');
  const [sidebarOpen, setSidebarOpen] = useState(true);

  
  const menuItems = [
    { id: 'home', label: 'Tổng quan', icon: LayoutDashboard },
    { id: 'users', label: 'Người dùng', icon: Users },
    { id: 'analytics', label: 'Phân tích', icon: BarChart3 },
    { id: 'moderation', label: 'Kiểm duyệt', icon: Shield },
    { id: 'support', label: 'Hỗ trợ', icon: HelpCircle },    
  ] as const;

  
  const renderContent = () => {
    switch (activeTab) {
      case 'home':
        return <AdminHome />;
      case 'users':
        return <UserManagement />;
      case 'analytics':
        return <Analytics />;
      case 'moderation':
        return <Moderation />;
      case 'support':
        return <SupportManagement />;
      default:
        return <AdminHome />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar - Cố định Layout */}
      <aside className={`bg-gray-900 text-white ${sidebarOpen ? 'w-64' : 'w-20'} transition-all duration-300 flex flex-col`}>
        <div className="p-4 border-b border-gray-800 flex items-center justify-between">
          {sidebarOpen && <span className="text-xl font-bold tracking-tight">Admin Panel</span>}
          <Button 
            variant="ghost" 
            size="icon" 
            onClick={() => setSidebarOpen(!sidebarOpen)} 
            className="text-white hover:bg-gray-800"
          >
            <Menu className="size-5" />
          </Button>
        </div>

        <nav className="flex-1 p-4 overflow-y-auto">
          <ul className="space-y-2">
            {menuItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <li key={item.id}>
                  <button
                    onClick={() => setActiveTab(item.id as Tab)}
                    className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                      isActive
                        ? 'bg-green-600 text-white shadow-lg'
                        : 'text-gray-400 hover:bg-gray-800 hover:text-white'
                    }`}
                  >
                    <Icon className="size-5 shrink-0" />
                    {sidebarOpen && <span className="font-medium">{item.label}</span>}
                  </button>
                </li>
              );
            })}
          </ul>
        </nav>

        <div className="p-4 border-t border-gray-800">
          <Button
            variant="ghost"
            onClick={onLogout}
            className={`w-full ${sidebarOpen ? 'justify-start' : 'justify-center'} text-gray-400 hover:bg-red-900/20 hover:text-red-400 transition-colors`}
          >
            <LogOut className="size-5 shrink-0" />
            {sidebarOpen && <span className="ml-3 font-medium">Đăng xuất</span>}
          </Button>
        </div>
      </aside>

      {/* Main Content - Nơi hiển thị dữ liệu từ API */}
      <main className="flex-1 overflow-auto relative">
        <div className="container mx-auto px-6 py-8">
          {renderContent()}
        </div>
      </main>
    </div>
  );
}