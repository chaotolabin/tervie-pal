import React, { useState, useEffect } from 'react';
import { Search, Dumbbell, Heart, Zap, Target, Flame, Loader2, Clock, Info } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Input } from '../ui/input';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '../ui/dialog';
import { Label } from '../ui/label';
import { toast } from 'sonner';
import api from '../lib/api';

// Định nghĩa Interface khớp với Backend response
interface Exercise {
  id: number;
  description: string;   // Backend dùng description làm tên bài tập
  major_heading: string; // Backend dùng major_heading làm category
  met_value: number;
}

// Danh mục filter (Hardcode để làm UI, map vào parameter major_heading)
const categories = [
  { id: 'all', label: 'Tất cả', icon: Dumbbell },
  { id: 'Running', label: 'Chạy bộ', icon: Heart },
  { id: 'Bicycling', label: 'Đạp xe', icon: Zap },
  { id: 'Conditioning', label: 'Thể lực', icon: Target },
  { id: 'Sports', label: 'Thể thao', icon: Flame },
];

export default function ExerciseLibraryPage() {
  // State dữ liệu
  const [exercises, setExercises] = useState<Exercise[]>([]);
  const [loading, setLoading] = useState(false);

  // State UI & Filter
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  
  // State Modal Detail & Log
  const [selectedExercise, setSelectedExercise] = useState<Exercise | null>(null);
  const [duration, setDuration] = useState<string>('30');
  const [logging, setLogging] = useState(false);

  // Fetch dữ liệu từ API
  useEffect(() => {
    const fetchExercises = async () => {
      setLoading(true);
      try {
        const params: any = { 
          q: searchQuery || '', 
          limit: 50 
        };
        
        // Nếu chọn category cụ thể, gửi lên backend
        if (selectedCategory !== 'all') {
          params.major_heading = selectedCategory;
        }

        // Gọi API /exercises/search từ exercise.py
        const res = await api.get('/exercises/search', { params });
        setExercises(res.data.items || []);
      } catch (error) {
        console.error("Lỗi tải bài tập:", error);
        toast.error("Không thể tải danh sách bài tập");
      } finally {
        setLoading(false);
      }
    };

    // Debounce search để tránh gọi API liên tục khi gõ
    const timeoutId = setTimeout(fetchExercises, 500);
    return () => clearTimeout(timeoutId);
  }, [searchQuery, selectedCategory]);

  // Hàm tính độ khó dựa trên MET (Logic Frontend tự quy định)
  const getDifficultyInfo = (met: number) => {
    if (met < 3) return { label: 'Nhẹ', color: 'bg-green-100 text-green-700' };
    if (met < 6) return { label: 'Trung bình', color: 'bg-yellow-100 text-yellow-700' };
    if (met < 9) return { label: 'Cao', color: 'bg-orange-100 text-orange-700' };
    return { label: 'Rất cao', color: 'bg-red-100 text-red-700' };
  };

  // Hàm ước tính Calo cho người 70kg (Công thức: MET * 3.5 * weight / 200)
  const estimateCalories = (met: number) => {
    return Math.round((met * 3.5 * 70) / 200);
  };

  // Hàm Log bài tập vào nhật ký
  const handleAddToLog = async () => {
    if (!selectedExercise || !duration) return;
    
    setLogging(true);
    try {
      await api.post('/logs/exercise', {
        items: [{
          exercise_id: selectedExercise.id,
          duration_min: parseFloat(duration) // Backend yêu cầu duration_min, không phải duration_minutes
        }],
        logged_at: new Date().toISOString()
      });
      
      toast.success(`Đã thêm "${selectedExercise.description}" vào nhật ký`);
      setSelectedExercise(null); // Đóng modal
    } catch (error) {
      toast.error("Lỗi khi lưu bài tập");
    } finally {
      setLogging(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold">Thư viện bài tập</h2>
          <p className="text-gray-600">Khám phá danh sách bài tập từ cơ sở dữ liệu chuẩn</p>
        </div>
      </div>

      {/* Search Bar */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-gray-400" />
        <Input
          placeholder="Tìm kiếm bài tập (Ví dụ: Running, Yoga...)"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="pl-10"
        />
      </div>

      {/* Category Tabs */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        {categories.map((category) => {
          const Icon = category.icon;
          const isActive = selectedCategory === category.id;
          return (
            <button
              key={category.id}
              onClick={() => setSelectedCategory(category.id)}
              className={`p-4 rounded-lg border-2 transition-all flex flex-col items-center justify-center gap-2 ${
                isActive
                  ? 'border-pink-500 bg-pink-50 text-pink-700'
                  : 'border-gray-200 hover:border-pink-300 text-gray-600'
              }`}
            >
              <Icon className={`size-6 ${isActive ? 'text-pink-600' : 'text-gray-400'}`} />
              <span className="font-semibold text-sm">{category.label}</span>
            </button>
          );
        })}
      </div>

      {/* Exercise Grid */}
      {loading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="size-8 animate-spin text-pink-600" />
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {exercises.map((exercise) => {
            const difficulty = getDifficultyInfo(exercise.met_value);
            return (
              <Card 
                key={exercise.id} 
                className="cursor-pointer hover:shadow-lg transition-shadow group"
                onClick={() => setSelectedExercise(exercise)}
              >
                <CardHeader className="pb-2">
                  <div className="flex justify-between items-start gap-2">
                    <CardTitle className="text-lg leading-tight group-hover:text-pink-600 transition-colors">
                      {exercise.description}
                    </CardTitle>
                  </div>
                  <div className="flex items-center gap-2 mt-2">
                    <Badge variant="outline">{exercise.major_heading || 'General'}</Badge>
                    <Badge className={`${difficulty.color} hover:${difficulty.color} border-none`}>
                      {difficulty.label}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between pt-3 border-t mt-2">
                    <div className="flex items-center gap-1 text-gray-500 text-sm">
                      <Zap className="size-4 text-yellow-500" />
                      <span>MET: <strong>{exercise.met_value}</strong></span>
                    </div>
                    <div className="flex items-center gap-1 text-pink-600 text-sm font-medium">
                      <Flame className="size-4" />
                      ~{estimateCalories(exercise.met_value)} kcal/phút
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      {!loading && exercises.length === 0 && (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <p className="text-gray-600">Không tìm thấy bài tập nào phù hợp với từ khóa "{searchQuery}"</p>
        </div>
      )}

      {/* Exercise Detail & Log Dialog */}
      <Dialog open={!!selectedExercise} onOpenChange={(open) => !open && setSelectedExercise(null)}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="text-xl pr-8 line-clamp-2">
              {selectedExercise?.description}
            </DialogTitle>
          </DialogHeader>
          
          {selectedExercise && (
            <div className="space-y-6 py-2">
              {/* Info Cards */}
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-pink-50 p-4 rounded-xl flex flex-col items-center text-center">
                  <Flame className="size-6 text-pink-600 mb-2" />
                  <span className="text-xs text-gray-500 uppercase font-bold">Tiêu hao (Ước tính)</span>
                  <span className="text-lg font-bold text-pink-700">
                    ~{estimateCalories(selectedExercise.met_value)} kcal/phút
                  </span>
                  <span className="text-[10px] text-gray-400 mt-1">(Cho người 70kg)</span>
                </div>
                <div className="bg-blue-50 p-4 rounded-xl flex flex-col items-center text-center">
                  <Zap className="size-6 text-blue-600 mb-2" />
                  <span className="text-xs text-gray-500 uppercase font-bold">Cường độ (MET)</span>
                  <span className="text-lg font-bold text-blue-700">{selectedExercise.met_value}</span>
                  <Badge className={`mt-1 ${getDifficultyInfo(selectedExercise.met_value).color} border-none`}>
                    {getDifficultyInfo(selectedExercise.met_value).label}
                  </Badge>
                </div>
              </div>

              {/* Input Duration */}
              <div className="space-y-3">
                <Label className="text-base">Thời gian tập luyện</Label>
                <div className="flex items-center gap-3">
                  <div className="relative flex-1">
                    <Clock className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-gray-400" />
                    <Input 
                      type="number" 
                      value={duration} 
                      onChange={(e) => setDuration(e.target.value)}
                      className="pl-10 text-lg"
                      min="1"
                    />
                  </div>
                  <span className="text-gray-500 font-medium whitespace-nowrap">phút</span>
                </div>
                
                {/* Calculated Total */}
                <div className="flex items-center gap-2 text-sm text-gray-600 bg-gray-50 p-3 rounded-lg">
                  <Info className="size-4" />
                  Tổng tiêu hao dự kiến: 
                  <strong className="text-gray-900">
                    {Math.round(estimateCalories(selectedExercise.met_value) * (parseInt(duration) || 0))} kcal
                  </strong>
                </div>
              </div>

              <DialogFooter>
                <Button className="w-full bg-gradient-to-r from-pink-500 to-purple-600 h-12 text-lg" onClick={handleAddToLog} disabled={logging}>
                  {logging ? <Loader2 className="animate-spin mr-2"/> : <PlusIcon />}
                  Thêm vào nhật ký
                </Button>
              </DialogFooter>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}

function PlusIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mr-2"><path d="M5 12h14"/><path d="M12 5v14"/></svg>
  )
}