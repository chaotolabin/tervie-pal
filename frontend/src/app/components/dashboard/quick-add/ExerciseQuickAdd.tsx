import React, { useState } from 'react';
import api from '../../../lib/api';

export default function ExerciseQuickAdd() {
  const [exerciseSearch, setExerciseSearch] = useState('');
  
  const handleAddExercise = async (exerciseId: number) => {
    // Gọi API logExercise khớp với logs.py
    await api.post('/logs/exercise', {
      exercise_id: exerciseId,
      duration_min: 30, // Ví dụ mặc định
      logged_at: new Date().toISOString()
    });
    alert("Đã thêm bài tập!");
  };

  return (
    <div className="p-4 space-y-4">
      <input 
        type="text" 
        placeholder="Tìm bài tập (Chạy bộ, Gym...)" 
        className="w-full border p-2 rounded"
        onChange={(e) => setExerciseSearch(e.target.value)}
      />
      {/* List kết quả từ /exercises/search */}
    </div>
  );
}