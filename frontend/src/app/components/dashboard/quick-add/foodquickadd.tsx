import React, { useState, useEffect } from 'react';
import { FoodService } from '../../../../service/food.service';
import { Search, Plus, ChefHat } from 'lucide-react';
import FoodAddModal from './FoodAddModal';
import CreateCustomFoodModal from './CreateCustomFoodModal';

interface FoodQuickAddProps {
  onClose?: () => void;
}

export default function FoodQuickAdd({ onClose }: FoodQuickAddProps) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<any[]>([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [selectedFoodId, setSelectedFoodId] = useState<number | null>(null);
  const [selectedFoodName, setSelectedFoodName] = useState<string>('');


  useEffect(() => {
    if (query.length > 1) {
      const delaySearch = setTimeout(async () => {
        const data = await FoodService.search(query);
        setResults(data.items); 
      }, 500);
      return () => clearTimeout(delaySearch);
    }
  }, [query]);

  const handleSelectFood = (food: any) => {
    setSelectedFoodId(food.id);
    setSelectedFoodName(food.name);
    setModalOpen(true);
  };

  const handleModalClose = () => {
    setModalOpen(false);
    setSelectedFoodId(null);
    setSelectedFoodName('');
  };

  const handleModalSuccess = () => {
    handleModalClose();
    if (onClose) onClose();
  };

  return (
    <div className="p-4">
      <div className="flex gap-2 mb-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-3 text-gray-400" size={20} />
          <input
            type="text"
            placeholder="Tìm tên món ăn (ví dụ: cơm trắng)..."
            className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </div>
        <button
          onClick={() => setCreateModalOpen(true)}
          className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 flex items-center gap-2 whitespace-nowrap"
        >
          <ChefHat size={18} />
          <span className="hidden sm:inline">Tạo món mới</span>
        </button>
      </div>

      <div className="space-y-2 max-h-60 overflow-y-auto">
        {results.map((food) => (
          <div 
            key={food.id} 
            className="flex justify-between items-center p-3 hover:bg-gray-50 border-b cursor-pointer"
            onClick={() => handleSelectFood(food)}
          >
            <div className="flex-1">
              <p className="font-medium">{food.name}</p>
              <p className="text-xs text-gray-500">{food.food_group || 'Chung'}</p>
            </div>
            <div className="p-1 bg-green-100 text-green-600 rounded-full">
              <Plus size={20} />
            </div>
          </div>
        ))}
      </div>

      {/* Food Add Modal */}
      {selectedFoodId && (
        <FoodAddModal
          foodId={selectedFoodId}
          foodName={selectedFoodName}
          open={modalOpen}
          onClose={handleModalClose}
          onSuccess={handleModalSuccess}
        />
      )}

      {/* Create Custom Food Modal */}
      <CreateCustomFoodModal
        open={createModalOpen}
        onClose={() => setCreateModalOpen(false)}
        onSuccess={(foodId, foodName) => {
          setCreateModalOpen(false);
          // Auto open add modal for the newly created food
          setSelectedFoodId(foodId);
          setSelectedFoodName(foodName);
          setModalOpen(true);
        }}
      />

      {results.length === 0 && query.length > 1 && (
        <p className="text-center text-gray-500 mt-4 italic">
          Không tìm thấy? Hãy tạo món ăn mới của riêng bạn.
        </p>
      )}
    </div>
  );
}