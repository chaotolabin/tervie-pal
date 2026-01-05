import React, { useState, useRef, useEffect } from 'react';
import { Message } from './Message';
import { useChatbot } from '../../../hooks/useChatbot';
import { X, Send, Loader2, MessageCircle, Trash2 } from 'lucide-react';

interface ChatbotWindowProps {
  onClose: () => void;
}

export const ChatbotWindow: React.FC<ChatbotWindowProps> = ({ onClose }) => {
  const { messages, isLoading, sendMessage, clearMessages } = useChatbot();
  const [input, setInput] = useState('');
  const [showClearConfirm, setShowClearConfirm] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      await sendMessage(input);
      setInput('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleClearMessages = () => {
    clearMessages();
    setShowClearConfirm(false);
  };

  return (
    <div className="flex flex-col h-[600px] w-[400px] bg-white rounded-2xl shadow-2xl overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center">
            <MessageCircle className="text-blue-600" size={24} />
          </div>
          <div>
            <h3 className="font-semibold text-lg">NutriBot</h3>
            <p className="text-xs text-blue-100">
              {isLoading ? '⏳ Đang suy nghĩ...' : 'Trợ lý dinh dưỡng'}
            </p>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          {messages.length > 1 && (
            <button
              onClick={() => setShowClearConfirm(true)}
              className="p-2 hover:bg-blue-500 rounded-lg transition-colors"
              title="Xóa lịch sử chat"
            >
              <Trash2 size={18} />
            </button>
          )}
          
          <button
            onClick={onClose}
            className="p-2 hover:bg-blue-500 rounded-lg transition-colors"
            title="Đóng (chatbot vẫn chạy ngầm)"
          >
            <X size={20} />
          </button>
        </div>
      </div>

      {/* ✅ Loading banner when closed */}
      {isLoading && (
        <div className="bg-yellow-50 border-b border-yellow-200 px-4 py-2 text-sm text-yellow-800">
          💡 <strong>Tip:</strong> Bạn có thể đóng cửa sổ này. Chatbot sẽ tiếp tục xử lý yêu cầu ở chế độ ngầm.
        </div>
      )}

      {/* Confirm Dialog */}
      {showClearConfirm && (
        <div className="absolute inset-0 bg-black/50 flex items-center justify-center z-50 rounded-2xl">
          <div className="bg-white p-6 rounded-xl shadow-xl max-w-sm m-4">
            <h4 className="text-lg font-semibold mb-2">Xóa lịch sử chat?</h4>
            <p className="text-gray-600 text-sm mb-4">
              Bạn có chắc muốn xóa toàn bộ lịch sử trò chuyện? Hành động này không thể hoàn tác.
            </p>
            <div className="flex space-x-2">
              <button
                onClick={() => setShowClearConfirm(false)}
                className="flex-1 px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded-lg transition-colors"
              >
                Hủy
              </button>
              <button
                onClick={handleClearMessages}
                className="flex-1 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
              >
                Xóa
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
        {messages.map((message) => (
          <Message key={message.id} message={message} />
        ))}
        
        {isLoading && (
          <div className="flex justify-start mb-4">
            <div className="bg-gray-100 rounded-2xl px-4 py-3 border border-gray-200">
              <div className="flex items-center space-x-2 text-gray-500">
                <Loader2 size={16} className="animate-spin" />
                <span className="text-sm">Đang suy nghĩ...</span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Form */}
      <div className="p-4 bg-white border-t border-gray-200">
        <form onSubmit={handleSubmit} className="flex space-x-2">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Nhập tin nhắn..."
            disabled={isLoading}
            className="
              flex-1 px-4 py-3 
              border border-gray-300 rounded-xl
              focus:outline-none focus:ring-2 focus:ring-blue-500
              disabled:bg-gray-100 disabled:cursor-not-allowed
              text-sm
            "
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="
              px-4 py-3 
              bg-blue-600 text-white rounded-xl
              hover:bg-blue-700 
              disabled:bg-gray-300 disabled:cursor-not-allowed
              transition-colors
              flex items-center justify-center
            "
          >
            <Send size={20} />
          </button>
        </form>
        
        {/* Quick Suggestions */}
        <div className="mt-2 flex flex-wrap gap-2">
          {!isLoading && messages.length === 1 && (
            <>
              <button
                onClick={() => setInput('Trứng có bao nhiêu calo?')}
                className="text-xs px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded-full text-gray-700 transition-colors"
              >
                💡 Tra cứu dinh dưỡng
              </button>
              <button
                onClick={() => setInput('Gợi ý món tăng cân')}
                className="text-xs px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded-full text-gray-700 transition-colors"
              >
                🎯 Gợi ý món ăn
              </button>
              <button
                onClick={() => setInput('Tạo thực đơn cho tôi')}
                className="text-xs px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded-full text-gray-700 transition-colors"
              >
                📋 Tạo thực đơn
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};