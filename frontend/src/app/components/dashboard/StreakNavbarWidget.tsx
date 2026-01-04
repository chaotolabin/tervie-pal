import React, { useEffect, useState } from 'react';
import { Flame, Trophy } from 'lucide-react';
import { HoverCard, HoverCardContent, HoverCardTrigger } from '../ui/hover-card';
import { Button } from '../ui/button';
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
  const [open, setOpen] = useState(false);
  
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

  // Flame Icon component for weekly visualization
  const FlameIcon = ({ active, isToday }: { active: boolean; isToday: boolean }) => {
    if (!active) {
      return (
        <Flame className="size-6 text-gray-300" fill="none" strokeWidth={1.5} />
      );
    }
    return (
      <div className="relative">
        <Flame className="size-6 text-orange-500" fill="currentColor" />
        {isToday && (
          <div className="absolute -top-1 -right-1 size-2 bg-orange-500 rounded-full border border-white" />
        )}
      </div>
    );
  };

  // Get day names in English (Mon, Tue, etc.)
  const getDayName = (dateStr: string): string => {
    const date = new Date(dateStr);
    const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    return days[date.getDay()];
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
    <HoverCard openDelay={200} closeDelay={100} open={open} onOpenChange={setOpen}>
      <HoverCardTrigger asChild>
        <Button
          variant="ghost"
          size="sm"
          className="flex items-center gap-2 hover:bg-orange-50 hover:text-orange-600 transition-colors cursor-pointer"
          onClick={() => setOpen(!open)}
        >
          <Flame className="size-4 text-orange-500" fill="currentColor" />
          <span className="font-semibold text-base">{currentStreak}</span>
        </Button>
      </HoverCardTrigger>
      <HoverCardContent 
        align="end" 
        className="w-80 p-5 z-[9999]"
        sideOffset={8}
        side="bottom"
        onMouseEnter={() => setOpen(true)}
        onMouseLeave={() => setOpen(false)}
      >
        {loading ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-orange-500"></div>
          </div>
        ) : streak ? (
          <div className="space-y-4">
            {/* Header */}
            <div className="flex justify-between items-start">
              <div>
                <p className="text-gray-600 text-sm mb-1">Current Streak:</p>
                <p className="text-4xl font-black text-orange-500">
                  {currentStreak}
                </p>
              </div>
              
              {/* Longest Streak Badge */}
              <div className="flex items-center gap-2">
                <Trophy className="size-5 text-yellow-600" />
                <div>
                  <p className="text-sm font-semibold text-gray-900">Longest:</p>
                  <p className="text-lg font-bold text-gray-900">{longestStreak}</p>
                </div>
              </div>
            </div>

            {/* Week Visualization */}
            <div className="space-y-2">
              {/* Day Labels */}
              <div className="flex justify-between">
                {streak.week.map((item, index) => {
                  const dayName = getDayName(item.day);
                  const isToday = new Date().toISOString().split('T')[0] === item.day;
                  const isActive = item.status === 'green' || item.status === 'yellow';
                  
                  return (
                    <div key={index} className="flex flex-col items-center gap-1.5">
                      <span className={`text-xs font-medium ${isToday ? 'text-orange-500' : 'text-gray-600'}`}>
                        {dayName}
                      </span>
                      <FlameIcon active={isActive} isToday={isToday} />
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Milestone Progress */}
            <div className="space-y-2 pt-2 border-t border-gray-100">
              <p className="text-sm text-gray-600">
                Next milestone: <span className="font-semibold">{nextMilestone} days</span>
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
                Keep logging daily to maintain your streak!
              </p>
            </div>
          </div>
        ) : (
          <div className="text-center py-4 text-gray-500 text-sm">
            Chưa có dữ liệu streak
          </div>
        )}
      </HoverCardContent>
    </HoverCard>
  );
}

