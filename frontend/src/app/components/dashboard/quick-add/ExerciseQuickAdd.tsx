import React, { useState, useEffect } from 'react';
import api from '../../lib/api';
import { toast } from 'sonner';
import { Search, Plus, Loader2 } from 'lucide-react';

interface ExerciseQuickAddProps {
  onClose?: () => void;
}

export default function ExerciseQuickAdd({ onClose }: ExerciseQuickAddProps) {
  const [exerciseSearch, setExerciseSearch] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedExercise, setSelectedExercise] = useState<any | null>(null);
  const [duration, setDuration] = useState('30');
  const [submitting, setSubmitting] = useState(false);

  // Tìm kiếm bài tập
  useEffect(() => {
    if (!exerciseSearch.trim()) {
      setSearchResults([]);
      return;
    }

    const searchExercises = async () => {
      setLoading(true);
      try {
        const res = await api.get('/exercises/search', {
          params: { q: exerciseSearch, limit: 10 }
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
  }, [exerciseSearch]);

  const handleAddExercise = async () => {
    if (!selectedExercise || !duration) return;
    
    setSubmitting(true);
    try {
      // Gọi API logExercise khớp với logs.py - cần items array
      await api.post('/logs/exercise', {
        items: [
          {
            exercise_id: selectedExercise.id,
            duration_min: parseFloat(duration) // Backend yêu cầu duration_min, không phải duration_minutes
          }
        ],
        logged_at: new Date().toISOString()
      });
      toast.success(`Đã thêm: ${selectedExercise.description}`);
      if (onClose) onClose();
      
      // Trigger refresh summary và streak ở dashboard
      window.dispatchEvent(new CustomEvent('refreshDashboard'));
      window.dispatchEvent(new CustomEvent('refreshStreak'));
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Không thể lưu bài tập');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="p-4 space-y-4">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-gray-400" />
        <input 
          type="text" 
          placeholder="Tìm bài tập (Chạy bộ, Gym...)" 
          className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
          value={exerciseSearch}
          onChange={(e) => setExerciseSearch(e.target.value)}
        />
        {loading && (
          <Loader2 className="absolute right-3 top-1/2 -translate-y-1/2 size-4 animate-spin text-gray-400" />
        )}
      </div>

      {/* Danh sách kết quả */}
      {searchResults.length > 0 && (
        <div className="space-y-2 max-h-60 overflow-y-auto">
          {searchResults.map((ex) => (
            <div
              key={ex.id}
              className="flex justify-between items-center p-3 hover:bg-gray-50 border rounded cursor-pointer"
              onClick={() => setSelectedExercise(ex)}
            >
              <div>
                <p className="font-medium">{ex.description}</p>
                <p className="text-xs text-gray-500">{ex.major_heading}</p>
              </div>
              <Plus className="size-4 text-blue-600" />
            </div>
          ))}
        </div>
      )}

      {/* Dialog nhập thời gian nếu đã chọn bài tập */}
      {selectedExercise && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={() => setSelectedExercise(null)}>
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4" onClick={(e) => e.stopPropagation()}>
            <h3 className="font-semibold text-lg mb-4">Ghi nhận hoạt động</h3>
            <div className="space-y-4">
              <div className="p-4 bg-blue-50 rounded-lg">
                <h4 className="font-semibold text-blue-900">{selectedExercise.description}</h4>
                <p className="text-sm text-blue-700 mt-1">Cường độ (MET): {selectedExercise.met_value}</p>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Thời gian tập (phút)</label>
                <input
                  type="number"
                  value={duration}
                  onChange={(e) => setDuration(e.target.value)}
                  min="1"
                  className="w-full border rounded-lg px-4 py-2"
                />
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => setSelectedExercise(null)}
                  className="flex-1 px-4 py-2 border rounded-lg hover:bg-gray-50"
                >
                  Hủy
                </button>
                <button
                  onClick={handleAddExercise}
                  disabled={submitting}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  {submitting ? <Loader2 className="animate-spin mx-auto" /> : 'Lưu lại'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}