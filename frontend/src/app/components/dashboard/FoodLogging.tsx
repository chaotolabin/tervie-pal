import React, { useState, useEffect, useMemo } from 'react';
import { toast } from 'sonner';
import { FoodService } from '../../../service/food.service';
import { Trash2, Apple } from 'lucide-react';
import { Button } from '../ui/button';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '../ui/accordion';

interface FoodItem {
  id: number;
  food_id: number;
  calories: number | null;
  protein_g: number | null;
  carbs_g: number | null;
  fat_g: number | null;
  grams: number;
  quantity: number;
  unit: string;
  food_name?: string;
}

interface FoodLog {
  id: number;
  meal_type: string;
  total_calories: number;
  total_protein_g: number;
  total_carbs_g: number;
  total_fat_g: number;
  items: FoodItem[];
}

interface MealGroupSummary {
  total_calories: number;
  total_protein: number;
  total_carbs: number;
  total_fat: number;
  logs: FoodLog[];
}

const mealTypeLabels: Record<string, string> = {
  breakfast: 'Bữa sáng',
  lunch: 'Bữa trưa',
  dinner: 'Bữa tối',
  snacks: 'Đồ ăn vặt',
};

const mealTypeOrder = ['breakfast', 'lunch', 'dinner', 'snacks'];

