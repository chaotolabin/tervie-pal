import React, { useEffect, useState } from 'react';
import { Heart, MessageCircle, Share2, Bookmark, TrendingUp } from 'lucide-react';
import { Card, CardContent } from '../ui/card';
import { Button } from '../ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '../ui/avatar';
import { Badge } from '../ui/badge';
import { BlogService } from '../../../service/blog.service';
import { toast } from 'sonner';
import PostDetailPage from './PostDetailPage';

interface Author {
  id: string;
  username: string;
  avatar_url?: string;
  streak_count?: number;
}

interface Post {
  id: string;
  content: string;
  created_at: string;
  author: Author;
  likes_count: number;
  comments_count: number;
  is_liked: boolean;
  is_saved: boolean;
  tags?: string[];
}

export default function BlogPage() {
  const [feed, setFeed] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedPost, setSelectedPost] = useState<string | null>(null);

  useEffect(() => {
    const fetchFeed = async () => {
      try {
        const res = await BlogService.getFeed({ limit: 20 });
        setFeed(res.items || []);
      } catch (error) {
        console.error('Lỗi tải feed:', error);
        toast.error('Không thể tải bài viết');
      } finally {
        setLoading(false);
      }
    };
    fetchFeed();
  }, []);

  const handleLikePost = async (postId: string) => {
    const post = feed.find(p => p.id === postId);
    if (!post) return;

    const newIsLiked = !post.is_liked;
    setFeed(feed.map(p => p.id === postId ? {
      ...p,
      is_liked: newIsLiked,
      likes_count: newIsLiked ? p.likes_count + 1 : p.likes_count - 1
    } : p));

    try {
      if (newIsLiked) {
        await BlogService.likePost(postId);
      } else {
        await BlogService.unlikePost(postId);
      }
    } catch (error) {
      // Revert on error
      setFeed(feed.map(p => p.id === postId ? post : p));
      toast.error('Lỗi khi tương tác');
    }
  };

  const handleSavePost = async (postId: string) => {
    const post = feed.find(p => p.id === postId);
    if (!post) return;

    const newIsSaved = !post.is_saved;
    setFeed(feed.map(p => p.id === postId ? { ...p, is_saved: newIsSaved } : p));

    try {
      if (newIsSaved) {
        await BlogService.savePost(postId);
        toast.success('Đã lưu bài viết');
      } else {
        await BlogService.unsavePost(postId);
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
        <h1 className="text-3xl font-bold text-gray-900">Cộng đồng</h1>
        <Button className="bg-gradient-to-r from-pink-500 to-purple-600 text-white">
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
            <MessageCircle className="size-12 mx-auto mb-3 opacity-50" />
            <p>Chưa có bài viết nào</p>
          </div>
        ) : (
          feed.map((post) => {
            // Skip posts without author data
            if (!post.author) {
              console.warn('Post missing author:', post.id);
              return null;
            }
            
            return (
              <Card key={post.id} className="hover:shadow-md transition-shadow cursor-pointer">
                <CardContent className="pt-6">
                  {/* Author Info */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <Avatar className="size-10 border-2 border-pink-100">
                        <AvatarImage src={post.author?.avatar_url} />
                        <AvatarFallback className="bg-gradient-to-r from-pink-500 to-purple-600 text-white font-bold">
                          {post.author?.username?.charAt(0).toUpperCase() || 'U'}
                        </AvatarFallback>
                      </Avatar>
                      <div>
                        <div className="flex items-center gap-2">
                          <p className="font-bold text-gray-900">{post.author?.username || 'Unknown'}</p>
                          {post.author?.streak_count && post.author.streak_count > 0 && (
                            <Badge variant="outline" className="text-xs bg-orange-50 text-orange-600 border-orange-200">
                              {post.author.streak_count} ngày 🔥
                            </Badge>
                          )}
                        </div>
                        <p className="text-xs text-gray-500">{formatDate(post.created_at)}</p>
                      </div>
                    </div>
                  </div>

                {/* Content */}
                <div className="mb-4" onClick={() => setSelectedPost(post.id)}>
                  <p className="text-gray-800 leading-relaxed whitespace-pre-wrap">{post.content}</p>
                </div>

                {/* Tags */}
                {post.tags && post.tags.length > 0 && (
                  <div className="flex flex-wrap gap-2 mb-4">
                    {post.tags.map((tag, idx) => (
                      <Badge key={idx} variant="secondary" className="bg-blue-50 text-blue-600 hover:bg-blue-100 cursor-pointer text-xs">
                        #{tag}
                      </Badge>
                    ))}
                  </div>
                )}

                {/* Actions */}
                <div className="flex items-center gap-6 pt-3 border-t">
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
                    <span className="font-medium">{post.likes_count}</span>
                  </Button>

                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setSelectedPost(post.id)}
                    className="text-gray-600 hover:bg-blue-50 hover:text-blue-600"
                  >
                    <MessageCircle className="size-5 mr-2" />
                    <span className="font-medium">{post.comments_count || 0}</span>
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

                  <Button variant="ghost" size="sm" className="text-gray-600 hover:bg-gray-100">
                    <Share2 className="size-5" />
                  </Button>
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