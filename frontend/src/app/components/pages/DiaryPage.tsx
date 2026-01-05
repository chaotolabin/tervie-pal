import React, { useState, useEffect } from 'react';
import { LogService } from '../../../service/log.service';
import FoodLogging from '../dashboard/FoodLogging';
import ExerciseQuickAdd from '../dashboard/quick-add/ExerciseQuickAdd';
import { getLocalDateString } from '../../../utils/dateUtils';

export default function DiaryPage() {
  const [date, setDate] = useState(getLocalDateString());
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Gọi endpoint /logs/{target_date}
        const res = await LogService.getDailyLogs(date);
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
      <div className="grid grid-cols-4 gap-4 bg-white p-6 shadow">
        <div className="text-center">
          <p className="text-gray-500 text-sm">Nạp vào</p>
          <p className="font-bold text-xl">{data.summary?.total_calories_consumed || 0}</p>
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
        <div className="bg-white p-4 shadow">
          <h3 className="font-bold mb-4">Hoạt động thể chất</h3>
          {data.exercise_logs && data.exercise_logs.length > 0 ? (
            data.exercise_logs.map((entry: any) => (
              <div key={entry.id} className="mb-3 pb-3 border-b last:border-b-0">
                <div className="flex justify-between items-center mb-1">
                  <span className="text-sm text-gray-500">
                    {new Date(entry.logged_at).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })}
                  </span>
                  <span className="font-medium text-blue-600">-{Math.round(Number(entry.total_calories || 0))} kcal</span>
                </div>
                {entry.items && entry.items.length > 0 && (
                  <div className="pl-2 space-y-1">
                    {entry.items.map((item: any) => (
                      <div key={item.id} className="text-sm text-gray-600">
                        • {item.duration_min || 0} phút
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))
          ) : (
            <p className="text-gray-400 text-sm">Chưa có hoạt động thể chất.</p>
          )}
          <ExerciseQuickAdd />
        </div>
      </div>
    </div>
  );
}