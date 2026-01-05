import apiClient from './apiClient';

export const BlogService = {
  getFeed: async (params: { page?: number; sort?: string; hashtag?: string; author_id?: string; saved?: boolean, limit?: number }) => {
    const response = await apiClient.get('/blog/feed', { params });
    return response.data;
  },

  getPost: async (postId: string) => {
    const response = await apiClient.get(`/blog/posts/${postId}`);
    return response.data;
  },

  createPost: async (data: { 
    content_text: string; 
    media?: Array<{ url: string; media_type: string; sort_order?: number }>; 
    hashtags?: string[]; 
    title?: string 
  }) => {
    const response = await apiClient.post('/blog/posts', data);
    return response.data;
  },

  updatePost: async (postId: string, data: { 
    content_text?: string; 
    media?: Array<{ url: string; media_type: string; mime_type?: string; width?: number; height?: number; size_bytes?: number; sort_order?: number }>; 
    hashtags?: string[]; 
    title?: string 
  }) => {
    const response = await apiClient.patch(`/blog/posts/${postId}`, data);
    return response.data;
  },

  deletePost: async (postId: string): Promise<void> => {
    await apiClient.delete(`/blog/posts/${postId}`);
  },

  likePost: async (postId: string) => {
    await apiClient.post(`/blog/posts/${postId}/like`);
  },

  unlikePost: async (postId: string) => {
    await apiClient.delete(`/blog/posts/${postId}/like`);
  },

  savePost: async (postId: string) => {
    await apiClient.post(`/blog/posts/${postId}/save`);
  },

  unsavePost: async (postId: string) => {
    await apiClient.delete(`/blog/posts/${postId}/save`);
  },

  searchHashtags: async (query: string, limit: number = 20) => {
    const response = await apiClient.get('/blog/hashtags/search', {
      params: { q: query, limit }
    });
    return response.data;
  },

  getPostsByHashtag: async (hashtagName: string, limit: number = 20, cursor?: string) => {
    const response = await apiClient.get(`/blog/hashtags/${hashtagName}/posts`, {
      params: { limit, cursor }
    });
    return response.data;
  },

  // Upload file lên ImageKit qua Backend
  uploadMedia: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await apiClient.post('/blog/media/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  },

  uploadMultipleMedia: async (files: File[]) => {
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));
    const response = await apiClient.post('/blog/media/upload-multiple', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  }
};