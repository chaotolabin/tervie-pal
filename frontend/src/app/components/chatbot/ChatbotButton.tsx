import React from 'react';
import { MessageCircle } from 'lucide-react';

interface ChatbotButtonProps {
  onClick: () => void;
  hasNewMessage?: boolean;
}

export const ChatbotButton: React.FC<ChatbotButtonProps> = ({ 
  onClick, 
  hasNewMessage = false 
}) => {
  return (
    <button
      onClick={onClick}
      className="
        relative
        w-16 h-16 
        bg-gradient-to-r from-blue-600 to-blue-700
        hover:from-blue-700 hover:to-blue-800
        text-white rounded-full 
        shadow-lg hover:shadow-xl 
        transition-all duration-300
        flex items-center justify-center
        group
      "
      aria-label="Open chatbot"
    >
      <MessageCircle 
        size={28} 
        className="group-hover:scale-110 transition-transform"
      />
      
      {/* ✅ New message indicator (red dot) */}
      {hasNewMessage && (
        <span className="absolute -top-1 -right-1 flex h-5 w-5">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-5 w-5 bg-red-500 border-2 border-white"></span>
        </span>
      )}
    </button>
  );
};