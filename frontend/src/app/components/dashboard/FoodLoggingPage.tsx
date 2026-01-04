import React, { useState, useEffect } from 'react';
import { LogService } from '../../../service/log.service';
import FoodLogging from './FoodLogging';
import FoodQuickAdd from './quick-add/foodquickadd';

export default function FoodLoggingPage() {
  const [date, setDate] = useState(new Date().toISOString().split('T')[0]);
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    setLoading(true);
    try {
      const res = await LogService.getDailyLogs(date);
      setData(res);
    } catch (error: any) {
      console.error('Error fetching daily logs:', error);
      // Nếu lỗi 401, có thể token hết hạn - sẽ được xử lý bởi interceptor
      if (error.response?.status === 401) {
        // Token sẽ được refresh tự động bởi api interceptor
        // Chỉ cần set data null để hiển thị empty state
      }
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    
    // Lắng nghe event refresh từ các component con
    const handleRefresh = () => {
      fetchData();
    };
    
    const handleRefreshFoodLogs = () => {
      fetchData();
    };
    
    window.addEventListener('refreshDashboard', handleRefresh);
    window.addEventListener('refreshFoodLogs', handleRefreshFoodLogs);
    
    return () => {
      window.removeEventListener('refreshDashboard', handleRefresh);
      window.removeEventListener('refreshFoodLogs', handleRefreshFoodLogs);
    };
  }, [date]);

  if (loading) {
    return (
      <div className="p-8 text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-pink-600 mx-auto mb-2"></div>
        <p className="text-gray-600">Đang tải dữ liệu...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Dinh dưỡng</h2>
        <input 
          type="date" 
          value={date} 
          onChange={(e) => setDate(e.target.value)} 
          className="border p-2 rounded"
        />
      </div>

      {/* Tóm tắt dinh dưỡng */}
      {data?.summary ? (
        <div className="grid grid-cols-4 gap-4 bg-white p-6 rounded-xl shadow">
          <div className="text-center">
            <p className="text-gray-500 text-sm">Nạp vào</p>
            <p className="font-bold text-xl">{data.summary.total_calories_consumed || 0} kcal</p>
          </div>
          <div className="text-center">
            <p className="text-gray-500 text-sm">Tiêu hao</p>
            <p className="font-bold text-xl">{data.summary.total_calories_burned || 0} kcal</p>
          </div>
          <div className="text-center">
            <p className="text-gray-500 text-sm">Protein</p>
            <p className="font-bold text-xl">{data.summary.total_protein_g?.toFixed(1) || 0} g</p>
          </div>
          <div className="text-center">
            <p className="text-gray-500 text-sm">Carbs</p>
            <p className="font-bold text-xl">{data.summary.total_carbs_g?.toFixed(1) || 0} g</p>
          </div>
        </div>
      ) : (
        <div className="bg-white p-6 rounded-xl shadow">
          <p className="text-gray-500 text-center">Chưa có dữ liệu dinh dưỡng cho ngày này.</p>
        </div>
      )}

      {/* Thêm món ăn */}
      <div className="bg-white p-6 rounded-xl shadow">
        <h3 className="font-bold text-lg mb-4">Thêm món ăn</h3>
        <FoodQuickAdd />
      </div>

      {/* Danh sách log */}
      <FoodLogging foodLogs={data?.food_logs || []} />
    </div>
  );
}

