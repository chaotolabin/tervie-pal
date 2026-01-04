import React from 'react';
import { toast } from 'sonner';

export default function FoodLogging({ foodLogs }: { foodLogs: any[] }) {
  const handleDelete = async (logId: number) => {
    try {
      const { LogService } = await import('../../../service/log.service');
      await LogService.deleteFoodLog(logId);
      toast.success('Đã xóa bữa ăn');
      
      // Trigger refresh thay vì reload toàn bộ trang
      window.dispatchEvent(new CustomEvent('refreshDashboard'));
      window.dispatchEvent(new CustomEvent('refreshFoodLogs'));
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Không thể xóa bữa ăn');
    }
  };

  return (
    <div className="bg-white rounded-xl shadow p-4">
      <h3 className="font-bold text-lg mb-4">Bữa ăn hôm nay</h3>
      {foodLogs.length === 0 ? (
        <p className="text-gray-400">Chưa có dữ liệu ăn uống.</p>
      ) : (
        foodLogs.map((log) => (
          <div key={log.id} className="flex justify-between border-b py-2 text-sm">
            <span>{log.meal_type} - {log.items.length} món</span>
            <span className="font-medium text-blue-600">{log.total_calories} kcal</span>
          </div>
        ))
      )}
    </div>
  );
}