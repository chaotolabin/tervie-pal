import { useState } from 'react';
import { chatbotService, ChatMessage } from '../service/chatbot.service';

export const useChatbot = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'Xin chào! Mình là NutriBot 🤖\n\nMình có thể giúp bạn:\n• Tra cứu dinh dưỡng món ăn\n• Gợi ý món phù hợp với mục tiêu\n• Tạo thực đơn cả ngày\n\nBạn cần tư vấn gì không?',
      timestamp: new Date(),
    },
  ]);
  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = async (content: string) => {
    // Add user message
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // ✅ Call API with authentication
      const response = await chatbotService.sendMessage(content);

      // Add bot response
      const botMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.response,
        timestamp: new Date(),
        intent: response.intent,
        data: response.data,
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error: any) {
      console.error('Error:', error);

      // ✅ Handle authentication error
      if (error.message.includes('đăng nhập')) {
        const errorMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: '❌ ' + error.message + '\n\nVui lòng đăng nhập lại để tiếp tục sử dụng chatbot.',
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, errorMessage]);
        
        // ✅ Reload page after 2 seconds to go to login
        setTimeout(() => {
          window.location.reload();
        }, 2000);
      } else {
        // Generic error
        const errorMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: '❌ Đã có lỗi xảy ra. Vui lòng thử lại sau.\n\n' + error.message,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, errorMessage]);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const clearMessages = () => {
    setMessages([
      {
        id: '1',
        role: 'assistant',
        content: 'Xin chào! Mình là NutriBot 🤖\n\nMình có thể giúp bạn:\n• Tra cứu dinh dưỡng món ăn\n• Gợi ý món phù hợp với mục tiêu\n• Tạo thực đơn cả ngày\n\nBạn cần tư vấn gì không?',
        timestamp: new Date(),
      },
    ]);
  };

  return {
    messages,
    isLoading,
    sendMessage,
    clearMessages,
  };
};