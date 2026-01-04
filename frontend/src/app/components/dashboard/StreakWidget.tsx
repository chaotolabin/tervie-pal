import { useEffect, useState } from 'react';
import { Flame, Trophy, Calendar } from 'lucide-react';
import { Card, CardContent } from '../ui/card'; // Giả sử bạn có UI components này
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

  useEffect(() => {
    const fetchStreak = async () => {
      try {
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

    fetchStreak();
  }, []);

  if (loading) {
    return (
      <div className="animate-pulse bg-white p-4 rounded-xl border h-32 flex items-center justify-center">
        <span className="text-gray-400 text-sm">Đang tải dữ liệu...</span>
      </div>
    );
  }

  if (!streak) return null;

  return (
    <div className="bg-white p-5 rounded-2xl shadow-sm border border-gray-100">
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