import apiClient from './apiClient';

export const BlogService = {
  getFeed: async (params: { page?: number; sort?: string; hashtag?: string }) => {
    const response = await apiClient.get('/blog/feed', { params });
    return response.data;
  },

  createPost: async (content: string, mediaUrls: any[]) => {
    const response = await apiClient.post('/blog/posts', {
      content,
      media: mediaUrls
    });
    return response.data;
  },

  likePost: async (postId: string) => {
    await apiClient.post(`/blog/posts/${postId}/like`);
  },

  // Đặc biệt: Upload file lên ImageKit qua Backend
  uploadMedia: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await apiClient.post('/blog/media/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  }
};