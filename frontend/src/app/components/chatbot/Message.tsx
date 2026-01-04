// src/app/components/chatbot/Message.tsx

import React from 'react';
import { ChatMessage } from '../../../service/chatbot.service';

interface MessageProps {
  message: ChatMessage;
}

export const Message: React.FC<MessageProps> = ({ message }) => {
  const isUser = message.role === 'user';

  const formatContent = (text: string) => {
    return text.split('\n').map((line, i) => {
      if (!line.trim()) return <br key={i} />;
      
      const html = line.replace(/\*\*(.+?)\*\*/g, '<strong class="font-semibold">$1</strong>');
      
      return (
        <div 
          key={i}
          className="leading-relaxed"
          dangerouslySetInnerHTML={{ __html: html }}
        />
      );
    });
  };

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={`
          max-w-[85%] rounded-2xl px-4 py-3 shadow-sm
          ${isUser 
            ? 'bg-blue-600 text-white rounded-br-md' 
            : 'bg-gray-100 text-gray-900 border border-gray-200 rounded-bl-md'
          }
        `}
      >
        <div className="text-sm">
          {formatContent(message.content)}
        </div>

        <div 
          className={`
            text-xs mt-2 
            ${isUser ? 'text-blue-100 text-right' : 'text-gray-500'}
          `}
        >
          {message.timestamp.toLocaleTimeString('vi-VN', {
            hour: '2-digit',
            minute: '2-digit'
          })}
        </div>
      </div>
    </div>
  );
};