import React, { useEffect, useState } from 'react';
import { API } from '../../../lib/api-client';

export default function StreakWidget() {
  const [streak, setStreak] = useState<any>(null);

  useEffect(() => {
    API.getStreak().then(res => setStreak(res.data));
  }, []);

  if (!streak) return null;

  return (
    <div className="bg-white p-4 rounded-xl shadow">
      <div className="flex justify-between items-center mb-4">
        <h3 className="font-bold">Chuỗi ngày (Streak)</h3>
        <span className="text-orange-500 font-bold">🔥 {streak.current_streak} ngày</span>
      </div>
      <div className="flex justify-between">
        {streak.week.map((d: any, i: number) => (
          <div key={i} className="flex flex-col items-center">
            <span className="text-xs text-gray-400">{new Date(d.day).toLocaleDateString('vi', {weekday: 'short'})}</span>
            <div className={`w-6 h-6 rounded-full mt-1 ${
              d.status === 'green' ? 'bg-green-500' : d.status === 'yellow' ? 'bg-yellow-400' : 'bg-gray-200'
            }`} />
          </div>
        ))}
      </div>
    </div>
  );
}