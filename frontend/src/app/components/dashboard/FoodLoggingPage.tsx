import React, { useState, useEffect, useCallback } from 'react';
import { LogService } from '../../../service/log.service';
import { GoalService } from '../../../service/goals.service';
import FoodLogging from './FoodLogging';
import FoodQuickAdd from './quick-add/foodquickadd';
import NutrientTargets from './NutrientTargets';
import { Calendar } from 'lucide-react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Input } from '../ui/input';
import { toast } from 'sonner';
import { getLocalDateString, getDaysAgoDateString } from '../../../utils/dateUtils';

export default function FoodLoggingPage() {
  const [date, setDate] = useState(getLocalDateString());
  const [selectedDateOption, setSelectedDateOption] = useState<string>('today'); // 'today', 'yesterday', '2days', 'custom'
  const [customDate, setCustomDate] = useState<string>(''); // Cho custom date picker
  const [data, setData] = useState<any>(null);
  const [goal, setGoal] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      // Fetch daily logs and goals in parallel
      const [logsRes, goalsRes] = await Promise.all([
        LogService.getDailyLogs(date).catch(() => null),
        GoalService.getCurrentGoal().catch(() => null), // Goals might not exist, so catch error
      ]);
      
      if (logsRes) {
        console.log('Daily logs response:', logsRes);
        setData(logsRes);
      }
      
      if (goalsRes) {
        setGoal(goalsRes);
      }
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
    
    const handleRefreshFoodLogs = (event?: any) => {
      // Nếu event có thông tin về ngày, kiểm tra xem có cần thay đổi date không
      if (event?.detail?.date) {
        const eventDate = event.detail.date;
        // Nếu ngày trong event khác với ngày hiện tại, cập nhật date
        if (eventDate !== date) {
          setDate(eventDate);
          // fetchData sẽ được gọi tự động khi date thay đổi
          return;
        }
      }
      // Nếu không có thông tin ngày hoặc cùng ngày, refresh ngay
      fetchData();
    };
    
    window.addEventListener('refreshDashboard', handleRefresh);
    window.addEventListener('refreshFoodLogs', handleRefreshFoodLogs);
    
    return () => {
      window.removeEventListener('refreshDashboard', handleRefresh);
      window.removeEventListener('refreshFoodLogs', handleRefreshFoodLogs);
    };
  }, [date, fetchData]);

  // Helper function để lấy date từ option
  const getDateFromOption = (option: string): string => {
    switch (option) {
      case 'today':
        return getLocalDateString();
      case 'yesterday':
        return getDaysAgoDateString(1);
      case '2days':
        return getDaysAgoDateString(2);
      default:
        return getLocalDateString();
    }
  };

  // Khi selectedDateOption thay đổi, cập nhật date (trừ custom)
  useEffect(() => {
    if (selectedDateOption !== 'custom') {
      const newDate = getDateFromOption(selectedDateOption);
      setDate(newDate);
    }
  }, [selectedDateOption]);

  // Xử lý khi thay đổi date option
  const handleDateOptionChange = (option: string) => {
    setSelectedDateOption(option);
    if (option === 'custom') {
      // Nếu chọn custom, mở date picker với ngày hiện tại
      setCustomDate(date);
    } else {
      const newDate = getDateFromOption(option);
      setDate(newDate);
    }
  };

  // Xử lý khi thay đổi custom date
  const handleCustomDateChange = (newDate: string) => {
    setCustomDate(newDate);
    setDate(newDate);
  };

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
        
        {/* Date Filter với các option */}
        <div className="flex items-center gap-2">
          <Calendar className="size-4 text-gray-500" />
          <Select value={selectedDateOption} onValueChange={handleDateOptionChange}>
            <SelectTrigger className="w-[150px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="today">Hôm nay</SelectItem>
              <SelectItem value="yesterday">Hôm qua</SelectItem>
              <SelectItem value="2days">2 ngày trước</SelectItem>
              <SelectItem value="custom">Chọn ngày khác...</SelectItem>
            </SelectContent>
          </Select>
          
          {/* Custom Date Picker - chỉ hiển thị khi chọn "Chọn ngày khác..." */}
          {selectedDateOption === 'custom' && (
            <Input
              type="date"
              value={customDate || date}
              onChange={(e) => handleCustomDateChange(e.target.value)}
              className="w-auto"
            />
          )}
        </div>
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

      {/* Nutrient Targets with Progress Bars */}
      {summary && (
        <NutrientTargets
          energy={{
            consumed: toNumber(summary.total_calories_consumed),
            target: toNumber(goal?.daily_calorie_target) || 2000, // Default to 2000 if no goal
          }}
          protein={{
            consumed: toNumber(summary.total_protein_g),
            target: toNumber(goal?.protein_grams) || 150, // Default to 150g if no goal
          }}
          carbs={{
            consumed: toNumber(summary.total_carbs_g),
            target: toNumber(goal?.carb_grams) || 200, // Default to 200g if no goal
          }}
          fat={{
            consumed: toNumber(summary.total_fat_g || 0),
            target: toNumber(goal?.fat_grams) || 65, // Default to 65g if no goal
          }}
          onRefresh={fetchData}
        />
      )}
      
      {!summary && !error && data && (
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
      {data && foodLogs.length > 0 ? (
        <FoodLogging foodLogs={foodLogs} />
      ) : data && foodLogs.length === 0 ? (
        <div className="bg-white rounded-xl shadow p-4">
          <h3 className="font-bold text-lg mb-4">Bữa ăn {selectedDateOption === 'today' ? 'hôm nay' : selectedDateOption === 'yesterday' ? 'hôm qua' : `ngày ${date}`}</h3>
          <p className="text-gray-400">Chưa có dữ liệu ăn uống.</p>
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow p-4">
          <h3 className="font-bold text-lg mb-4">Bữa ăn</h3>
          <p className="text-gray-400">Đang tải dữ liệu...</p>
        </div>
      )}
    </div>
  );
}

