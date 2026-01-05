import React, { useState, useEffect } from 'react';
import { ChatbotButton } from './ChatbotButton';
import { ChatbotWindow } from './ChatbotWindow';
import { useChatbot } from '../../../hooks/useChatbot';

export const ChatbotWidget: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const { hasNewMessage, markAsRead } = useChatbot();

  const handleOpen = () => {
    setIsOpen(true);
    markAsRead(); // ✅ Clear notification when opening
  };

  return (
    <>
      <div className="fixed bottom-6 right-6 z-50">
        {isOpen && (
          <div className="mb-4">
            <ChatbotWindow onClose={() => setIsOpen(false)} />
          </div>
        )}

        {!isOpen && (
          <ChatbotButton 
            onClick={handleOpen} 
            hasNewMessage={hasNewMessage} 
          />
        )}
      </div>

      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/20 z-40 md:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}
    </>
  );
};