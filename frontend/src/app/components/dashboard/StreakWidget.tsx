import React, { useEffect, useState } from 'react';
import { Flame, Trophy, Calendar } from 'lucide-react';
import { Card, CardContent } from '../ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../ui/dialog';
import { toast } from 'sonner';
import api from '../lib/api';


interface StreakDay {
  day: string; // YYYY-MM-DD
  status: 'green' | 'yellow' | 'gray';
}

interface StreakResponse {
  current_streak: number;
  longest_streak: number;
  week: StreakDay[];
}

export default function StreakWidget() {
  const [streak, setStreak] = useState<StreakResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const fetchStreak = async () => {
    try {
      setLoading(true);
      // Gọi endpoint GET /streak từ streak.py
      const res = await api.get('/streak');
      setStreak(res.data);
    } catch (error) {
      console.error("Lỗi tải streak:", error);
      // Không toast lỗi ở đây để tránh spam nếu user chưa log food
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStreak();
    
    // Lắng nghe event refresh từ các component log (food/exercise)
    const handleRefresh = () => {
      fetchStreak();
    };
    
    window.addEventListener('refreshDashboard', handleRefresh);
    window.addEventListener('refreshStreak', handleRefresh);
    
    return () => {
      window.removeEventListener('refreshDashboard', handleRefresh);
      window.removeEventListener('refreshStreak', handleRefresh);
    };
  }, []);

  if (loading) {
    return (
      <div className="animate-pulse bg-white p-4 rounded-xl border h-32 flex items-center justify-center">
        <span className="text-gray-400 text-sm">Đang tải dữ liệu...</span>
      </div>
    );
  }

  if (!streak) return null;

  // Get day names in Vietnamese
  const getDayName = (dateStr: string): string => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('vi-VN', { weekday: 'short' }); // T2, T3...
  };

  // Get formatted date
  const getFormattedDate = (dateStr: string): string => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('vi-VN', { day: 'numeric', month: 'numeric' }); // 01/01
  };

  return (
    <>
      <div 
        className="bg-white p-5 rounded-2xl shadow-sm border border-gray-100 cursor-pointer hover:shadow-md transition-shadow"
        onClick={() => setIsModalOpen(true)}
      >
      {/* Header: Current Streak */}
      <div className="flex justify-between items-start mb-6">
        <div>
          <h3 className="text-gray-500 text-sm font-medium mb-1 flex items-center gap-2">
            <Flame className="size-4 text-orange-500" fill="currentColor" />
            Chuỗi hiện tại
          </h3>
          <p className="text-3xl font-black text-gray-900">
            {streak.current_streak} <span className="text-sm font-normal text-gray-400">ngày</span>
          </p>
        </div>
        
        {/* Longest Streak Badge */}
        <div className="bg-yellow-50 px-3 py-1.5 rounded-lg flex items-center gap-2 border border-yellow-100">
          <Trophy className="size-4 text-yellow-600" />
          <div className="text-xs">
            <span className="text-yellow-700 block font-bold">{streak.longest_streak} ngày</span>
            <span className="text-yellow-600/80">Kỷ lục</span>
          </div>
        </div>
      </div>

      {/* Week Visualization */}
      <div>
        <div className="flex justify-between items-end">
          {streak.week.map((item, index) => {
            const date = new Date(item.day);
            const dayName = date.toLocaleDateString('vi-VN', { weekday: 'short' }); // T2, T3...
            
            // Map màu sắc theo status từ Backend
            // green: Đã hoàn thành mục tiêu
            // yellow: Có log nhưng chưa đủ
            // gray: Không có dữ liệu/Tương lai
            let bgColor = 'bg-gray-100';
            let textColor = 'text-gray-400';
            let borderColor = 'border-transparent';

            if (item.status === 'green') {
              bgColor = 'bg-green-500';
              textColor = 'text-white';
              borderColor = 'border-green-600';
            } else if (item.status === 'yellow') {
              bgColor = 'bg-yellow-400';
              textColor = 'text-white';
              borderColor = 'border-yellow-500';
            }

            // Highlight ngày hôm nay
            const isToday = new Date().toISOString().split('T')[0] === item.day;

            return (
              <div key={index} className="flex flex-col items-center gap-2">
                <span className={`text-[10px] uppercase font-bold ${isToday ? 'text-blue-600' : 'text-gray-400'}`}>
                  {dayName}
                </span>
                
                <div 
                  className={`
                    size-8 rounded-full flex items-center justify-center border-2 transition-all
                    ${bgColor} ${borderColor} ${textColor}
                    ${item.status === 'green' ? 'shadow-md shadow-green-200' : ''}
                  `}
                  title={item.day}
                >
                  {item.status === 'green' && <CheckIcon />}
                </div>
              </div>
            );
          })}
        </div>
      </div>
      </div>

      {/* Streak Detail Modal */}
      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Flame className="size-5 text-orange-500" fill="currentColor" />
              Chi tiết Streak
            </DialogTitle>
          </DialogHeader>

          <div className="space-y-6 py-4">
            {/* Current Streak & Longest Streak */}
            <div className="flex justify-between items-center">
              <div>
                <p className="text-sm text-gray-600 mb-1">Chuỗi hiện tại</p>
                <p className="text-3xl font-black text-orange-500">
                  {streak.current_streak} <span className="text-base font-normal text-gray-400">ngày</span>
                </p>
              </div>
              
              <div className="bg-yellow-50 px-4 py-3 rounded-lg flex items-center gap-2 border border-yellow-100">
                <Trophy className="size-5 text-yellow-600" />
                <div>
                  <p className="text-xs text-yellow-600/80 mb-1">Kỷ lục</p>
                  <p className="text-xl font-bold text-yellow-700">{streak.longest_streak} ngày</p>
                </div>
              </div>
            </div>

            {/* 7 Days Status */}
            <div className="space-y-3">
              <p className="text-sm font-semibold text-gray-700">7 ngày gần nhất</p>
              <div className="grid grid-cols-7 gap-2">
                {streak.week.map((item, index) => {
                  const isToday = new Date().toISOString().split('T')[0] === item.day;
                  
                  // Map màu sắc theo status
                  let bgColor = 'bg-gray-200';
                  let borderColor = 'border-gray-300';
                  let textColor = 'text-gray-500';
                  let statusText = 'Chưa có';

                  if (item.status === 'green') {
                    bgColor = 'bg-green-500';
                    borderColor = 'border-green-600';
                    textColor = 'text-white';
                    statusText = 'Hoàn thành đúng hạn';
                  } else if (item.status === 'yellow') {
                    bgColor = 'bg-yellow-400';
                    borderColor = 'border-yellow-500';
                    textColor = 'text-white';
                    statusText = 'Hoàn thành sau hạn';
                  }

                  return (
                    <div 
                      key={index} 
                      className="flex flex-col items-center gap-1.5"
                      title={`${getDayName(item.day)} ${getFormattedDate(item.day)} - ${statusText}`}
                    >
                      <span className={`text-[10px] font-medium ${isToday ? 'text-orange-600 font-bold' : 'text-gray-500'}`}>
                        {getDayName(item.day)}
                      </span>
                      <div 
                        className={`
                          size-10 rounded-full flex items-center justify-center border-2 transition-all
                          ${bgColor} ${borderColor} ${textColor}
                          ${isToday ? 'ring-2 ring-orange-400 ring-offset-2' : ''}
                          ${item.status === 'green' ? 'shadow-md shadow-green-200' : ''}
                        `}
                      >
                        {item.status === 'green' && (
                          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" className="size-4">
                            <path d="M20 6 9 17l-5-5" />
                          </svg>
                        )}
                        {item.status === 'yellow' && (
                          <span className="text-xs font-bold">!</span>
                        )}
                      </div>
                      <span className="text-[9px] text-gray-400">{getFormattedDate(item.day)}</span>
                    </div>
                  );
                })}
              </div>

              {/* Legend */}
              <div className="flex justify-center gap-4 pt-2 border-t border-gray-100">
                <div className="flex items-center gap-1.5">
                  <div className="size-3 rounded-full bg-green-500 border border-green-600"></div>
                  <span className="text-xs text-gray-600">Đúng hạn</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <div className="size-3 rounded-full bg-yellow-400 border border-yellow-500"></div>
                  <span className="text-xs text-gray-600">Sau hạn</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <div className="size-3 rounded-full bg-gray-200 border border-gray-300"></div>
                  <span className="text-xs text-gray-600">Chưa có</span>
                </div>
              </div>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}

// Icon check nhỏ
function CheckIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" className="size-3">
      <path d="M20 6 9 17l-5-5" />
    </svg>
  );
}