import React, { useEffect, useState } from 'react';
import { Heart, Bookmark, TrendingUp } from 'lucide-react';
import { Card, CardContent } from '../ui/card';
import { Button } from '../ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '../ui/avatar';
import { Badge } from '../ui/badge';
import { BlogService } from '../../../service/blog.service';
import { toast } from 'sonner';
import PostDetailPage from './PostDetailPage';
import CreatePostPage from './CreatePost';

interface Author {
  id: string;
  username: string;
  avatar_url?: string;
  streak_count?: number;
}

interface Post {
  id: number;
  user_id: string;
  content_text: string;
  title?: string;
  created_at: string;
  updated_at: string;
  author?: Author; // Optional vì backend không trả về
  like_count: number;
  save_count: number;
  is_liked: boolean;
  is_saved: boolean;
  hashtags?: string[];
  media?: Array<{
    id: string;
    url: string;
    media_type: string;
    width?: number;
    height?: number;
  }>;
}

export default function BlogPage() {
  const [feed, setFeed] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedPost, setSelectedPost] = useState<string | null>(null);
  const [showCreatePost, setShowCreatePost] = useState(false);

  useEffect(() => {
    const fetchFeed = async () => {
      try {
        const res = await BlogService.getFeed({ limit: 20 });
        console.log('Feed response:', res);
        console.log('Feed items:', res.items);
        if (res.items && res.items.length > 0) {
          console.log('First post sample:', res.items[0]);
        }
        setFeed(res.items || []);
      } catch (error) {
        console.error('Lỗi tải feed:', error);
        toast.error('Không thể tải bài viết');
      } finally {
        setLoading(false);
      }
    };
    
    if (!showCreatePost) {
      fetchFeed();
    }
  }, [showCreatePost]);

  const handleLikePost = async (postId: number) => {
    const post = feed.find(p => p.id === postId);
    if (!post) return;

    const newIsLiked = !post.is_liked;
    setFeed(feed.map(p => p.id === postId ? {
      ...p,
      is_liked: newIsLiked,
      like_count: newIsLiked ? p.like_count + 1 : p.like_count - 1
    } : p));

    try {
      if (newIsLiked) {
        await BlogService.likePost(String(postId));
      } else {
        await BlogService.unlikePost(String(postId));
      }
    } catch (error) {
      // Revert on error
      setFeed(feed.map(p => p.id === postId ? post : p));
      toast.error('Lỗi khi tương tác');
    }
  };

  const handleSavePost = async (postId: number) => {
    const post = feed.find(p => p.id === postId);
    if (!post) return;

    const newIsSaved = !post.is_saved;
    setFeed(feed.map(p => p.id === postId ? { ...p, is_saved: newIsSaved } : p));

    try {
      if (newIsSaved) {
        await BlogService.savePost(String(postId));
        toast.success('Đã lưu bài viết');
      } else {
        await BlogService.unsavePost(String(postId));
      }
    } catch (error) {
      setFeed(feed.map(p => p.id === postId ? post : p));
      toast.error('Lỗi khi lưu bài viết');
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diff = Math.floor((now.getTime() - date.getTime()) / 1000);

    if (diff < 60) return 'Vừa xong';
    if (diff < 3600) return `${Math.floor(diff / 60)} phút trước`;
    if (diff < 86400) return `${Math.floor(diff / 3600)} giờ trước`;
    if (diff < 604800) return `${Math.floor(diff / 86400)} ngày trước`;
    
    return date.toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit' });
  };

  if (selectedPost) {
    return <PostDetailPage postId={selectedPost} onBack={() => setSelectedPost(null)} />;
  }

  if (showCreatePost) {
    return (
      <CreatePostPage 
        onBack={() => setShowCreatePost(false)}
        onPostCreated={() => {
          setShowCreatePost(false);
          setLoading(true);
        }}
      />
    );
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-[50vh]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-pink-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto py-6 px-4">
      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Tervie Blog</h1>
        <Button 
          onClick={() => setShowCreatePost(true)}
          className="bg-gradient-to-r from-pink-500 to-purple-600 text-white"
        >
          Tạo bài viết
        </Button>
      </div>

      {/* Filter Tabs */}
      <div className="flex gap-4 mb-6 pb-4 border-b overflow-x-auto">
        <button className="flex items-center gap-2 px-4 py-2 rounded-full bg-pink-50 text-pink-600 font-medium whitespace-nowrap">
          <TrendingUp className="size-4" />
          Xu hướng
        </button>
        <button className="px-4 py-2 rounded-full text-gray-600 hover:bg-gray-100 whitespace-nowrap">
          Đang theo dõi
        </button>
      </div>

      {/* Trending Topics */}
      <Card className="mb-6 border-pink-100">
        <CardContent className="pt-6">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="size-5 text-pink-600" />
            <h3 className="font-bold text-gray-900">Chủ đề nổi bật</h3>
          </div>
          <div className="flex flex-wrap gap-2">
            {['#Giảm cân', '#Meal prep', '#Tập gym', '#Ăn chay', '#HIIT'].map(tag => (
              <Badge key={tag} variant="secondary" className="bg-pink-50 text-pink-600 hover:bg-pink-100 cursor-pointer">
                {tag}
              </Badge>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Posts Feed */}
      <div className="space-y-4">
        {feed.length === 0 ? (
          <div className="text-center py-12 text-gray-400">
            <p>Chưa có bài viết nào</p>
          </div>
        ) : (
          feed.map((post) => {
            return (
              <Card key={post.id} className="hover:shadow-md transition-shadow overflow-hidden">
                <CardContent className="p-0">
                  {/* Title - Clickable */}
                  {post.title && (
                    <div 
                      className="p-6 pb-4 cursor-pointer hover:bg-gray-50 transition-colors"
                      onClick={() => setSelectedPost(String(post.id))}
                    >
                      <h2 className="font-bold text-2xl text-gray-900 leading-tight">
                        {post.title}
                      </h2>
                    </div>
                  )}

                  {/* Media Preview - Clickable */}
                  {post.media && post.media.length > 0 && (
                    <div 
                      className="cursor-pointer"
                      onClick={() => setSelectedPost(String(post.id))}
                    >
                      {post.media[0].media_type === 'video' ? (
                        <video 
                          src={post.media[0].url} 
                          className="w-full aspect-video object-cover"
                          poster={post.media[0].url}
                        />
                      ) : (
                        <img 
                          src={post.media[0].url} 
                          alt={post.title} 
                          className="w-full aspect-video object-cover"
                        />
                      )}
                    </div>
                  )}

                  <div className="p-6 pt-4">
                    {/* Tags */}
                    {post.hashtags && post.hashtags.length > 0 && (
                      <div className="flex flex-wrap gap-2 mb-4">
                        {post.hashtags.map((tag, idx) => (
                          <Badge key={idx} variant="secondary" className="bg-blue-50 text-blue-600 hover:bg-blue-100 cursor-pointer">
                            #{tag}
                          </Badge>
                        ))}
                      </div>
                    )}

                    {/* Meta Info */}
                    <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
                      <div className="flex items-center gap-2">
                        <Avatar className="size-6">
                          <AvatarFallback className="bg-gradient-to-r from-pink-500 to-purple-600 text-white text-xs font-bold">
                            {post.user_id?.substring(0, 2).toUpperCase() || 'U'}
                          </AvatarFallback>
                        </Avatar>
                        <span>User {post.user_id?.substring(0, 8)}</span>
                        <span>•</span>
                        <span>{formatDate(post.created_at)}</span>
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center gap-6 pt-4 border-t">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleLikePost(post.id);
                        }}
                        className={`hover:bg-pink-50 ${post.is_liked ? 'text-pink-600' : 'text-gray-600'}`}
                      >
                        <Heart className={`size-5 mr-2 ${post.is_liked ? 'fill-pink-600' : ''}`} />
                        <span className="font-medium">{post.like_count}</span>
                      </Button>

                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleSavePost(post.id);
                        }}
                        className={`ml-auto ${post.is_saved ? 'text-blue-600' : 'text-gray-600'} hover:bg-blue-50`}
                      >
                        <Bookmark className={`size-5 ${post.is_saved ? 'fill-blue-600' : ''}`} />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })
        )}
      </div>
    </div>
  );
}