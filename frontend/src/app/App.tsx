import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Toaster } from './components/ui/sonner';
import LandingPage from './components/LandingPage';
import LoginPage from './components/LoginPage';
import SignupPage from './components/SignupPage';
import ForgotPasswordPage from './components/ForgotPasswordPage';
import ResetPasswordPage from './components/ResetPasswordPage';
import UserDashboard from './components/UserDashboard';
import AdminDashboard from './components/admin/AdminDashboard';
import api from './components/lib/api';
import { ChatbotWidget } from './components/chatbot/ChatbotWidget';

type Page = 'landing' | 'login' | 'signup' | 'forgot-password' | 'reset-password' | 'dashboard' | 'admin';
type UserRole = 'user' | 'admin' | null;

export default function App() {
  const [currentPage, setCurrentPage] = useState<Page>('landing');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userRole, setUserRole] = useState<UserRole>(null);
  const [isCheckingAuth, setIsCheckingAuth] = useState(true);
  const [userData, setUserData] = useState<any>(null);

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const resetToken = urlParams.get('token');
    if (resetToken && !isAuthenticated) {
      setCurrentPage('reset-password');
      setIsCheckingAuth(false);
      return;
    }

    const checkAuth = async () => {
      const accessToken = localStorage.getItem('access_token');
      const refreshToken = localStorage.getItem('refresh_token');

      if (!accessToken && !refreshToken) {
        setIsCheckingAuth(false);
        return;
      }

      try {
        const userRes = await api.get('/users/me');
        const role = userRes.data.user?.role || 'user';
        
        setUserData(userRes.data); // Lưu userData
        setIsAuthenticated(true);
        setUserRole(role as UserRole);
        setCurrentPage(role === 'admin' ? 'admin' : 'dashboard');
      } catch (error: any) {
        if (error.response?.status === 401 && refreshToken) {
          try {
            const refreshRes = await axios.post(
              `${import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'}/auth/refresh`,
              { refresh_token: refreshToken },
              { headers: { 'Content-Type': 'application/json' } }
            );

            const { access_token, refresh_token: newRefreshToken } = refreshRes.data;
            localStorage.setItem('access_token', access_token);
            if (newRefreshToken) {
              localStorage.setItem('refresh_token', newRefreshToken);
            }

            const userRes = await api.get('/users/me');
            const role = userRes.data.user?.role || 'user';
            
            setUserData(userRes.data); // Lưu userData
            setIsAuthenticated(true);
            setUserRole(role as UserRole);
            setCurrentPage(role === 'admin' ? 'admin' : 'dashboard');
          } catch (refreshError) {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            setIsAuthenticated(false);
            setUserRole(null);
            setCurrentPage('landing');
          }
        } else {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          setIsAuthenticated(false);
          setUserRole(null);
          setCurrentPage('landing');
        }
      } finally {
        setIsCheckingAuth(false);
      }
    };

    checkAuth();
  }, []);

  const handleLogin = (role: string | UserRole = 'user') => {
    const userRole = (role as UserRole) || 'user';
    setIsAuthenticated(true);
    setUserRole(userRole);
    setCurrentPage(userRole === 'admin' ? 'admin' : 'dashboard');
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setUserRole(null);
    setCurrentPage('landing');
  };

  const renderPage = () => {
    if (isCheckingAuth) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-100">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-pink-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Đang tải...</p>
          </div>
        </div>
      );
    }

    if (!isAuthenticated && currentPage === 'landing') {
      return <LandingPage onLogin={() => setCurrentPage('login')} onSignup={() => setCurrentPage('signup')} />;
    }

    if (!isAuthenticated && currentPage === 'login') {
      return <LoginPage 
        onLogin={handleLogin} 
        onBack={() => setCurrentPage('landing')} 
        onSignup={() => setCurrentPage('signup')}
        onForgotPassword={() => setCurrentPage('forgot-password')}
      />;
    }

    if (!isAuthenticated && currentPage === 'signup') {
      return <SignupPage onSignup={handleLogin} onBack={() => setCurrentPage('landing')} onLogin={() => setCurrentPage('login')} />;
    }

    if (!isAuthenticated && currentPage === 'forgot-password') {
      return <ForgotPasswordPage onBack={() => setCurrentPage('login')} />;
    }

    if (!isAuthenticated && currentPage === 'reset-password') {
      const urlParams = new URLSearchParams(window.location.search);
      const token = urlParams.get('token');
      
      return <ResetPasswordPage 
        onBack={() => setCurrentPage('login')} 
        onSuccess={() => setCurrentPage('login')}
        token={token || undefined}
      />;
    }

    if (isAuthenticated && userRole === 'admin') {
      return <AdminDashboard onLogout={handleLogout} />;
    }

    if (isAuthenticated && userRole === 'user') {
      return <UserDashboard onLogout={handleLogout} userData={userData} />;
    }

    return <LandingPage onLogin={() => setCurrentPage('login')} onSignup={() => setCurrentPage('signup')} />;
  };

  return (
    <>
      {renderPage()}
      <Toaster />
      {isAuthenticated && <ChatbotWidget />}
    </>
  );
}