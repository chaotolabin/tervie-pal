import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Progress } from '../ui/progress';

interface MacroData {
  current: number;
  goal: number;
  unit?: string;
}

interface MacroSummaryProps {
  protein: MacroData;
  carbs: MacroData;
  fat: MacroData;
  showChart?: boolean;
}

export default function MacroSummary({ protein, carbs, fat, showChart = true }: MacroSummaryProps) {
  const macros = [
    { name: 'Protein', data: protein, color: 'bg-red-500', bgColor: 'bg-red-100' },
    { name: 'Carbs', data: carbs, color: 'bg-blue-500', bgColor: 'bg-blue-100' },
    { name: 'Fat', data: fat, color: 'bg-yellow-500', bgColor: 'bg-yellow-100' }
  ];

  const totalCurrent = protein.current + carbs.current + fat.current;
  const proteinPercent = (protein.current / totalCurrent) * 100;
  const carbsPercent = (carbs.current / totalCurrent) * 100;
  const fatPercent = (fat.current / totalCurrent) * 100;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Dinh dưỡng đa lượng (Macros)</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Circular Chart */}
        {showChart && (
          <div className="flex items-center justify-center">
            <div className="relative size-48">
              <svg className="size-full -rotate-90" viewBox="0 0 100 100">
                <circle
                  cx="50"
                  cy="50"
                  r="40"
                  fill="none"
                  stroke="#f3f4f6"
                  strokeWidth="8"
                />
                
                {/* Protein */}
                <circle
                  cx="50"
                  cy="50"
                  r="40"
                  fill="none"
                  stroke="#ef4444"
                  strokeWidth="8"
                  strokeDasharray={`${proteinPercent * 2.51} ${251 - proteinPercent * 2.51}`}
                  strokeDashoffset="0"
                />
                
                {/* Carbs */}
                <circle
                  cx="50"
                  cy="50"
                  r="40"
                  fill="none"
                  stroke="#3b82f6"
                  strokeWidth="8"
                  strokeDasharray={`${carbsPercent * 2.51} ${251 - carbsPercent * 2.51}`}
                  strokeDashoffset={`-${proteinPercent * 2.51}`}
                />
                
                {/* Fat */}
                <circle
                  cx="50"
                  cy="50"
                  r="40"
                  fill="none"
                  stroke="#eab308"
                  strokeWidth="8"
                  strokeDasharray={`${fatPercent * 2.51} ${251 - fatPercent * 2.51}`}
                  strokeDashoffset={`-${(proteinPercent + carbsPercent) * 2.51}`}
                />
              </svg>
              
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="text-center">
                  <p className="text-2xl font-bold">{totalCurrent.toFixed(2)}g</p>
                  <p className="text-xs text-gray-600">Tổng</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Macro Details */}
        <div className="space-y-4">
          {macros.map((macro) => {
            const percentage = (macro.data.current / macro.data.goal) * 100;
            const isOverGoal = percentage > 100;
            
            return (
              <div key={macro.name} className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className={`size-3 rounded-full ${macro.color}`} />
                    <span className="font-medium">{macro.name}</span>
                  </div>
                  <span className="text-sm">
                    <span className={isOverGoal ? 'text-red-600 font-semibold' : 'font-semibold'}>
                      {macro.data.current.toFixed(2)}g
                    </span>
                    <span className="text-gray-600"> / {macro.data.goal}g</span>
                  </span>
                </div>
                
                <div className="relative">
                  <Progress 
                    value={Math.min(percentage, 100)} 
                    className={`h-2 ${macro.bgColor}`}
                  />
                  {isOverGoal && (
                    <div className="absolute top-0 right-0 h-2 bg-red-500 rounded-r-full" 
                         style={{ width: `${Math.min((percentage - 100) / 2, 50)}%` }} 
                    />
                  )}
                </div>
                
                <div className="flex justify-between text-xs text-gray-600">
                  <span>{Math.round(percentage)}%</span>
                  <span>
                    {macro.data.goal - macro.data.current > 0 
                      ? `Còn ${(macro.data.goal - macro.data.current).toFixed(2)}g`
                      : isOverGoal 
                      ? `Vượt ${(macro.data.current - macro.data.goal).toFixed(2)}g`
                      : 'Đã đạt mục tiêu'
                    }
                  </span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Summary Stats */}
        <div className="grid grid-cols-3 gap-2 pt-4 border-t">
          <div className="text-center p-2 bg-red-50 rounded">
            <p className="text-xs text-gray-600">Protein</p>
            <p className="font-bold text-red-600">{Math.round(proteinPercent)}%</p>
          </div>
          <div className="text-center p-2 bg-blue-50 rounded">
            <p className="text-xs text-gray-600">Carbs</p>
            <p className="font-bold text-blue-600">{Math.round(carbsPercent)}%</p>
          </div>
          <div className="text-center p-2 bg-yellow-50 rounded">
            <p className="text-xs text-gray-600">Fat</p>
            <p className="font-bold text-yellow-600">{Math.round(fatPercent)}%</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
