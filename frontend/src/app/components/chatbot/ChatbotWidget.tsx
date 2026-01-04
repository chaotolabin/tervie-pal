// src/app/components/chatbot/ChatbotWidget.tsx

import React, { useState } from 'react';
import { ChatbotButton } from './ChatbotButton';
import { ChatbotWindow } from './ChatbotWindow';

export const ChatbotWidget: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <div className="fixed bottom-6 right-6 z-50">
        {isOpen && (
          <div className="mb-4">
            <ChatbotWindow onClose={() => setIsOpen(false)} />
          </div>
        )}

        {!isOpen && (
          <ChatbotButton onClick={() => setIsOpen(true)} />
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