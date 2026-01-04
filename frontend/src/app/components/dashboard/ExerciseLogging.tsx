import React, { useState, useEffect, useRef } from 'react';
import { Search, Plus, Filter, Clock, Flame, Dumbbell, Loader2, Trash2, Calendar } from 'lucide-react';
import { Input } from '../ui/input';
import { Button } from '../ui/button';
import { Card, CardContent } from '../ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Badge } from '../ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '../ui/dialog';
import { Label } from '../ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { toast } from 'sonner';
import api from '../lib/api';
import { LogService } from '../../../service/log.service';
import { getLocalDateString, getDaysAgoDateString } from '../../../utils/dateUtils';

// --- Interfaces khớp với Backend ---
interface ExerciseLog {
  id: number; // item.id
  entry_id: number; // entry.id - cần để xóa
  exercise: {
    id: number;
    description: string;
    major_heading: string;
    met_value: number;
  };
  duration_minutes: number;
  calories_burned: number;
  logged_at: string;
}

interface ExerciseSearchResult {
  id: number;
  description: string;
  major_heading: string;
  met_value: number;
}

export default function ExerciseLogging() {
  // State dữ liệu thực
  const [logs, setLogs] = useState<ExerciseLog[]>([]);
  const [allLogs, setAllLogs] = useState<ExerciseLog[]>([]); // Lưu tất cả logs để filter
  const [searchResults, setSearchResults] = useState<ExerciseSearchResult[]>([]);
  const [allMajorHeadings, setAllMajorHeadings] = useState<string[]>([]); // Tất cả major headings để hiển thị categories
  const [recentExercises, setRecentExercises] = useState<ExerciseSearchResult[]>([]); // Bài tập gần đây
  
  // State UI
  const [searchQuery, setSearchQuery] = useState('');
  const [searchMajorHeading, setSearchMajorHeading] = useState<string>('all'); // Filter major heading trong search
  const [loading, setLoading] = useState(false);
  const [activeMainTab, setActiveMainTab] = useState<'history' | 'search'>('history'); // Tab chính: history hoặc search
  const [searchTab, setSearchTab] = useState<'recent' | 'browse'>('browse'); // Tab trong search: recent hoặc browse
  
  // State cho filter
  const [selectedDate, setSelectedDate] = useState<string>(() => {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  });
  const [selectedDateOption, setSelectedDateOption] = useState<string>('today'); // 'today', 'yesterday', '2days', 'custom'
  const [customDate, setCustomDate] = useState<string>(''); // Cho custom date picker
  const [selectedMajorHeading, setSelectedMajorHeading] = useState<string>('all');
  
  // State cho Dialog thêm bài tập
  const [selectedExercise, setSelectedExercise] = useState<ExerciseSearchResult | null>(null);
  const [duration, setDuration] = useState<string>('30');
  const [exerciseDate, setExerciseDate] = useState<string>(() => {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }); // Ngày để thêm bài tập
  const [submitting, setSubmitting] = useState(false);

  // 1. Tải lịch sử tập luyện theo ngày
  const fetchLogs = async (date: string) => {
    try {
      setLoading(true);
      // Sử dụng /logs/daily để lấy cả exercise_logs, không phải /logs/summary
      const res = await api.get(`/logs/daily/${date}`);
      // Backend trả về logs trong object exercise_logs với items bên trong
      const exerciseEntries = res.data.exercise_logs || [];
      
      // Debug: log để kiểm tra
      console.log('=== FETCH LOGS DEBUG ===');
      console.log('Date:', date);
      console.log('Full response:', res.data);
      console.log('Exercise entries count:', exerciseEntries.length);
      exerciseEntries.forEach((entry: any, idx: number) => {
        console.log(`Entry ${idx}:`, {
          id: entry.id,
          logged_at: entry.logged_at,
          items_count: entry.items?.length || 0,
          items: entry.items
        });
      });
      
      // Lấy tất cả exercise_ids cần fetch
      const exerciseIds = new Set<number>();
      exerciseEntries.forEach((entry: any) => {
        if (entry.items && entry.items.length > 0) {
          entry.items.forEach((item: any) => {
            if (item.exercise_id) {
              exerciseIds.add(item.exercise_id);
            }
          });
        }
      });

      // Fetch thông tin exercises - Tối ưu: chỉ fetch nếu cần thiết
      // Backend đã trả về met_value_snapshot, có thể dùng luôn nếu có
      const exerciseMap = new Map<number, any>();
      console.log('Exercise IDs to fetch:', Array.from(exerciseIds));
      if (exerciseIds.size > 0) {
        try {
          // Batch fetch với Promise.all - giới hạn số lượng đồng thời
          const exerciseIdsArray = Array.from(exerciseIds);
          const batchSize = 10; // Fetch 10 exercises cùng lúc
          
          for (let i = 0; i < exerciseIdsArray.length; i += batchSize) {
            const batch = exerciseIdsArray.slice(i, i + batchSize);
            console.log(`Fetching exercise batch ${i / batchSize + 1}:`, batch);
            const exercisePromises = batch.map(async (exerciseId) => {
              try {
                const exerciseRes = await api.get(`/exercises/${exerciseId}`);
                exerciseMap.set(exerciseId, exerciseRes.data);
                console.log(`✓ Fetched exercise ${exerciseId}:`, exerciseRes.data.description);
              } catch (err) {
                console.error(`✗ Failed to fetch exercise ${exerciseId}:`, err);
              }
            });
            await Promise.all(exercisePromises);
          }
          console.log('Exercise map size:', exerciseMap.size);
        } catch (err) {
          console.error("Error fetching exercises:", err);
        }
      } else {
        console.warn('No exercise IDs to fetch!');
      }

      // Flatten items từ các entries thành danh sách logs
      const flattenedLogs: ExerciseLog[] = [];
      exerciseEntries.forEach((entry: any) => {
        if (entry.items && entry.items.length > 0) {
          entry.items.forEach((item: any) => {
            const exercise = exerciseMap.get(item.exercise_id);
            const logItem: ExerciseLog = {
              id: item.id, // item.id
              entry_id: entry.id, // entry.id - cần để xóa
              exercise: exercise ? {
                id: exercise.id,
                description: exercise.description || 'Unknown',
                major_heading: exercise.major_heading || '',
                met_value: exercise.met_value || item.met_value_snapshot || 0
              } : {
                id: item.exercise_id,
                description: 'Unknown',
                major_heading: '',
                met_value: item.met_value_snapshot || 0
              },
              duration_minutes: parseFloat(item.duration_min || 0),
              calories_burned: parseFloat(item.calories || 0),
              logged_at: entry.logged_at
            };
            flattenedLogs.push(logItem);
            console.log('Added log item:', logItem);
          });
        } else {
          console.warn('Entry has no items:', entry);
        }
      });
      
      console.log('Total flattened logs:', flattenedLogs.length);
      setAllLogs(flattenedLogs);
      // Áp dụng filter
      applyFilters(flattenedLogs, selectedMajorHeading);
      
      // Debug: log để kiểm tra
      console.log('=== END FETCH LOGS DEBUG ===');
    } catch (error) {
      console.error("Lỗi tải logs:", error);
      setAllLogs([]);
      setLogs([]);
    } finally {
      setLoading(false);
    }
  };

  // 2. Lọc logs theo major_heading
  const applyFilters = (logsToFilter: ExerciseLog[], majorHeading: string) => {
    let filtered = [...logsToFilter];
    
    // Filter theo major_heading
    if (majorHeading !== 'all') {
      filtered = filtered.filter(log => log.exercise.major_heading === majorHeading);
    }
    
    console.log('Applying filters - Total logs:', logsToFilter.length, 'Filtered:', filtered.length, 'Major heading:', majorHeading);
    setLogs(filtered);
  };

  // Lấy danh sách unique major_headings từ logs
  const getUniqueMajorHeadings = (): string[] => {
    const headings = new Set<string>();
    allLogs.forEach(log => {
      if (log.exercise.major_heading) {
        headings.add(log.exercise.major_heading);
      }
    });
    return Array.from(headings).sort();
  };

  // Sử dụng useRef để track lần mount đầu tiên và date đã fetch
  const isFirstMount = useRef(true);
  const lastFetchedDate = useRef<string | null>(null);
  
  // Fetch logs ngay khi component mount - Đảm bảo luôn load logs cho ngày hôm nay
  useEffect(() => {
    if (!isFirstMount.current) return; // Chỉ chạy lần đầu
    
    const today = new Date().toISOString().split('T')[0];
    // Fetch logs cho ngày hôm nay ngay khi component mount
    // Không phụ thuộc vào selectedDate ban đầu
    console.log('Component mounted, fetching logs for today:', today);
    lastFetchedDate.current = today;
    fetchLogs(today).catch(err => {
      console.error('Error fetching logs on mount:', err);
      lastFetchedDate.current = null; // Reset nếu lỗi
    });
    
    // Đánh dấu đã mount
    isFirstMount.current = false;
  }, []); // Chỉ chạy một lần khi mount

  // Khi selectedDateOption thay đổi, cập nhật selectedDate
  useEffect(() => {
    if (selectedDateOption !== 'custom') {
      const date = getDateFromOption(selectedDateOption);
      setSelectedDate(date);
    }
  }, [selectedDateOption]);

  // Fetch logs khi selectedDate thay đổi (KHÔNG phải lần mount đầu)
  useEffect(() => {
    // Skip nếu đây là lần mount đầu (đã fetch ở useEffect trên)
    if (isFirstMount.current) {
      return;
    }
    
    // Chỉ fetch nếu selectedDate thay đổi và chưa fetch cho date này
    if (selectedDate && selectedDate !== lastFetchedDate.current) {
      console.log('Selected date changed, fetching logs for:', selectedDate, '(last fetched:', lastFetchedDate.current, ')');
      lastFetchedDate.current = selectedDate;
      fetchLogs(selectedDate);
    } else {
      console.log('Skipping fetch - date unchanged or already fetched:', selectedDate, '(last fetched:', lastFetchedDate.current, ')');
    }
  }, [selectedDate]);

  // Khi chuyển sang tab "Tìm kiếm", tự động load exercises nếu chưa có - Tối ưu: lazy load
  useEffect(() => {
    if (activeMainTab === 'search' && !searchQuery.trim() && searchResults.length === 0 && !loading) {
      // Chỉ load khi user thực sự cần (không load ngay)
      // User có thể search hoặc click category để load
      // Hoặc load với limit nhỏ hơn
      const triggerSearch = async () => {
        setLoading(true);
        try {
          const params: any = { q: '', limit: 20 }; // Giảm từ 100 xuống 20 cho lần đầu
          if (searchMajorHeading !== 'all') {
            params.major_heading = searchMajorHeading;
          }
          const res = await api.get('/exercises/search', { params });
          setSearchResults(res.data.items || []);
        } catch (error) {
          console.error("Lỗi tải exercises:", error);
        } finally {
          setLoading(false);
        }
      };
      // Delay nhỏ để không block UI
      const timeoutId = setTimeout(triggerSearch, 300);
      return () => clearTimeout(timeoutId);
    }
  }, [activeMainTab]);

  // Khi major_heading filter thay đổi, áp dụng filter lại
  useEffect(() => {
    applyFilters(allLogs, selectedMajorHeading);
  }, [selectedMajorHeading]);

  // 2. Lấy danh sách tất cả major headings - Lazy load khi cần
  const fetchMajorHeadings = async () => {
    // Nếu đã có rồi, không fetch lại
    if (allMajorHeadings.length > 0) return;
    
    try {
      // Chỉ fetch với limit nhỏ để lấy sample, sau đó extract unique major_headings
      // Hoặc có thể extract từ logs hiện có trước
      const headingsFromLogs = new Set<string>();
      allLogs.forEach(log => {
        if (log.exercise.major_heading) {
          headingsFromLogs.add(log.exercise.major_heading);
        }
      });
      
      // Nếu đã có đủ từ logs, dùng luôn
      if (headingsFromLogs.size >= 5) {
        setAllMajorHeadings(Array.from(headingsFromLogs).sort());
        return;
      }
      
      // Nếu chưa đủ, fetch thêm từ API nhưng với limit nhỏ hơn
      const res = await api.get('/exercises/search', {
        params: { q: '', limit: 30 } // Giảm từ 100 xuống 30
      });
      res.data.items?.forEach((ex: any) => {
        if (ex.major_heading) {
          headingsFromLogs.add(ex.major_heading);
        }
      });
      setAllMajorHeadings(Array.from(headingsFromLogs).sort());
    } catch (error) {
      console.error("Lỗi lấy major headings:", error);
    }
  };

  // 3. Lấy bài tập gần đây (từ logs) - Tối ưu: dùng data từ logs thay vì fetch lại
  useEffect(() => {
    if (allLogs.length === 0) return;
    
    try {
      // Lấy exercise_ids từ logs gần đây (7 ngày) và dùng data đã có
      const today = new Date();
      const sevenDaysAgo = new Date(today);
      sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
      
      const recentExercisesMap = new Map<number, ExerciseSearchResult>();
      allLogs.forEach(log => {
        const logDate = new Date(log.logged_at);
        if (logDate >= sevenDaysAgo && log.exercise.id) {
          // Dùng data đã có từ logs thay vì fetch lại
          if (!recentExercisesMap.has(log.exercise.id)) {
            recentExercisesMap.set(log.exercise.id, {
              id: log.exercise.id,
              description: log.exercise.description,
              major_heading: log.exercise.major_heading,
              met_value: log.exercise.met_value
            });
          }
        }
      });
      
      // Chỉ fetch những exercises chưa có đầy đủ thông tin (nếu cần)
      const exercisesToFetch: number[] = [];
      Array.from(recentExercisesMap.values()).slice(0, 10).forEach(ex => {
        if (!ex.description || ex.description === 'Unknown') {
          exercisesToFetch.push(ex.id);
        }
      });
      
      // Chỉ fetch những cái cần thiết
      if (exercisesToFetch.length > 0) {
        const fetchPromises = exercisesToFetch.map(async (id) => {
          try {
            const res = await api.get(`/exercises/${id}`);
            recentExercisesMap.set(id, {
              id: res.data.id,
              description: res.data.description,
              major_heading: res.data.major_heading,
              met_value: res.data.met_value
            });
          } catch (err) {
            console.error(`Failed to fetch exercise ${id}:`, err);
          }
        });
        Promise.all(fetchPromises).then(() => {
          setRecentExercises(Array.from(recentExercisesMap.values()).slice(0, 10));
        });
      } else {
        setRecentExercises(Array.from(recentExercisesMap.values()).slice(0, 10));
      }
    } catch (error) {
      console.error("Lỗi lấy bài tập gần đây:", error);
    }
  }, [allLogs]);

  // 4. Xử lý tìm kiếm bài tập (Debounce đơn giản) - Tối ưu: giảm limit ban đầu
  useEffect(() => {
    const searchExercises = async () => {
      // Nếu có search query, tự động chuyển sang tab "Tìm kiếm"
      if (searchQuery.trim() && activeMainTab !== 'search') {
        setActiveMainTab('search');
      }

      // Chỉ search khi đang ở tab "Tìm kiếm" hoặc có search query
      if (activeMainTab !== 'search' && !searchQuery.trim()) {
        return;
      }

      setLoading(true);
      try {
        // Giảm limit ban đầu để load nhanh hơn, có thể load thêm sau
        const params: any = { limit: 30 }; // Giảm từ 100 xuống 30
        
        // Nếu có search query, thêm vào params
        if (searchQuery.trim()) {
          params.q = searchQuery;
        } else {
          // Nếu không có query nhưng đang ở tab search, search với q rỗng để lấy tất cả
          params.q = '';
        }
        
        // Nếu có filter major heading, thêm vào
        if (searchMajorHeading !== 'all') {
          params.major_heading = searchMajorHeading;
        }
        
        const res = await api.get('/exercises/search', { params });
        setSearchResults(res.data.items || []);
      } catch (error) {
        console.error("Lỗi tìm kiếm:", error);
      } finally {
        setLoading(false);
      }
    };

    const timeoutId = setTimeout(searchExercises, 500);
    return () => clearTimeout(timeoutId);
  }, [searchQuery, searchMajorHeading, activeMainTab]);

  // 5. Xử lý Log bài tập
  const handleLogExercise = async () => {
    if (!selectedExercise || !duration) return;
    
    setSubmitting(true);
    try {
      // Tạo datetime từ exerciseDate và thời gian hiện tại
      const exerciseDateTime = new Date(exerciseDate);
      exerciseDateTime.setHours(new Date().getHours());
      exerciseDateTime.setMinutes(new Date().getMinutes());
      
      // Gọi API POST /logs/exercise từ logs.py
      await api.post('/logs/exercise', {
        items: [
          {
            exercise_id: selectedExercise.id,
            duration_min: parseFloat(duration) // Backend yêu cầu duration_min, không phải duration_minutes
          }
        ],
        logged_at: exerciseDateTime.toISOString()
      });
      
      toast.success(`Đã thêm: ${selectedExercise.description}`);
      setSelectedExercise(null); // Đóng modal
      setSearchQuery(''); // Reset tìm kiếm
      
      // Refresh lại list với ngày mà bài tập được thêm vào (exerciseDate)
      // Nếu exerciseDate khác selectedDate, cập nhật selectedDate để hiển thị đúng
      if (exerciseDate !== selectedDate) {
        // Tìm option tương ứng với exerciseDate
        const today = new Date().toISOString().split('T')[0];
        const yesterday = new Date();
        yesterday.setDate(yesterday.getDate() - 1);
        const yesterdayStr = yesterday.toISOString().split('T')[0];
        const twoDaysAgo = new Date();
        twoDaysAgo.setDate(twoDaysAgo.getDate() - 2);
        const twoDaysAgoStr = twoDaysAgo.toISOString().split('T')[0];
        
        if (exerciseDate === today) {
          setSelectedDateOption('today');
          setSelectedDate(exerciseDate);
        } else if (exerciseDate === yesterdayStr) {
          setSelectedDateOption('yesterday');
          setSelectedDate(exerciseDate);
        } else if (exerciseDate === twoDaysAgoStr) {
          setSelectedDateOption('2days');
          setSelectedDate(exerciseDate);
        } else {
          setSelectedDateOption('custom');
          setCustomDate(exerciseDate);
          setSelectedDate(exerciseDate);
        }
      }
      
      await fetchLogs(exerciseDate);
      
      // Reset exerciseDate về hôm nay sau khi thêm
      setExerciseDate(new Date().toISOString().split('T')[0]);
      
      // Trigger refresh summary ở dashboard bằng cách dispatch custom event
      window.dispatchEvent(new CustomEvent('refreshDashboard'));
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Không thể lưu bài tập');
    } finally {
      setSubmitting(false);
    }
  };

  // 6. Xử lý xóa bài tập
  const handleDeleteExercise = async (entryId: number, exerciseName: string) => {
    if (!confirm(`Bạn có chắc muốn xóa "${exerciseName}"?`)) {
      return;
    }

    try {
      await LogService.deleteExerciseLog(entryId);
      toast.success('Đã xóa bài tập');
      await fetchLogs(selectedDate); // Refresh lại list với ngày hiện tại
      
      // Trigger refresh summary ở dashboard
      window.dispatchEvent(new CustomEvent('refreshDashboard'));
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Không thể xóa bài tập');
    }
  };

  // Helper để tính ngày dựa trên option
  const getDateFromOption = (option: string): string => {
    switch (option) {
      case 'today':
        return getLocalDateString();
      case 'yesterday':
        return getDaysAgoDateString(1);
      case '2days':
        return getDaysAgoDateString(2);
      case 'custom':
        return customDate || getLocalDateString();
      default:
        return getLocalDateString();
    }
  };

  // Helper tính độ nặng nhẹ dựa trên MET
  const getIntensity = (met: number) => {
    if (met < 3) return { label: 'Nhẹ', color: 'bg-green-100 text-green-700' };
    if (met < 6) return { label: 'Trung bình', color: 'bg-yellow-100 text-yellow-700' };
    return { label: 'Cao', color: 'bg-red-100 text-red-700' };
  };

  // Xử lý khi thay đổi date option
  const handleDateOptionChange = (option: string) => {
    setSelectedDateOption(option);
    if (option === 'custom') {
      // Nếu chọn custom, mở date picker với ngày hiện tại
      setCustomDate(selectedDate);
    } else {
      const date = getDateFromOption(option);
      setSelectedDate(date);
    }
  };

  // Xử lý khi thay đổi custom date
  const handleCustomDateChange = (date: string) => {
    setCustomDate(date);
    setSelectedDate(date);
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Tập luyện</h2>
      </div>

      {/* Search Bar - Dùng chung cho cả 2 tab */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-gray-400" />
        <Input
          id="exercise-search"
          placeholder={activeMainTab === 'search' ? "Tìm kiếm bài tập..." : "Thêm mới bài tập (Chạy bộ, Gym, Yoga...)"}
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="pl-10"
        />
        {loading && (
          <div className="absolute right-3 top-1/2 -translate-y-1/2">
            <Loader2 className="size-4 animate-spin text-gray-400" />
          </div>
        )}
      </div>

      {/* Tabs: Chuyển đổi giữa Kết quả tìm kiếm và Lịch sử */}
      <Tabs value={activeMainTab} onValueChange={(v) => setActiveMainTab(v as 'history' | 'search')} className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger 
              value="history" 
              onClick={() => { 
                // Không clear search query khi chuyển tab, để giữ lại cho lần sau
              }}
            >
              Lịch sử tập luyện
            </TabsTrigger>
            <TabsTrigger 
              value="search"
              onClick={() => {
                // Focus vào search input khi chuyển sang tab tìm kiếm
                setTimeout(() => {
                  document.getElementById('exercise-search')?.focus();
                }, 100);
              }}
            >
              Tìm kiếm
            </TabsTrigger>
          </TabsList>

        {/* Tab 1: Lịch sử Log (Dữ liệu từ API /logs/daily) */}
        <TabsContent value="history" className="space-y-3 mt-4">
          {/* Filters: Date và Major Heading - Đặt trong tab Lịch sử */}
          <div className="flex gap-3 items-center pb-3 border-b flex-wrap">
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
                  value={customDate || selectedDate}
                  onChange={(e) => handleCustomDateChange(e.target.value)}
                  className="w-auto"
                />
              )}
            </div>

            {/* Major Heading Filter */}
            <Select value={selectedMajorHeading} onValueChange={setSelectedMajorHeading}>
              <SelectTrigger className="w-[200px]">
                <SelectValue placeholder="Tất cả nhóm bài tập" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tất cả nhóm bài tập</SelectItem>
                {getUniqueMajorHeadings().map((heading) => (
                  <SelectItem key={heading} value={heading}>
                    {heading}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {loading ? (
            <div className="text-center py-12">
              <Loader2 className="size-8 animate-spin text-pink-600 mx-auto mb-3" />
              <p className="text-gray-500">Đang tải dữ liệu...</p>
            </div>
          ) : logs.length === 0 ? (
            <div className="text-center py-12 bg-gray-50 rounded-lg border border-dashed">
              <Dumbbell className="size-10 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-500">
                {selectedDate === new Date().toISOString().split('T')[0] 
                  ? 'Hôm nay chưa tập gì cả.' 
                  : `Ngày ${new Date(selectedDate).toLocaleDateString('vi-VN')} chưa có dữ liệu tập luyện.`}
              </p>
              <Button variant="link" onClick={() => document.getElementById('exercise-search')?.focus()}>
                Bắt đầu ngay
              </Button>
            </div>
          ) : (
            logs.map((log) => {
              const intensity = getIntensity(log.exercise.met_value);
              return (
                <Card key={log.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-4">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-start gap-2 mb-1">
                          <h3 className="font-semibold">{log.exercise.description}</h3>
                          <Badge variant="outline" className={`text-[10px] border-none ${intensity.color}`}>
                            {intensity.label}
                          </Badge>
                        </div>
                        <div className="flex items-center gap-3 text-sm text-gray-600">
                          <span className="flex items-center gap-1">
                            <Clock className="size-3" />
                            {log.duration_minutes} phút
                          </span>
                          <span>•</span>
                          <span className="text-xs bg-gray-100 px-2 py-0.5 rounded">
                            {log.exercise.major_heading}
                          </span>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <div className="text-right">
                          <p className="text-lg font-bold text-orange-600 flex items-center justify-end gap-1">
                            <Flame className="size-4 fill-orange-600" />
                            {Math.round(log.calories_burned)}
                          </p>
                          <p className="text-xs text-gray-400">kcal</p>
                        </div>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="text-red-500 hover:text-red-700 hover:bg-red-50"
                          onClick={() => handleDeleteExercise(log.entry_id, log.exercise.description)}
                          title="Xóa bài tập"
                        >
                          <Trash2 className="size-4" />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })
          )}
        </TabsContent>

        {/* Tab 2: Tìm kiếm bài tập */}
        <TabsContent value="search" className="space-y-4 mt-4">
          {/* Filter major heading - Chỉ hiển thị khi ở tab search */}
          <div className="flex gap-2 items-center">
            <Filter className="size-4 text-gray-500" />
            <Select 
              value={searchMajorHeading} 
              onValueChange={setSearchMajorHeading}
              onOpenChange={(open) => {
                // Lazy load major headings khi mở dropdown
                if (open && allMajorHeadings.length === 0) {
                  fetchMajorHeadings();
                }
              }}
            >
              <SelectTrigger className="w-[200px]">
                <SelectValue placeholder="Tất cả nhóm" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tất cả nhóm</SelectItem>
                {allMajorHeadings.length > 0 ? (
                  allMajorHeadings.map((heading) => (
                    <SelectItem key={heading} value={heading}>
                      {heading}
                    </SelectItem>
                  ))
                ) : (
                  <SelectItem value="loading" disabled>Đang tải...</SelectItem>
                )}
              </SelectContent>
            </Select>
          </div>

          {/* Tabs: Most Recent và Browse All */}
          <Tabs value={searchTab} onValueChange={(v) => setSearchTab(v as 'recent' | 'browse')} className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="recent">Gần đây</TabsTrigger>
              <TabsTrigger value="browse">Duyệt tất cả</TabsTrigger>
            </TabsList>

            {/* Tab: Gần đây */}
            <TabsContent value="recent" className="mt-4">
              {/* Luôn hiển thị kết quả tìm kiếm nếu có, nếu không thì hiển thị bài tập gần đây */}
              {searchResults.length > 0 ? (
                // Hiển thị kết quả tìm kiếm
                <div className="space-y-2">
                  {searchResults.map((ex) => (
                    <Card 
                      key={ex.id} 
                      className="hover:border-blue-500 cursor-pointer transition-colors"
                      onClick={() => setSelectedExercise(ex)}
                    >
                      <CardContent className="p-4 flex justify-between items-center">
                        <div>
                          <h3 className="font-semibold">{ex.description}</h3>
                          <p className="text-sm text-gray-500">{ex.major_heading}</p>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge variant="secondary">MET: {ex.met_value}</Badge>
                          <Plus className="size-4 text-blue-600" />
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                  {loading && (
                    <div className="text-center py-4">
                      <Loader2 className="size-5 animate-spin text-pink-600 mx-auto" />
                    </div>
                  )}
                </div>
              ) : !loading ? (
                // Nếu không có kết quả và không đang loading, hiển thị bài tập gần đây
                <div className="space-y-2">
                  {recentExercises.length > 0 ? (
                    recentExercises.map((ex) => (
                      <Card 
                        key={ex.id} 
                        className="hover:border-blue-500 cursor-pointer transition-colors"
                        onClick={() => setSelectedExercise(ex)}
                      >
                        <CardContent className="p-4 flex justify-between items-center">
                          <div>
                            <h3 className="font-semibold">{ex.description}</h3>
                            <p className="text-sm text-gray-500">{ex.major_heading}</p>
                          </div>
                          <div className="flex items-center gap-2">
                            <Badge variant="secondary">MET: {ex.met_value}</Badge>
                            <Plus className="size-4 text-blue-600" />
                          </div>
                        </CardContent>
                      </Card>
                    ))
                  ) : (
                    <div className="text-center py-8 text-gray-500">
                      Chưa có bài tập gần đây. Hãy tìm kiếm để thêm bài tập mới.
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Loader2 className="size-6 animate-spin text-pink-600 mx-auto mb-2" />
                  <p className="text-gray-500">Đang tải...</p>
                </div>
              )}
            </TabsContent>

            {/* Tab: Duyệt tất cả - Grid categories hoặc search results */}
            <TabsContent value="browse" className="mt-4">
              {searchResults.length > 0 ? (
                // Nếu có results (từ search hoặc category click), hiển thị kết quả
                <div className="space-y-2">
                  {searchResults.map((ex) => (
                    <Card 
                      key={ex.id} 
                      className="hover:border-blue-500 cursor-pointer transition-colors"
                      onClick={() => setSelectedExercise(ex)}
                    >
                      <CardContent className="p-4 flex justify-between items-center">
                        <div>
                          <h3 className="font-semibold">{ex.description}</h3>
                          <p className="text-sm text-gray-500">{ex.major_heading}</p>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge variant="secondary">MET: {ex.met_value}</Badge>
                          <Plus className="size-4 text-blue-600" />
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                  {loading && (
                    <div className="text-center py-4">
                      <Loader2 className="size-5 animate-spin text-pink-600 mx-auto" />
                    </div>
                  )}
                </div>
              ) : !loading ? (
                // Nếu không có results và không đang loading, hiển thị grid categories
                <div className="grid grid-cols-3 gap-4">
                  {allMajorHeadings.length > 0 ? (
                    allMajorHeadings.map((heading) => (
                      <Card
                        key={heading}
                        className="hover:border-blue-500 cursor-pointer transition-colors h-24 flex items-center justify-center"
                        onClick={async () => {
                          setSearchMajorHeading(heading);
                          setSearchQuery('');
                          setLoading(true);
                          try {
                            // Fetch exercises trong category này
                            const res = await api.get('/exercises/search', {
                              params: { q: '', major_heading: heading, limit: 50 }
                            });
                            setSearchResults(res.data.items || []);
                            // Đảm bảo đang ở tab search
                            setActiveMainTab('search');
                          } catch (error) {
                            console.error("Lỗi tải exercises:", error);
                          } finally {
                            setLoading(false);
                          }
                        }}
                      >
                        <CardContent className="p-4 text-center">
                          <p className="font-semibold text-sm">{heading}</p>
                        </CardContent>
                      </Card>
                    ))
                  ) : (
                    <div className="col-span-3 text-center py-8 text-gray-500">
                      Đang tải danh mục...
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Loader2 className="size-6 animate-spin text-pink-600 mx-auto mb-2" />
                  <p className="text-gray-500">Đang tải...</p>
                </div>
              )}
            </TabsContent>
          </Tabs>
        </TabsContent>
      </Tabs>

      {/* Dialog nhập thời gian tập */}
      <Dialog open={!!selectedExercise} onOpenChange={(open) => {
        if (!open) {
          setSelectedExercise(null);
          // Reset exerciseDate về hôm nay khi đóng dialog
          setExerciseDate(new Date().toISOString().split('T')[0]);
        }
      }}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Ghi nhận hoạt động</DialogTitle>
          </DialogHeader>
          
          <div className="space-y-4 py-4">
            <div className="p-4 bg-blue-50 rounded-lg">
              <h4 className="font-semibold text-blue-900">{selectedExercise?.description}</h4>
              <p className="text-sm text-blue-700 mt-1">
                 Cường độ (MET): {selectedExercise?.met_value}
              </p>
            </div>

            <div className="space-y-2">
              <Label>Ngày tập luyện</Label>
              <div className="flex items-center gap-2">
                <Calendar className="size-4 text-gray-500" />
                <Input
                  type="date"
                  value={exerciseDate}
                  onChange={(e) => setExerciseDate(e.target.value)}
                  className="flex-1"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label>Thời gian tập (phút)</Label>
              <div className="flex items-center gap-2">
                <Input 
                  type="number" 
                  value={duration} 
                  onChange={(e) => setDuration(e.target.value)}
                  min="1"
                  className="text-lg"
                />
                <span className="text-gray-500 font-medium">phút</span>
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button variant="ghost" onClick={() => setSelectedExercise(null)}>Hủy</Button>
            <Button onClick={handleLogExercise} disabled={submitting}>
              {submitting ? <Loader2 className="animate-spin mr-2" /> : 'Lưu lại'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}