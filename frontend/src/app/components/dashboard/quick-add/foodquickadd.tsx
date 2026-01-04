import React, { useState, useEffect } from 'react';
import { FoodService } from '../../../../service/food.service';
import { Search, Plus, Calculator } from 'lucide-react';
import { toast } from 'sonner';
import { LogService } from '../../../../service/log.service';

interface FoodQuickAddProps {
  onClose?: () => void;
}

export default function FoodQuickAdd({ onClose }: FoodQuickAddProps) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<any[]>([]);
  const [selectedFood, setSelectedFood] = useState<any | null>(null);


  useEffect(() => {
    if (query.length > 1) {
      const delaySearch = setTimeout(async () => {
        const data = await FoodService.search(query);
        setResults(data.items); 
      }, 500);
      return () => clearTimeout(delaySearch);
    }
  }, [query]);

  const handleLogFood = async (e: React.MouseEvent, foodId: number) => {
    e.stopPropagation(); // Prevent triggering onClick on parent div
    try {
      const today = new Date().toISOString().split('T')[0];
      await LogService.addFoodLog({
        logged_at: new Date().toISOString(),
        items: [
          {
            food_id: foodId,
            portion_id: 1, // Default portion, user can update later
            quantity: 1
          }
        ]
      });
      toast.success("Đã ghi nhận món ăn vào nhật ký!");
      if (onClose) onClose();
      
      // Trigger refresh summary ở dashboard
      window.dispatchEvent(new CustomEvent('refreshDashboard'));
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Không thể lưu món ăn");
    }
  };

  return (
    <div className="p-4">
      <div className="relative mb-4">
        <Search className="absolute left-3 top-3 text-gray-400" size={20} />
        <input
          type="text"
          placeholder="Tìm tên món ăn (ví dụ: cơm trắng)..."
          className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
      </div>

      <div className="space-y-2 max-h-60 overflow-y-auto">
        {results.map((food) => (
          <div 
            key={food.id} 
            className="flex justify-between items-center p-3 hover:bg-gray-50 border-b cursor-pointer"
            onClick={() => setSelectedFood(food)}
          >
            <div>
              <p className="font-medium">{food.name}</p>
              <p className="text-xs text-gray-500">{food.food_group || 'Chung'}</p>
            </div>
            <button 
              onClick={(e) => handleLogFood(e, food.id)}
              className="p-1 bg-green-100 text-green-600 rounded-full hover:bg-green-200"
            >
              <Plus size={20} />
            </button>
          </div>
        ))}
      </div>

      {results.length === 0 && query.length > 1 && (
        <p className="text-center text-gray-500 mt-4 italic">
          Không tìm thấy? Hãy tạo món ăn mới của riêng bạn.
        </p>
      )}
    </div>
  );
}