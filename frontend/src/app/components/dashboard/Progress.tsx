import React, { useEffect, useState } from 'react';
import { API } from '../../../lib/api';

export default function Progress() {
  const [goal, setGoal] = useState<any>(null);

  useEffect(() => {
    API.getGoal().then(res => setGoal(res.data));
  }, []);

  if (!goal) return <div>Chưa thiết lập mục tiêu.</div>;

  return (
    <div className="bg-white p-6 rounded-xl shadow">
      <h3 className="font-bold mb-4 italic text-blue-600">Mục tiêu: {goal.goal_type}</h3>
      <div className="space-y-4">
        <div>
          <div className="flex justify-between text-sm mb-1">
            <span>Calorie hàng ngày</span>
            <span>{goal.daily_calorie_target} kcal</span>
          </div>
          <div className="w-full bg-gray-200 h-2 rounded-full overflow-hidden">
             <div className="bg-blue-500 h-full" style={{width: '70%'}} /> {/* Bạn sẽ tính % dựa trên logs summary */}
          </div>
        </div>
      </div>
    </div>
  );
}