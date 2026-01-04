import React, { useEffect, useState } from 'react';
import { Flame, Trophy } from 'lucide-react';
import { Button } from '../ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../ui/dialog';
import api from '../lib/api';

interface StreakDay {
  day: string; // YYYY-MM-DD
  status: 'green' | 'yellow' | 'gray';
}

interface StreakResponse {
  current_streak: number;
  longest_streak: number;
  week: StreakDay[];
  /** Optional: Next milestone goal (e.g., 10, 30, 100) */
  next_milestone?: number;
}

interface StreakNavbarWidgetProps {
  /** Optional: Pass streak data from parent to avoid duplicate API calls */
  streakData?: StreakResponse | null;
}

export default function StreakNavbarWidget({ streakData: streakDataProp }: StreakNavbarWidgetProps) {
  const [streak, setStreak] = useState<StreakResponse | null>(streakDataProp || null);
  const [loading, setLoading] = useState(!streakDataProp);
  const [isModalOpen, setIsModalOpen] = useState(false);
  
  // Calculate next milestone (default: 10, 30, 100, etc.)
  const calculateNextMilestone = (current: number): number => {
    if (current < 10) return 10;
    if (current < 30) return 30;
    if (current < 100) return 100;
    // For 100+, increment by 50
    return Math.ceil((current + 1) / 50) * 50;
  };

  const fetchStreak = async () => {
    try {
      setLoading(true);
      const res = await api.get('/streak');
      setStreak(res.data);
    } catch (error) {
      console.error("Lỗi tải streak:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Only fetch if no prop data provided
    if (!streakDataProp) {
      fetchStreak();
    } else {
      setStreak(streakDataProp);
      setLoading(false);
    }

    // Listen for refresh events
    const handleRefresh = () => {
      fetchStreak();
    };

    window.addEventListener('refreshDashboard', handleRefresh);
    window.addEventListener('refreshStreak', handleRefresh);

    return () => {
      window.removeEventListener('refreshDashboard', handleRefresh);
      window.removeEventListener('refreshStreak', handleRefresh);
    };
  }, [streakDataProp]);

  // Update when prop changes
  useEffect(() => {
    if (streakDataProp) {
      setStreak(streakDataProp);
    }
  }, [streakDataProp]);

  const currentStreak = streak?.current_streak || 0;
  const longestStreak = streak?.longest_streak || 0;
  const nextMilestone = streak?.next_milestone || calculateNextMilestone(currentStreak);
  const milestoneProgress = Math.min((currentStreak / nextMilestone) * 100, 100);

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

  // Don't render if no data
  if (!streak && loading) {
    return (
      <Button
        variant="ghost"
        size="sm"
        className="flex items-center gap-2"
        disabled
      >
        <Flame className="size-4 text-gray-300" />
        <span className="font-semibold text-base text-gray-400">-</span>
      </Button>
    );
  }

  return (
    <>
      <Button
        variant="ghost"
        size="sm"
        className="flex items-center gap-2 hover:bg-orange-50 hover:text-orange-600 transition-colors cursor-pointer"
        onClick={() => setIsModalOpen(true)}
      >
        <Flame className="size-4 text-orange-500" fill="currentColor" />
        <span className="font-semibold text-base">{currentStreak}</span>
      </Button>

      {/* Streak Detail Modal */}
      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Flame className="size-5 text-orange-500" fill="currentColor" />
              Chi tiết Streak
            </DialogTitle>
          </DialogHeader>

          {loading ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-orange-500"></div>
            </div>
          ) : streak ? (
            <div className="space-y-6 py-4">
              {/* Current Streak & Longest Streak */}
              <div className="flex justify-between items-center">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Chuỗi hiện tại</p>
                  <p className="text-3xl font-black text-orange-500">
                    {currentStreak} <span className="text-base font-normal text-gray-400">ngày</span>
                  </p>
                </div>
                
                <div className="bg-yellow-50 px-4 py-3 rounded-lg flex items-center gap-2 border border-yellow-100">
                  <Trophy className="size-5 text-yellow-600" />
                  <div>
                    <p className="text-xs text-yellow-600/80 mb-1">Kỷ lục</p>
                    <p className="text-xl font-bold text-yellow-700">{longestStreak} ngày</p>
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

              {/* Milestone Progress */}
              <div className="space-y-2 pt-2 border-t border-gray-100">
                <p className="text-sm text-gray-600">
                  Mốc tiếp theo: <span className="font-semibold">{nextMilestone} ngày</span>
                </p>
                
                {/* Progress Bar */}
                <div className="relative w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div 
                    className="absolute left-0 top-0 h-full bg-orange-500 transition-all duration-300"
                    style={{ width: `${milestoneProgress}%` }}
                  />
                </div>
                
                {/* Progress Text */}
                <div className="flex justify-between text-xs text-gray-500">
                  <span>{currentStreak}/{nextMilestone}</span>
                  <span>{Math.round(milestoneProgress)}%</span>
                </div>
              </div>

              {/* Motivational Message */}
              <div className="pt-2">
                <p className="text-xs text-gray-500 text-center">
                  Tiếp tục ghi nhận hàng ngày để duy trì streak!
                </p>
              </div>
            </div>
          ) : (
            <div className="text-center py-4 text-gray-500 text-sm">
              Chưa có dữ liệu streak
            </div>
          )}
        </DialogContent>
      </Dialog>
    </>
  );
}

