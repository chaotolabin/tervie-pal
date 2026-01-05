import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Progress } from '../ui/progress';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

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
  const [activeIndex, setActiveIndex] = useState<number | null>(null);
  
  const macros = [
    { name: 'Protein', data: protein, color: '#FB7185', bgColor: 'bg-gray-100' },
    { name: 'Carbs', data: carbs, color: '#38BDF8', bgColor: 'bg-gray-100' },
    { name: 'Fat', data: fat, color: '#FBBF24', bgColor: 'bg-gray-100' }
  ];

  const totalCurrent = protein.current + carbs.current + fat.current;
  const proteinPercent = (protein.current / totalCurrent) * 100;
  const carbsPercent = (carbs.current / totalCurrent) * 100;
  const fatPercent = (fat.current / totalCurrent) * 100;
  
  const chartData = [
    { name: 'Protein', value: protein.current, color: '#FB7185', percent: proteinPercent },
    { name: 'Carbs', value: carbs.current, color: '#38BDF8', percent: carbsPercent },
    { name: 'Fat', value: fat.current, color: '#FBBF24', percent: fatPercent }
  ];

  return (
    <Card className="shadow-sm">
      <CardHeader>
        <CardTitle>Dinh dưỡng đa lượng (Macros)</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex gap-8">
          {/* Left Section - Pie Chart (35%) */}
          {showChart && (
            <div className="w-[35%] flex items-center justify-center">
              <div className="relative w-full max-w-[200px] aspect-square">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={chartData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={80}
                      paddingAngle={5}
                      cornerRadius={5}
                      dataKey="value"
                      onMouseEnter={(_, index) => setActiveIndex(index)}
                      onMouseLeave={() => setActiveIndex(null)}
                      style={{ outline: 'none' }}
                    >
                      {chartData.map((entry, index) => (
                        <Cell 
                          key={`cell-${index}`} 
                          fill={entry.color}
                          stroke={activeIndex === index ? '#fff' : 'none'}
                          strokeWidth={2}
                          fillOpacity={activeIndex === null || activeIndex === index ? 1 : 0.6}
                          style={{ 
                            transition: 'fill-opacity 0.3s ease, stroke 0.3s ease',
                            cursor: 'pointer'
                          }}
                        />
                      ))}
                    </Pie>
                    <Tooltip 
                      contentStyle={{
                        backgroundColor: 'white',
                        border: 'none',
                        borderRadius: '8px',
                        boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
                        padding: '8px 12px'
                      }}
                      formatter={(value: any, name: any, props: any) => [
                        `${value.toFixed(1)}g (${Math.round(props.payload.percent)}%)`,
                        name
                      ]}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {/* Right Section - Macro Details (65%) */}
          <div className="w-[65%] space-y-5 py-2">
            {macros.map((macro, index) => {
              const percentage = (macro.data.current / macro.data.goal) * 100;
              const isOverGoal = percentage > 100;
              const macroPercent = index === 0 ? proteinPercent : index === 1 ? carbsPercent : fatPercent;
              
              return (
                <div key={macro.name} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="size-3 rounded-full" style={{ backgroundColor: macro.color }} />
                      <span className="font-semibold text-gray-700">{macro.name}</span>
                      <span 
                        className="text-xs font-bold px-2 py-0.5"
                        style={{ 
                          backgroundColor: macro.color + '20',
                          color: macro.color
                        }}
                      >
                        {Math.round(macroPercent)}%
                      </span>
                    </div>
                    <span className="text-sm">
                      <span className={isOverGoal ? 'text-red-600 font-semibold' : 'font-semibold text-gray-900'}>
                        {macro.data.current.toFixed(1)}g
                      </span>
                      <span className="text-gray-500"> / {macro.data.goal}g</span>
                    </span>
                  </div>
                  
                  <div className="relative h-2 bg-gray-100 overflow-hidden">
                    <div 
                      className="h-full transition-all duration-300"
                      style={{ 
                        backgroundColor: macro.color,
                        width: `${Math.min(percentage, 100)}%` 
                      }}
                    />
                  </div>
                  
                  <div className="flex justify-between text-xs text-gray-500">
                    <span>{Math.round(percentage)}%</span>
                    <span>
                      {macro.data.goal - macro.data.current > 0 
                        ? `Còn ${(macro.data.goal - macro.data.current).toFixed(1)}g`
                        : isOverGoal 
                        ? `Vượt ${(macro.data.current - macro.data.goal).toFixed(1)}g`
                        : 'Đã đạt mục tiêu'
                      }
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