export default function FoodLogging({ foodLogs }: { foodLogs: any[] }) {
  const [foodNames, setFoodNames] = useState<Record<number, string>>({});
  const [loadingNames, setLoadingNames] = useState<Record<number, boolean>>({});

  // Fetch food names for all unique food_ids
  useEffect(() => {
    const fetchFoodNames = async () => {
      const uniqueFoodIds = new Set<number>();
      foodLogs.forEach((log: any) => {
        log.items?.forEach((item: any) => {
          if (item.food_id && !foodNames[item.food_id] && !loadingNames[item.food_id]) {
            uniqueFoodIds.add(item.food_id);
          }
        });
      });

      if (uniqueFoodIds.size === 0) return;

      // Mark as loading
      const newLoading: Record<number, boolean> = { ...loadingNames };
      uniqueFoodIds.forEach(id => {
        newLoading[id] = true;
      });
      setLoadingNames(newLoading);

      // Fetch all food names in parallel
      const fetchPromises = Array.from(uniqueFoodIds).map(async (foodId) => {
        try {
          const foodDetail = await FoodService.getDetail(foodId);
          return { foodId, name: foodDetail.name };
        } catch (error) {
          return { foodId, name: `Food #${foodId}` };
        }
      });

      const results = await Promise.all(fetchPromises);
      const newNames: Record<number, string> = { ...foodNames };
      results.forEach(({ foodId, name }) => {
        newNames[foodId] = name;
      });
      setFoodNames(newNames);

      // Clear loading state
      const finalLoading: Record<number, boolean> = { ...loadingNames };
      uniqueFoodIds.forEach(id => {
        delete finalLoading[id];
      });
      setLoadingNames(finalLoading);
    };

    fetchFoodNames();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [foodLogs]);

  const handleDelete = async (logId: number, e?: React.MouseEvent) => {
    if (e) {
      e.stopPropagation(); // Prevent accordion toggle
    }
    if (!confirm('Bạn có chắc muốn xóa bữa ăn này?')) return;
    
    try {
      const { LogService } = await import('../../../service/log.service');
      await LogService.deleteFoodLog(logId);
      toast.success('Đã xóa bữa ăn');
      
      // Trigger refresh
      window.dispatchEvent(new CustomEvent('refreshDashboard'));
      window.dispatchEvent(new CustomEvent('refreshFoodLogs'));
    } catch (error: any) {
      let errorMsg = 'Không thể xóa bữa ăn';
      if (error.response?.data?.detail) {
        const detail = error.response.data.detail;
        if (typeof detail === 'string') {
          errorMsg = detail;
        } else if (Array.isArray(detail) && detail.length > 0) {
          errorMsg = detail.map((err: any) => err.msg || JSON.stringify(err)).join(', ');
        } else if (typeof detail === 'object') {
          errorMsg = JSON.stringify(detail);
        }
      }
      toast.error(errorMsg);
    }
  };

  // Group logs by meal_type and calculate summaries
  const mealGroups = useMemo(() => {
    const groups: Record<string, MealGroupSummary> = {};
    
    foodLogs.forEach((log: any) => {
      const mealType = log.meal_type || 'snacks';
      if (!groups[mealType]) {
        groups[mealType] = {
          total_calories: 0,
          total_protein: 0,
          total_carbs: 0,
          total_fat: 0,
          logs: [],
        };
      }
      
      // Sum up macros from all items in this log entry
      const entryCalories = Number(log.total_calories || 0);
      const entryProtein = Number(log.total_protein_g || 0);
      const entryCarbs = Number(log.total_carbs_g || 0);
      const entryFat = Number(log.total_fat_g || 0);
      
      groups[mealType].total_calories += entryCalories;
      groups[mealType].total_protein += entryProtein;
      groups[mealType].total_carbs += entryCarbs;
      groups[mealType].total_fat += entryFat;
      groups[mealType].logs.push(log);
    });
    
    return groups;
  }, [foodLogs]);

  // Helper to format numbers
  const formatNumber = (val: number | null | undefined, decimals: number = 2): string => {
    if (val === null || val === undefined) return '0';
    return Number(val).toFixed(decimals);
  };

  const formatMacro = (val: number | null | undefined): string => {
    const num = formatNumber(val, 1);
    return num === '0.00' ? '0' : num;
  };

  if (foodLogs.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow p-4">
        <h3 className="font-bold text-lg mb-4">Bữa ăn hôm nay</h3>
        <p className="text-gray-400">Chưa có dữ liệu ăn uống.</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow p-4">
      <h3 className="font-bold text-lg mb-4">Bữa ăn hôm nay</h3>
      
      <Accordion type="multiple" className="w-full" defaultValue={mealTypeOrder}>
        {mealTypeOrder.map((mealType) => {
          const group = mealGroups[mealType];
          if (!group || group.logs.length === 0) return null;

          const mealLabel = mealTypeLabels[mealType] || mealType;
          const summary = `${formatMacro(group.total_calories)} kcal • ${formatMacro(group.total_protein)} g protein • ${formatMacro(group.total_carbs)} g carbs • ${formatMacro(group.total_fat)} g fat`;

          return (
            <AccordionItem key={mealType} value={mealType} className="border-b">
              <AccordionTrigger className="hover:no-underline py-3">
                <div className="flex items-center justify-between w-full pr-4">
                  <span className="font-semibold text-gray-800">{mealLabel}</span>
                  <span className="text-sm text-gray-500 font-normal">
                    {summary}
                  </span>
                </div>
              </AccordionTrigger>
              
              <AccordionContent className="pt-2 pb-4">
                <div className="space-y-3">
                  {group.logs.map((log: any) => (
                    <div key={log.id} className="space-y-1">
                      {/* Food Items - Each item in a horizontal row */}
                      {log.items?.map((item: any, idx: number) => {
                        const foodName = foodNames[item.food_id] || 
                                       (loadingNames[item.food_id] ? 'Đang tải...' : `Food #${item.food_id}`);
                        const itemCalories = formatNumber(item.calories);
                        const serving = item.portion_id 
                          ? `${formatNumber(item.quantity, 3)} ${item.unit}`
                          : `${formatNumber(item.grams, 3)} g`;
                        
                        return (
                          <div
                            key={item.id || idx}
                            className="flex items-center gap-3 px-3 py-2.5 rounded-md hover:bg-gray-50 transition-colors group/item"
                          >
                            {/* Food Icon & Name */}
                            <div className="flex items-center gap-2 flex-1 min-w-0">
                              <Apple size={18} className="text-red-500 flex-shrink-0" />
                              <span className="text-sm text-gray-800 truncate font-medium">
                                {foodName}
                              </span>
                            </div>
                            
                            {/* Quantity */}
                            <div className="text-sm text-gray-600 flex-shrink-0 min-w-[80px]">
                              {serving}
                            </div>
                            
                            {/* Calories */}
                            <div className="text-sm font-semibold text-blue-600 flex-shrink-0 min-w-[90px] text-right">
                              {itemCalories} kcal
                            </div>
                            
                            {/* Delete Button - Show on hover */}
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={(e) => handleDelete(log.id, e)}
                              className="h-8 w-8 text-gray-400 hover:text-red-600 hover:bg-red-50 opacity-0 group-hover/item:opacity-100 transition-opacity flex-shrink-0"
                              title="Xóa bữa ăn"
                            >
                              <Trash2 size={16} />
                            </Button>
                          </div>
                        );
                      })}
                    </div>
                  ))}
                </div>
              </AccordionContent>
            </AccordionItem>
          );
        })}
      </Accordion>
    </div>
  );
}