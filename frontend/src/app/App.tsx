import { useState } from 'react';
import { Toaster } from './components/ui/sonner';
import LandingPage from './components/LandingPage';
import LoginPage from './components/LoginPage';
import SignupPage from './components/SignupPage';
import UserDashboard from './components/UserDashboard';
import AdminDashboard from './components/admin/AdminDashboard';
import { ChatbotWidget } from './components/chatbot/ChatbotWidget';  // ✅ Import chatbot

type Page = 'landing' | 'login' | 'signup' | 'dashboard' | 'admin';
type UserRole = 'user' | 'admin' | null;

export default function App() {
  const [currentPage, setCurrentPage] = useState<Page>('landing');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userRole, setUserRole] = useState<UserRole>(null);

  const handleLogin = (role: UserRole = 'user') => {
    setIsAuthenticated(true);
    setUserRole(role);
    setCurrentPage(role === 'admin' ? 'admin' : 'dashboard');
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setUserRole(null);
    setCurrentPage('landing');
  };

  const renderPage = () => {
    if (!isAuthenticated && currentPage === 'landing') {
      return <LandingPage onLogin={() => setCurrentPage('login')} onSignup={() => setCurrentPage('signup')} />;
    }

    if (!isAuthenticated && currentPage === 'login') {
      return <LoginPage onLogin={handleLogin} onBack={() => setCurrentPage('landing')} onSignup={() => setCurrentPage('signup')} />;
    }

    if (!isAuthenticated && currentPage === 'signup') {
      return <SignupPage onSignup={handleLogin} onBack={() => setCurrentPage('landing')} onLogin={() => setCurrentPage('login')} />;
    }

    if (isAuthenticated && userRole === 'admin') {
      return <AdminDashboard onLogout={handleLogout} />;
    }

    if (isAuthenticated && userRole === 'user') {
      return <UserDashboard onLogout={handleLogout} />;
    }

    return <LandingPage onLogin={() => setCurrentPage('login')} onSignup={() => setCurrentPage('signup')} />;
  };

  return (
    <>
      {renderPage()}
      <Toaster />
      {isAuthenticated && <ChatbotWidget />}  {/* ✅ Thêm chatbot - chỉ hiện khi đã login */}
    </>
  );
}