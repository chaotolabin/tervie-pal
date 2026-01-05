import React from 'react';
import { HelpCircle, RefreshCw } from 'lucide-react';

interface NutrientTargetsProps {
  energy: {
    consumed: number;
    target: number;
  };
  protein: {
    consumed: number;
    target: number;
  };
  carbs: {
    consumed: number;
    target: number;
  };
  fat: {
    consumed: number;
    target: number;
  };
  onRefresh?: () => void;
}

export default function NutrientTargets({
  energy,
  protein,
  carbs,
  fat,
  onRefresh,
}: NutrientTargetsProps) {
  const calculatePercentage = (current: number, target: number): number => {
    if (!target || target === 0) return 0;
    const percentage = (current / target) * 100;
    return Math.min(Math.max(percentage, 0), 100); // Clamp between 0 and 100
  };

  const formatValue = (value: number | string | null | undefined, decimals: number = 1): string => {
    if (value === null || value === undefined) return '0';
    const num = typeof value === 'string' ? parseFloat(value) : Number(value);
    if (isNaN(num)) return '0';
    return num.toFixed(decimals);
  };

  const nutrients = [
    {
      label: 'Energy',
      consumed: energy.consumed,
      target: energy.target,
      unit: 'kcal',
      color: 'bg-slate-500',
      trackColor: 'bg-slate-100',
      textColor: 'text-slate-600',
    },
    {
      label: 'Protein',
      consumed: protein.consumed,
      target: protein.target,
      unit: 'g',
      color: 'bg-rose-500',
      trackColor: 'bg-rose-100',
      textColor: 'text-rose-600',
    },
    {
      label: 'Net Carbs',
      consumed: carbs.consumed,
      target: carbs.target,
      unit: 'g',
      color: 'bg-amber-500',
      trackColor: 'bg-amber-100',
      textColor: 'text-amber-600',
    },
    {
      label: 'Fat',
      consumed: fat.consumed,
      target: fat.target,
      unit: 'g',
      color: 'bg-yellow-500',
      trackColor: 'bg-yellow-100',
      textColor: 'text-yellow-600',
    },
  ];

  return (
    <div className="bg-white rounded-xl shadow p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <h3 className="font-bold text-lg">Targets</h3>
          <button
            className="text-gray-400 hover:text-gray-600 transition-colors"
            title="Thông tin về mục tiêu dinh dưỡng"
          >
            <HelpCircle size={16} />
          </button>
        </div>
        <div className="flex items-center gap-2">
          <span className="font-bold text-teal-600 text-sm">CONSUMED</span>
          {onRefresh && (
            <button
              onClick={onRefresh}
              className="text-gray-400 hover:text-gray-600 transition-colors"
              title="Làm mới dữ liệu"
            >
              <RefreshCw size={16} />
            </button>
          )}
        </div>
      </div>

      <div className="space-y-5">
        {nutrients.map((nutrient) => {
          const percentage = calculatePercentage(nutrient.consumed, nutrient.target);
          const displayPercentage = Math.round(percentage);

          return (
            <div key={nutrient.label} className="space-y-1.5">
              {/* Label */}
              <div className="flex items-center justify-between">
                <span className={`text-sm font-medium ${nutrient.textColor}`}>
                  {nutrient.label}
                </span>
                <span className={`text-xs ${nutrient.textColor} font-normal opacity-80`}>
                  {displayPercentage}%
                </span>
              </div>

              {/* Current / Target text above progress bar */}
              <div className={`text-xs ${nutrient.textColor} opacity-90`}>
                {formatValue(nutrient.consumed)} / {formatValue(nutrient.target)} {nutrient.unit}
              </div>

              {/* Progress Bar */}
              <div className={`w-full h-1.5 ${nutrient.trackColor} rounded-full overflow-hidden`}>
                <div
                  className={`h-full ${nutrient.color} transition-all duration-300 ease-out rounded-full`}
                  style={{ width: `${percentage}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

