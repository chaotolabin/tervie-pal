import { useState, useEffect } from 'react';
import { Search, Plus, Filter, Clock, Flame, Dumbbell, Loader2 } from 'lucide-react';
import { Input } from '../ui/input';
import { Button } from '../ui/button';
import { Card, CardContent } from '../ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Badge } from '../ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '../ui/dialog';
import { Label } from '../ui/label';
import { toast } from 'sonner';
import api from '../lib/api';

// --- Interfaces khớp với Backend ---
interface ExerciseLog {
  id: number;
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
  const [searchResults, setSearchResults] = useState<ExerciseSearchResult[]>([]);
  
  // State UI
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  
  // State cho Dialog thêm bài tập
  const [selectedExercise, setSelectedExercise] = useState<ExerciseSearchResult | null>(null);
  const [duration, setDuration] = useState<string>('30');
  const [submitting, setSubmitting] = useState(false);

  // 1. Tải lịch sử tập luyện hôm nay
  const fetchTodayLogs = async () => {
    try {
      const today = new Date().toISOString().split('T')[0];
      const res = await api.get(`/logs/summary/${today}`);
      // Backend trả về logs trong object exercise_logs
      setLogs(res.data.exercise_logs || []);
    } catch (error) {
      console.error("Lỗi tải logs:", error);
    }
  };

  useEffect(() => {
    fetchTodayLogs();
  }, []);

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
      // Gọi API POST /logs/exercise từ logs.py
      await api.post('/logs/exercise', {
        items: [
          {
            exercise_id: selectedExercise.id,
            duration_minutes: parseInt(duration)
          }
        ],
        logged_at: new Date().toISOString()
      });
      
      toast.success(`Đã thêm: ${selectedExercise.description}`);
      setSelectedExercise(null); // Đóng modal
      setSearchQuery(''); // Reset tìm kiếm
      fetchTodayLogs(); // Refresh lại list
    } catch (error) {
      toast.error('Không thể lưu bài tập');
    } finally {
      setSubmitting(false);
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
      <div className="flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-gray-400" />
          <Input
            id="exercise-search"
            placeholder="Tìm kiếm bài tập (Chạy bộ, Gym, Yoga...)"
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
        <Button variant="outline" size="icon">
          <Filter className="size-4" />
        </Button>
      </div>

      {/* Tabs: Chuyển đổi giữa Kết quả tìm kiếm và Lịch sử */}
      <Tabs defaultValue="history" value={isSearching ? 'search' : 'history'} className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="history" onClick={() => { setSearchQuery(''); setIsSearching(false); }}>
            Lịch sử hôm nay
          </TabsTrigger>
          <TabsTrigger value="search">Tìm kiếm</TabsTrigger>
        </TabsList>

        {/* Tab 1: Lịch sử Log (Dữ liệu từ API /logs/summary) */}
        <TabsContent value="history" className="space-y-3 mt-4">
          {logs.length === 0 ? (
            <div className="text-center py-12 bg-gray-50 rounded-lg border border-dashed">
              <Dumbbell className="size-10 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-500">Hôm nay chưa tập gì cả.</p>
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
                      <div className="text-right">
                        <p className="text-lg font-bold text-orange-600 flex items-center justify-end gap-1">
                          <Flame className="size-4 fill-orange-600" />
                          {Math.round(log.calories_burned)}
                        </p>
                        <p className="text-xs text-gray-400">kcal</p>
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
      <Dialog open={!!selectedExercise} onOpenChange={(open) => !open && setSelectedExercise(null)}>
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