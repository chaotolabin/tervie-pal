import React, { useState, useEffect } from 'react';
import { logService } from '../../../../service/apiClient';
import FoodLogging from '../dashboard/FoodLogging';
import ExerciseQuickAdd from '../dashboard/quick-add/ExerciseQuickAdd';

export default function DiaryPage() {
  const [date, setDate] = useState(new Date().toISOString().split('T')[0]);
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Gọi endpoint /logs/{target_date}
        const res = await logService.getDailyLogs(date);
        setData(res);
      } catch (error) {
        console.error('Error fetching daily logs:', error);
        setData(null);
      }
    };
    fetchData();
  }, [date]);

  if (!data) return <div>Đang tải nhật ký...</div>;

  return (
    <div className="p-4 space-y-6 max-w-4xl mx-auto">
      {/* Bộ chọn ngày */}
      <input type="date" value={date} onChange={(e) => setDate(e.target.value)} className="border p-2 rounded" />

      {/* Tóm tắt dinh dưỡng thực tế từ backend */}
      <div className="grid grid-cols-4 gap-4 bg-white p-6 rounded-xl shadow">
        <div className="text-center">
          <p className="text-gray-500 text-sm">Nạp vào</p>
          <p className="font-bold text-xl">{data.summary.total_calories_in}</p>
        </div>
        <div className="text-center">
          <p className="text-gray-500 text-sm">Tiêu hao</p>
          <p className="font-bold text-xl">{data.summary.total_calories_burned}</p>
        </div>
        {/* ... Carbs, Protein, Fat */}
      </div>

      {/* Danh sách log chi tiết */}
      <div className="grid md:grid-cols-2 gap-6">
        <FoodLogging foodLogs={data.food_logs} />
        <div className="bg-white p-4 rounded-xl shadow">
          <h3 className="font-bold mb-4">Hoạt động thể chất</h3>
          {data.exercise_logs.map((ex: any) => (
            <div key={ex.id} className="flex justify-between py-2 border-b">
              <span>{ex.exercise_name}</span>
              <span>-{ex.calories_burned} kcal</span>
            </div>
          ))}
          <ExerciseQuickAdd />
        </div>
      </div>
    </div>
  );
}