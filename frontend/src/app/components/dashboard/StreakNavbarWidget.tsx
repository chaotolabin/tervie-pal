import React, { useEffect, useState } from 'react';
import { Flame, Trophy } from 'lucide-react';
import { Button } from '../ui/button';
import { HoverCard, HoverCardContent, HoverCardTrigger } from '../ui/hover-card';
import { Card, CardContent } from '../ui/card';
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

  // Get streak color based on length
  const getStreakColor = () => {
    if (currentStreak >= 30) return 'from-yellow-500 to-red-600';
    if (currentStreak >= 7) return 'from-red-200 to-red-200';
    return 'from-yellow-100 to-yellow-100';
  }; 

  // Get streak message
  const getStreakMessage = () => {
    if (currentStreak === 0) return 'Bắt đầu streak của bạn ngay nào!';
    if (currentStreak < 7) return 'Đang khởi động tốt rùi nè ÒvÓ!';
    if (currentStreak < 30) return 'Tiếp tục phát huy nữa nha -.-!';
    return 'Streak đỉnh cao, OMG!';
  };

  // Get text color based on streak length
  const getTextColor = () => {
    if (currentStreak >= 0 && currentStreak < 30) return 'text-orange-800';
    return 'text-white';
  };

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
    <HoverCard openDelay={200} closeDelay={100}>
      <HoverCardTrigger asChild>
        <Button
          variant="ghost"
          size="sm"
          className="flex items-center gap-2 hover:bg-orange-50 hover:text-orange-600 transition-colors"
        >
          <Flame className="size-4 text-orange-500" fill="currentColor" />
          <span className="font-semibold text-base">{currentStreak}</span>
        </Button>
      </HoverCardTrigger>

      <HoverCardContent className="w-80 p-0 bg-transparent border-none shadow-none" align="end" sideOffset={8}>
        <Card className={`bg-gradient-to-br ${getStreakColor()} ${getTextColor()} border-none shadow-xl`}>
          <CardContent className="p-5">
            <div className="space-y-4">
              {/* Header with Circular Streak Display */}
              <div className="flex items-center gap-4">
                <div className="relative">
                  <div className="size-20 rounded-full border-4 border-white/30 flex items-center justify-center bg-white/10">
                    <div className="text-center">
                      <p className="text-3xl font-bold">{currentStreak}</p>
                      <p className="text-xs opacity-90">ngày</p>
                    </div>
                  </div>
                  <div className="absolute -top-1 -right-1">
                    <Flame className="size-6 text-orange-300 animate-pulse" />
                  </div>
                </div>

                <div className="flex-1">
                  <p className="text-sm opacity-90">Streak hiện tại</p>
                  <p className="font-semibold mt-1 text-base">{getStreakMessage()}</p>
                  {longestStreak > 0 && (
                    <div className="flex items-center gap-1.5 mt-2">
                      <Trophy className="size-3 opacity-75" />
                      <p className="text-xs opacity-75">
                        Kỷ lục: {longestStreak} ngày
                      </p>
                    </div>
                  )}
                </div>
              </div>

              {/* 7 Days Visualization */}
              {streak?.week && streak.week.length > 0 && (
                <div className="pt-3 border-t border-white/20">
                  <p className="text-xs opacity-90 mb-3">7 ngày gần nhất</p>
                  <div className="flex justify-between items-end">
                    {streak.week.map((item, index) => {
                      const date = new Date(item.day);
                      const dayName = date.toLocaleDateString('vi-VN', { weekday: 'short' });
                      
                      // Map màu sắc theo status
                      let bgColor = 'bg-white/20';
                      let borderColor = 'border-white/30';
                      let iconColor = 'text-white/60';

                      if (item.status === 'green') {
                        bgColor = 'bg-green-500';
                        borderColor = 'border-green-600';
                        iconColor = 'text-white';
                      } else if (item.status === 'yellow') {
                        bgColor = 'bg-yellow-400';
                        borderColor = 'border-yellow-500';
                        iconColor = 'text-white';
                      }

                      const isToday = new Date().toISOString().split('T')[0] === item.day;

                      return (
                        <div key={index} className="flex flex-col items-center gap-2">
                          <span className={`text-[10px] uppercase font-medium ${isToday ? 'opacity-100' : 'opacity-75'}`}>
                            {dayName}
                          </span>
                          
                          <div 
                            className={`
                              size-8 rounded-full flex items-center justify-center border-2 transition-all
                              ${bgColor} ${borderColor} ${iconColor}
                              ${isToday ? 'ring-2 ring-white/50 ring-offset-2 ring-offset-transparent' : ''}
                            `}
                            title={`${getDayName(item.day)} ${getFormattedDate(item.day)}`}
                          >
                            {item.status === 'green' && (
                              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" className="size-3.5">
                                <path d="M20 6 9 17l-5-5" />
                              </svg>
                            )}
                            {item.status === 'yellow' && (
                              <span className="text-xs font-bold">!</span>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                  
                  {/* Legend */}
                  <div className="flex justify-center gap-3 mt-3 pt-2 border-t border-white/10">
                    <div className="flex items-center gap-1.5">
                      <div className="size-3 rounded-full bg-green-500 border border-green-600 flex items-center justify-center">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" className="size-2 text-white">
                          <path d="M20 6 9 17l-5-5" />
                        </svg>
                      </div>
                      <span className="text-[10px] opacity-75">Đúng hạn</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <div className="size-3 rounded-full bg-yellow-400 border border-yellow-500 flex items-center justify-center">
                        <span className="text-[8px] font-bold text-white">!</span>
                      </div>
                      <span className="text-[10px] opacity-75">Sau hạn</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <div className="size-3 rounded-full bg-white/20 border border-white/30"></div>
                      <span className="text-[10px] opacity-75">Chưa có</span>
                    </div>
                  </div>
                </div>
              )}

              {/* Progress to next milestone */}
              {currentStreak > 0 && (
                <div className="pt-3 border-t border-white/20">
                  <div className="flex justify-between text-xs opacity-90 mb-2">
                    <span>Mốc tiếp theo</span>
                    <span>
                      {currentStreak < 7 ? `${7 - currentStreak} ngày` :
                       currentStreak < 30 ? `${30 - currentStreak} ngày` :
                       currentStreak < 100 ? `${100 - currentStreak} ngày` :
                       'Đã đạt 100 ngày! 🎉'}
                    </span>
                  </div>
                  <div className="h-2 bg-white/20 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-white/60 rounded-full transition-all duration-500"
                      style={{
                        width: `${currentStreak < 7 
                          ? (currentStreak / 7) * 100 
                          : currentStreak < 30 
                          ? ((currentStreak - 7) / 23) * 100 
                          : currentStreak < 100
                          ? ((currentStreak - 30) / 70) * 100
                          : 100}%`
                      }}
                    />
                  </div>
                </div>
              )}

              {/* Motivational tip */}
              <p className="text-xs text-center opacity-75 pt-2">
                Nhớ ghi lại dinh dưỡng và tập luyện hàng ngày để duy trì streak!
              </p>
            </div>
          </CardContent>
        </Card>
      </HoverCardContent>
    </HoverCard>
  );
}

