import React, { useState, useEffect, useCallback } from 'react';
import { LogService } from '../../../service/log.service';
import FoodLogging from './FoodLogging';
import FoodQuickAdd from './quick-add/foodquickadd';
import { toast } from 'sonner';

export default function FoodLoggingPage() {
  const [date, setDate] = useState(new Date().toISOString().split('T')[0]);
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await LogService.getDailyLogs(date);
      console.log('Daily logs response:', res);
      setData(res);
    } catch (error: any) {
      console.error('Error fetching daily logs:', error);
      
      // Xử lý các loại lỗi khác nhau
      if (error.response?.status === 401) {
        // Token hết hạn - interceptor sẽ tự động refresh và retry request
        // Đợi một chút để interceptor xử lý, sau đó retry
        setTimeout(async () => {
          try {
            const retryRes = await LogService.getDailyLogs(date);
            setData(retryRes);
            setError(null);
          } catch (retryError: any) {
            // Nếu vẫn lỗi sau khi retry, hiển thị lỗi
            setError('Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.');
            toast.error('Phiên đăng nhập đã hết hạn');
          } finally {
            setLoading(false);
          }
        }, 1500);
        return;
      } else if (error.response?.status === 403) {
        setError('Bạn không có quyền truy cập trang này');
        toast.error('Bạn không có quyền truy cập trang dinh dưỡng');
      } else if (error.response?.status >= 500) {
        setError('Lỗi server. Vui lòng thử lại sau.');
        toast.error('Lỗi server. Vui lòng thử lại sau.');
      } else if (error.message === 'Network Error' || !error.response) {
        setError('Không thể kết nối đến server. Vui lòng kiểm tra kết nối mạng.');
        toast.error('Không thể kết nối đến server');
      } else {
        const errorMsg = formatErrorMessage(error, 'Có lỗi xảy ra khi tải dữ liệu');
        setError(errorMsg);
        toast.error(errorMsg);
      }
      setData(null);
    } finally {
      setLoading(false);
    }
  }, [date]);

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
  }, [date, fetchData]);

  if (loading) {
    return (
      <div className="p-8 text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-pink-600 mx-auto mb-2"></div>
        <p className="text-gray-600">Đang tải dữ liệu...</p>
      </div>
    );
  }

  // Debug: Log current state
  console.log('FoodLoggingPage render:', { loading, error, data, hasSummary: !!data?.summary });

  // Đảm bảo luôn có giá trị mặc định để tránh lỗi render
  const summary = data?.summary || null;
  const foodLogs = data?.food_logs || [];

  // Helper function để convert giá trị thành số an toàn
  const toNumber = (value: any): number => {
    if (value === null || value === undefined) return 0;
    const num = typeof value === 'string' ? parseFloat(value) : Number(value);
    return isNaN(num) ? 0 : num;
  };

  // Helper function để format error message từ API response
  const formatErrorMessage = (error: any, defaultMsg: string = 'Có lỗi xảy ra'): string => {
    if (error?.response?.data?.detail) {
      const detail = error.response.data.detail;
      if (typeof detail === 'string') {
        return detail;
      } else if (Array.isArray(detail) && detail.length > 0) {
        // FastAPI validation errors thường là array
        return detail.map((err: any) => err.msg || JSON.stringify(err)).join(', ');
      } else if (typeof detail === 'object') {
        return JSON.stringify(detail);
      }
    }
    return error?.message || defaultMsg;
  };

  return (
    <div className="space-y-6 p-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Dinh dưỡng</h2>
        <input 
          type="date" 
          value={date} 
          onChange={(e) => setDate(e.target.value)} 
          className="border p-2 rounded"
        />
      </div>

      {/* Hiển thị lỗi nếu có */}
      {error && error !== 'Đang xác thực lại...' && (
        <div className="bg-red-50 border border-red-200 p-4 rounded-xl">
          <p className="text-red-600 text-center font-medium">{error}</p>
          <button
            onClick={fetchData}
            className="mt-2 mx-auto block text-red-600 hover:text-red-700 underline text-sm"
          >
            Thử lại
          </button>
        </div>
      )}

      {/* Tóm tắt dinh dưỡng */}
      {summary ? (
        <div className="grid grid-cols-4 gap-4 bg-white p-6 rounded-xl shadow">
          <div className="text-center">
            <p className="text-gray-500 text-sm">Nạp vào</p>
            <p className="font-bold text-xl">{toNumber(summary.total_calories_consumed)} kcal</p>
          </div>
          <div className="text-center">
            <p className="text-gray-500 text-sm">Tiêu hao</p>
            <p className="font-bold text-xl">{toNumber(summary.total_calories_burned)} kcal</p>
          </div>
          <div className="text-center">
            <p className="text-gray-500 text-sm">Protein</p>
            <p className="font-bold text-xl">{toNumber(summary.total_protein_g).toFixed(1)} g</p>
          </div>
          <div className="text-center">
            <p className="text-gray-500 text-sm">Carbs</p>
            <p className="font-bold text-xl">{toNumber(summary.total_carbs_g).toFixed(1)} g</p>
          </div>
        </div>
      ) : !error && data ? (
        <div className="bg-white p-6 rounded-xl shadow">
          <p className="text-gray-500 text-center">Chưa có dữ liệu dinh dưỡng cho ngày này.</p>
        </div>
      ) : null}

      {/* Thêm món ăn */}
      <div className="bg-white p-6 rounded-xl shadow">
        <h3 className="font-bold text-lg mb-4">Thêm món ăn</h3>
        <FoodQuickAdd />
      </div>

      {/* Danh sách log */}
      {data ? (
        <FoodLogging foodLogs={foodLogs} />
      ) : (
        <div className="bg-white rounded-xl shadow p-4">
          <h3 className="font-bold text-lg mb-4">Bữa ăn hôm nay</h3>
          <p className="text-gray-400">Chưa có dữ liệu ăn uống.</p>
        </div>
      )}
    </div>
  );
}

