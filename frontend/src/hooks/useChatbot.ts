import { useState, useEffect, useRef } from 'react';
import { chatbotService, ChatMessage } from '../service/chatbot.service';

const MAX_MESSAGES = 50;

interface PendingRequest {
  userMessageId: string;
  userMessage: string;
  timestamp: number;
}

// ✅ Helper function to decode JWT and get user_id
const getUserIdFromToken = (): string | null => {
  try {
    const token = localStorage.getItem('access_token');
    if (!token) return null;

    // Decode JWT token (format: header.payload.signature)
    const payloadBase64 = token.split('.')[1];
    const payload = JSON.parse(atob(payloadBase64));
    
    // Get user_id from token (adjust field name based on your JWT structure)
    return payload.sub || payload.user_id || payload.id;
  } catch (error) {
    console.error('Error decoding token:', error);
    return null;
  }
};

// ✅ Generate user-specific storage keys
const getStorageKeys = () => {
  const userId = getUserIdFromToken();
  
  if (!userId) {
    // Fallback to anonymous keys if no user is logged in
    return {
      historyKey: 'chatbot_history_anonymous',
      pendingKey: 'chatbot_pending_anonymous',
    };
  }

  return {
    historyKey: `chatbot_history_${userId}`,
    pendingKey: `chatbot_pending_${userId}`,
  };
};

const getInitialMessages = (): ChatMessage[] => {
  try {
    const { historyKey } = getStorageKeys();
    const saved = localStorage.getItem(historyKey);
    
    if (saved) {
      const parsed = JSON.parse(saved);
      return parsed.map((msg: any) => ({
        ...msg,
        timestamp: new Date(msg.timestamp)
      }));
    }
  } catch (error) {
    console.error('Error loading chat history:', error);
  }

  return [
    {
      id: '1',
      role: 'assistant',
      content: 'Xin chào! Mình là NutriBot 🤖\n\nMình có thể giúp bạn:\n• Tra cứu dinh dưỡng món ăn\n• Gợi ý món phù hợp với mục tiêu\n• Tạo thực đơn cả ngày\n\nBạn cần tư vấn gì không?',
      timestamp: new Date(),
    },
  ];
};

