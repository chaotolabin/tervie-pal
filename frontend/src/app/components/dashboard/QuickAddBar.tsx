import React from 'react';
import { Plus } from 'lucide-react';
import { Card, CardContent } from '../ui/card';

interface QuickAddBarProps {
  /** Callback when the bar is clicked */
  onClick: () => void;
}

export default function QuickAddBar({ onClick }: QuickAddBarProps) {
  return (
    <Card 
      className="border border-gray-200 shadow-sm hover:shadow-md transition-all cursor-pointer group"
      onClick={onClick}
    >
      <CardContent className="p-4">
        <div className="flex items-center gap-4">
          {/* Circular Plus Button */}
          <div className="size-12 bg-[#f8c6d8] rounded-full flex items-center justify-center group-hover:scale-105 transition-transform shadow-md">
            <Plus className="size-6 text-white" />
          </div>
          
          {/* Text Content */}
          <div className="flex-1">
            <p className="font-semibold text-gray-900 group-hover:text-pink-600 transition-colors">
              Thêm nhanh
            </p>
            <p className="text-sm text-gray-500 group-hover:text-pink-500 transition-colors">
              Ghi nhận thực phẩm, bài tập, hoặc cập nhật cân nặng, chiều cao hiện tại của bạn
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

