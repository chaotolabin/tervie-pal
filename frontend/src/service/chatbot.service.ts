const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  intent?: string;
  data?: any;
}

export interface ChatResponse {
  response: string;
  intent: string;
  data?: any;
}

export const chatbotService = {
  async sendMessage(message: string): Promise<ChatResponse> {
    try {
      // ✅ Get access token from localStorage
      const token = localStorage.getItem('access_token');
      
      if (!token) {
        throw new Error('Bạn cần đăng nhập để sử dụng chatbot');
      }

      const response = await fetch(`${API_BASE_URL}/api/v1/chatbot/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,  // ✅ Send token
        },
        body: JSON.stringify({ message }),
      });

      // ✅ Handle authentication errors
      if (response.status === 401) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        throw new Error('Phiên đăng nhập hết hạn. Vui lòng đăng nhập lại.');
      }

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Chatbot API error:', error);
      throw error;
    }
  },
};