export const useChatbot = () => {
  const [messages, setMessages] = useState<ChatMessage[]>(getInitialMessages);
  const [isLoading, setIsLoading] = useState(false);
  const [hasNewMessage, setHasNewMessage] = useState(false);
  const requestInProgress = useRef<AbortController | null>(null);
  const currentUserId = useRef<string | null>(getUserIdFromToken());

  // ✅ Check if user has changed (logout/login)
  useEffect(() => {
    const newUserId = getUserIdFromToken();
    
    if (currentUserId.current !== newUserId) {
      // User has changed, reload messages for new user
      currentUserId.current = newUserId;
      setMessages(getInitialMessages());
      setHasNewMessage(false);
    }
  }, []);

  // ✅ Save to user-specific localStorage whenever messages change
  useEffect(() => {
    try {
      const { historyKey } = getStorageKeys();
      const messagesToSave = messages.slice(-MAX_MESSAGES);
      localStorage.setItem(historyKey, JSON.stringify(messagesToSave));
    } catch (error) {
      console.error('Error saving chat history:', error);
    }
  }, [messages]);

  // ✅ Check for pending request on mount
  useEffect(() => {
    checkPendingRequest();
  }, []);

  const checkPendingRequest = async () => {
    try {
      const { pendingKey } = getStorageKeys();
      const pendingStr = localStorage.getItem(pendingKey);
      if (!pendingStr) return;

      const pending: PendingRequest = JSON.parse(pendingStr);
      
      // Check if request is still fresh (within 5 minutes)
      const now = Date.now();
      if (now - pending.timestamp > 5 * 60 * 1000) {
        localStorage.removeItem(pendingKey);
        
        const timeoutMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: '⏱️ Yêu cầu đã hết hạn. Vui lòng gửi lại câu hỏi.',
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, timeoutMessage]);
        return;
      }

      setIsLoading(true);
      await continueRequest(pending);
    } catch (error) {
      console.error('Error checking pending request:', error);
    }
  };

  const continueRequest = async (pending: PendingRequest) => {
    const { pendingKey } = getStorageKeys();
    
    try {
      const response = await chatbotService.sendMessage(pending.userMessage);

      const botMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.response,
        timestamp: new Date(),
        intent: response.intent,
        data: response.data,
      };

      setMessages((prev) => [...prev, botMessage]);
      setHasNewMessage(true);
      
      localStorage.removeItem(pendingKey);
    } catch (error: any) {
      console.error('Error:', error);
      
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: '❌ Đã có lỗi xảy ra khi xử lý yêu cầu của bạn.\n\n' + (error.message || 'Vui lòng thử lại.'),
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
      
      localStorage.removeItem(pendingKey);
    } finally {
      setIsLoading(false);
    }
  };

  const sendMessage = async (content: string) => {
    const { pendingKey } = getStorageKeys();
    const userMessageId = Date.now().toString();
    
    const userMessage: ChatMessage = {
      id: userMessageId,
      role: 'user',
      content,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    // Save pending request to user-specific key
    const pendingRequest: PendingRequest = {
      userMessageId,
      userMessage: content,
      timestamp: Date.now(),
    };
    localStorage.setItem(pendingKey, JSON.stringify(pendingRequest));

    const controller = new AbortController();
    requestInProgress.current = controller;

    try {
      const response = await chatbotService.sendMessage(content);

      if (!controller.signal.aborted) {
        const botMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: response.response,
          timestamp: new Date(),
          intent: response.intent,
          data: response.data,
        };

        setMessages((prev) => [...prev, botMessage]);
        localStorage.removeItem(pendingKey);
      }
    } catch (error: any) {
      console.error('Error:', error);

      if (!controller.signal.aborted) {
        if (error.message.includes('đăng nhập')) {
          const errorMessage: ChatMessage = {
            id: (Date.now() + 1).toString(),
            role: 'assistant',
            content: '❌ ' + error.message + '\n\nVui lòng đăng nhập lại để tiếp tục sử dụng chatbot.',
            timestamp: new Date(),
          };
          setMessages((prev) => [...prev, errorMessage]);
          
          setTimeout(() => {
            window.location.reload();
          }, 2000);
        } else {
          const errorMessage: ChatMessage = {
            id: (Date.now() + 1).toString(),
            role: 'assistant',
            content: '❌ Đã có lỗi xảy ra. Vui lòng thử lại sau.\n\n' + error.message,
            timestamp: new Date(),
          };
          setMessages((prev) => [...prev, errorMessage]);
        }
        
        localStorage.removeItem(pendingKey);
      }
    } finally {
      setIsLoading(false);
      requestInProgress.current = null;
    }
  };

  const clearMessages = () => {
    const { historyKey, pendingKey } = getStorageKeys();
    
    const initialMessage: ChatMessage = {
      id: '1',
      role: 'assistant',
      content: 'Xin chào! Mình là NutriBot 🤖\n\nMình có thể giúp bạn:\n• Tra cứu dinh dưỡng món ăn\n• Gợi ý món phù hợp với mục tiêu\n• Tạo thực đơn cả ngày\n\nBạn cần tư vấn gì không?',
      timestamp: new Date(),
    };
    
    setMessages([initialMessage]);
    localStorage.setItem(historyKey, JSON.stringify([initialMessage]));
    localStorage.removeItem(pendingKey);
    setHasNewMessage(false);
  };

  const markAsRead = () => {
    setHasNewMessage(false);
  };

  return {
    messages,
    isLoading,
    hasNewMessage,
    sendMessage,
    clearMessages,
    markAsRead,
  };
};