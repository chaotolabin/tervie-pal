// src/app/components/chatbot/ChatbotButton.tsx

import React from 'react';
import { MessageCircle } from 'lucide-react';

interface ChatbotButtonProps {
  onClick: () => void;
}

export const ChatbotButton: React.FC<ChatbotButtonProps> = ({ onClick }) => {
  return (
    <button
      onClick={onClick}
      className="
        w-14 h-14
        bg-gradient-to-r from-blue-600 to-blue-700
        hover:from-blue-700 hover:to-blue-800
        text-white
        rounded-full
        shadow-lg hover:shadow-xl
        transition-all duration-300
        flex items-center justify-center
        group
        focus:outline-none focus:ring-4 focus:ring-blue-300
      "
      aria-label="Mở chatbot"
    >
      <MessageCircle 
        size={28} 
        className="group-hover:scale-110 transition-transform" 
      />
    </button>
  );
};