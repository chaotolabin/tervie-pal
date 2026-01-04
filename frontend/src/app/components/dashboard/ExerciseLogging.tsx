import React, { useState, useEffect } from 'react';
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
  
  // State UI
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  
  // State cho filter
  const [selectedDate, setSelectedDate] = useState<string>(new Date().toISOString().split('T')[0]);
  const [selectedDateOption, setSelectedDateOption] = useState<string>('today'); // 'today', 'yesterday', '2days', 'custom'
  const [customDate, setCustomDate] = useState<string>(''); // Cho custom date picker
  const [selectedMajorHeading, setSelectedMajorHeading] = useState<string>('all');
  
  // State cho Dialog thêm bài tập
  const [selectedExercise, setSelectedExercise] = useState<ExerciseSearchResult | null>(null);
  const [duration, setDuration] = useState<string>('30');
  const [exerciseDate, setExerciseDate] = useState<string>(new Date().toISOString().split('T')[0]); // Ngày để thêm bài tập
  const [submitting, setSubmitting] = useState(false);

  // 1. Tải lịch sử tập luyện theo ngày
  const fetchLogs = async (date: string) => {
    try {
      setLoading(true);
      // Sử dụng /logs/daily để lấy cả exercise_logs, không phải /logs/summary
      const res = await api.get(`/logs/daily/${date}`);
      // Backend trả về logs trong object exercise_logs với items bên trong
      const exerciseEntries = res.data.exercise_logs || [];
      
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

      // Fetch thông tin exercises một lần
      const exerciseMap = new Map<number, any>();
      if (exerciseIds.size > 0) {
        try {
          // Fetch từng exercise (có thể tối ưu bằng cách tạo endpoint batch)
          const exercisePromises = Array.from(exerciseIds).map(async (exerciseId) => {
            try {
              const exerciseRes = await api.get(`/exercises/${exerciseId}`);
              exerciseMap.set(exerciseId, exerciseRes.data);
            } catch (err) {
              console.error(`Failed to fetch exercise ${exerciseId}:`, err);
            }
          });
          await Promise.all(exercisePromises);
        } catch (err) {
          console.error("Error fetching exercises:", err);
        }
      }

      // Flatten items từ các entries thành danh sách logs
      const flattenedLogs: ExerciseLog[] = [];
      exerciseEntries.forEach((entry: any) => {
        if (entry.items && entry.items.length > 0) {
          entry.items.forEach((item: any) => {
            const exercise = exerciseMap.get(item.exercise_id);
            flattenedLogs.push({
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
            });
          });
        }
      });
      setAllLogs(flattenedLogs);
      // Áp dụng filter
      applyFilters(flattenedLogs, selectedMajorHeading);
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

  useEffect(() => {
    fetchLogs(selectedDate);
  }, [selectedDate]);

  // Khi major_heading filter thay đổi, áp dụng filter lại
  useEffect(() => {
    applyFilters(allLogs, selectedMajorHeading);
  }, [selectedMajorHeading]);

  // 2. Xử lý tìm kiếm bài tập (Debounce đơn giản)
  useEffect(() => {
    const searchExercises = async () => {
      if (!searchQuery.trim()) {
        setSearchResults([]);
        setIsSearching(false);
        return;
      }

      setIsSearching(true);
      setLoading(true);
      try {
        const res = await api.get('/exercises/search', {
          params: { q: searchQuery, limit: 10 }
        });
        setSearchResults(res.data.items || []);
      } catch (error) {
        console.error("Lỗi tìm kiếm:", error);
      } finally {
        setLoading(false);
      }
    };

    const timeoutId = setTimeout(searchExercises, 500);
    return () => clearTimeout(timeoutId);
  }, [searchQuery]);

  // 3. Xử lý Log bài tập
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
      // Reset exerciseDate về hôm nay sau khi thêm
      setExerciseDate(new Date().toISOString().split('T')[0]);
      // Refresh lại list với ngày đã chọn (có thể là ngày khác hôm nay)
      await fetchLogs(selectedDate);
      
      // Trigger refresh summary ở dashboard bằng cách dispatch custom event
      window.dispatchEvent(new CustomEvent('refreshDashboard'));
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Không thể lưu bài tập');
    } finally {
      setSubmitting(false);
    }
  };

  // 4. Xử lý xóa bài tập
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

  // Helper tính độ nặng nhẹ dựa trên MET
  const getIntensity = (met: number) => {
    if (met < 3) return { label: 'Nhẹ', color: 'bg-green-100 text-green-700' };
    if (met < 6) return { label: 'Trung bình', color: 'bg-yellow-100 text-yellow-700' };
    return { label: 'Cao', color: 'bg-red-100 text-red-700' };
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Tập luyện</h2>
        <Button onClick={() => document.getElementById('exercise-search')?.focus()}>
          <Plus className="size-4 mr-2" />
          Thêm mới
        </Button>
      </div>

      {/* Search Bar */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-gray-400" />
        <Input
          id="exercise-search"
          placeholder="Thêm mới bài tập (Chạy bộ, Gym, Yoga...)"
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
      <Tabs defaultValue="history" value={isSearching ? 'search' : 'history'} className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="history" onClick={() => { setSearchQuery(''); setIsSearching(false); }}>
            Lịch sử tập luyện
          </TabsTrigger>
          <TabsTrigger value="search">Tìm kiếm</TabsTrigger>
        </TabsList>

        {/* Tab 1: Lịch sử Log (Dữ liệu từ API /logs/daily) */}
        <TabsContent value="history" className="space-y-3 mt-4">
          {/* Filters: Date và Major Heading - Đặt trong tab Lịch sử */}
          <div className="flex gap-3 items-center pb-3 border-b">
            {/* Date Picker */}
            <div className="flex items-center gap-2">
              <Calendar className="size-4 text-gray-500" />
              <Input
                type="date"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                className="w-auto"
              />
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

        {/* Tab 2: Kết quả tìm kiếm (Dữ liệu từ API /exercises/search) */}
        <TabsContent value="search" className="space-y-3 mt-4">
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
          {searchQuery && searchResults.length === 0 && !loading && (
            <div className="text-center py-8 text-gray-500">
              Không tìm thấy bài tập nào phù hợp.
            </div>
          )}
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