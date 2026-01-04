import React, { useState, useEffect } from 'react';
import { ArrowLeft, Heart, MessageCircle, Share2, Send, MoreVertical, Loader2, Bookmark } from 'lucide-react';
import { Card, CardContent, CardHeader } from '../ui/card';
import { Button } from '../ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '../ui/avatar';
import { Badge } from '../ui/badge';
import { Textarea } from '../ui/textarea';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '../ui/dropdown-menu';
import { toast } from 'sonner';
import { BlogService } from '../../../service/blog.service';

// --- Interfaces khớp với Backend ---
interface Author {
  id: string;
  username: string;
  avatar_url?: string;
  streak_count?: number; // Nếu backend có trả về streak của author
}

interface Comment {
  id: number;
  content: string;
  created_at: string;
  author: Author;
  likes_count: number;
  is_liked: boolean;
}

interface PostDetail {
  id: string;
  content: string;
  created_at: string;
  author: Author;
  likes_count: number;
  comments_count: number;
  is_liked: boolean;
  is_saved: boolean;
  tags?: string[];
  media?: { url: string; type: 'image' | 'video' }[];
}

interface PostDetailPageProps {
  onBack: () => void;
  postId?: string; // ID bài viết được truyền từ trang Feed
}

export default function PostDetailPage({ onBack, postId }: PostDetailPageProps) {
  const [post, setPost] = useState<PostDetail | null>(null);
  const [comments, setComments] = useState<Comment[]>([]);
  const [newComment, setNewComment] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  // 1. Fetch dữ liệu bài viết và bình luận
  useEffect(() => {
    if (!postId) return;

    const fetchData = async () => {
      setLoading(true);
      try {
        // Sử dụng BlogService để fetch post detail
        const postData = await BlogService.getPost(postId);
        setPost(postData);
        setComments([]); // Comments feature not implemented in backend
      } catch (error) {
        console.error("Lỗi tải bài viết:", error);
        toast.error("Không thể tải bài viết này");
        onBack(); // Quay lại nếu lỗi
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [postId, onBack]);

  // 2. Xử lý Like bài viết
  const handleLikePost = async () => {
    if (!post || !postId) return;
    
    // Optimistic UI Update (Cập nhật giao diện ngay lập tức)
    const originalPost = { ...post };
    const newIsLiked = !post.is_liked;
    
    setPost({
      ...post,
      is_liked: newIsLiked,
      likes_count: newIsLiked ? post.likes_count + 1 : post.likes_count - 1
    });

    try {
      if (newIsLiked) {
        await BlogService.likePost(postId);
        toast.success("Đã thích bài viết");
      } else {
        await BlogService.unlikePost(postId);
      }
    } catch (error) {
      // Revert nếu lỗi
      setPost(originalPost);
      console.error("Like error:", error);
      toast.error("Lỗi khi tương tác");
    }
  };

  // 2b. Xử lý Save bài viết
  const handleSavePost = async () => {
    if (!post || !postId) return;
    
    // Optimistic UI Update
    const originalPost = { ...post };
    const newIsSaved = !post.is_saved;
    
    setPost({
      ...post,
      is_saved: newIsSaved
    });

    try {
      if (newIsSaved) {
        await BlogService.savePost(postId);
        toast.success("Đã lưu bài viết");
      } else {
        await BlogService.unsavePost(postId);
        toast.success("Đã bỏ lưu bài viết");
      }
    } catch (error) {
      // Revert nếu lỗi
      setPost(originalPost);
      console.error("Save error:", error);
      toast.error("Lỗi khi lưu bài viết");
    }
  };

  // 3. Xử lý Gửi bình luận
  const handleSubmitComment = async () => {
    if (!newComment.trim() || !post) {
      toast.error('Vui lòng nhập nội dung');
      return;
    }

    setSubmitting(true);
    try {
      // Comments feature not implemented in backend
      toast.error('Tính năng bình luận chưa được triển khai');
    } catch (error) {
      toast.error('Không thể gửi bình luận');
    } finally {
      setSubmitting(false);
    }
  };

  // Utility format ngày tháng
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('vi-VN', {
      hour: '2-digit',
      minute: '2-digit',
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-[50vh]">
        <Loader2 className="size-8 animate-spin text-pink-600" />
      </div>
    );
  }

  if (!post) return null;

  return (
    <div className="space-y-6 max-w-3xl mx-auto pb-10">
      {/* Back Button */}
      <Button variant="ghost" onClick={onBack} className="hover:bg-gray-100">
        <ArrowLeft className="size-4 mr-2" />
        Quay lại Feed
      </Button>

      {/* Post Card */}
      <Card className="border-none shadow-md overflow-hidden">
        <CardHeader className="pb-4">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-3">
              <Avatar className="size-12 border-2 border-pink-100">
                <AvatarImage src={post.author.avatar_url} />
                <AvatarFallback className="bg-gradient-to-r from-pink-500 to-purple-600 text-white font-bold">
                  {post.author.username.charAt(0).toUpperCase()}
                </AvatarFallback>
              </Avatar>
              <div>
                <div className="flex items-center gap-2">
                  <p className="font-bold text-gray-900">{post.author.username}</p>
                  {post.author.streak_count && (
                    <Badge variant="outline" className="text-xs bg-orange-50 text-orange-600 border-orange-200">
                      {post.author.streak_count} ngày 🔥
                    </Badge>
                  )}
                </div>
                <p className="text-xs text-gray-500">{formatDate(post.created_at)}</p>
              </div>
            </div>

            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" className="text-gray-400">
                  <MoreVertical className="size-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem>Sao chép liên kết</DropdownMenuItem>
                <DropdownMenuItem className="text-red-600">Báo cáo bài viết</DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </CardHeader>

        <CardContent className="space-y-4">
          {/* Content */}
          <div className="prose prose-sm max-w-none">
            <p className="whitespace-pre-wrap text-gray-800 text-base leading-relaxed">{post.content}</p>
          </div>

          {/* Media (Images/Videos) */}
          {post.media && post.media.length > 0 && (
            <div className={`grid gap-2 ${post.media.length > 1 ? 'grid-cols-2' : 'grid-cols-1'}`}>
              {post.media.map((item, idx) => (
                <div key={idx} className="rounded-xl overflow-hidden bg-gray-100 border">
                  {item.type === 'image' ? (
                     <img src={item.url} alt="Post content" className="w-full h-full object-cover max-h-[500px]" />
                  ) : (
                     <video src={item.url} controls className="w-full h-full object-cover" />
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Tags */}
          {post.tags && post.tags.length > 0 && (
            <div className="flex flex-wrap gap-2 pt-2">
              {post.tags.map((tag, idx) => (
                <Badge key={idx} variant="secondary" className="bg-blue-50 text-blue-600 hover:bg-blue-100 transition-colors">
                  #{tag}
                </Badge>
              ))}
            </div>
          )}

          {/* Actions Bar */}
          <div className="flex items-center gap-6 pt-4 border-t border-gray-100">
            <Button
              variant="ghost"
              size="sm"
              onClick={handleLikePost}
              className={`hover:bg-pink-50 ${post.is_liked ? 'text-pink-600' : 'text-gray-600'}`}
            >
              <Heart className={`size-5 mr-2 ${post.is_liked ? 'fill-pink-600' : ''}`} />
              <span className="font-medium">{post.likes_count}</span>
            </Button>
            
            <Button variant="ghost" size="sm" className="text-gray-600 hover:bg-blue-50 hover:text-blue-600">
              <MessageCircle className="size-5 mr-2" />
              <span className="font-medium">{post.comments_count}</span>
            </Button>
            
            <Button
              variant="ghost"
              size="sm"
              onClick={handleSavePost}
              className={`ml-auto ${post.is_saved ? 'text-blue-600' : 'text-gray-600'} hover:bg-blue-50 hover:text-blue-600`}
            >
              <Bookmark className={`size-5 ${post.is_saved ? 'fill-blue-600' : ''}`} />
            </Button>
            
            <Button variant="ghost" size="sm" className="text-gray-600 hover:bg-gray-100">
              <Share2 className="size-5" />
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Comments Section */}
      <Card className="border-none shadow-sm">
        <CardHeader className="pb-2 border-b">
          <h3 className="font-semibold text-lg text-gray-800">Bình luận</h3>
        </CardHeader>
        <CardContent className="space-y-6 pt-6">
          {/* Add Comment Input */}
          <div className="flex gap-3">
            <Avatar className="size-8 mt-1">
              <AvatarFallback className="bg-gray-200">Me</AvatarFallback>
            </Avatar>
            <div className="flex-1 space-y-3">
              <Textarea
                placeholder="Viết bình luận của bạn..."
                value={newComment}
                onChange={(e) => setNewComment(e.target.value)}
                rows={2}
                className="resize-none bg-gray-50 border-gray-200 focus:bg-white transition-all"
              />
              <div className="flex justify-end">
                <Button
                  onClick={handleSubmitComment}
                  disabled={submitting || !newComment.trim()}
                  className="bg-gradient-to-r from-pink-500 to-purple-600 text-white shadow-md hover:shadow-lg transition-all"
                  size="sm"
                >
                  {submitting ? <Loader2 className="size-4 animate-spin mr-2" /> : <Send className="size-4 mr-2" />}
                  Gửi
                </Button>
              </div>
            </div>
          </div>

          {/* Comments List */}
          <div className="space-y-6">
            {comments.length === 0 ? (
               <div className="text-center py-8 text-gray-400 italic">
                 Chưa có bình luận nào. Hãy là người đầu tiên!
               </div>
            ) : (
              comments.map((comment) => (
                <div key={comment.id} className="flex gap-3 animate-in fade-in slide-in-from-bottom-2 duration-300">
                  <Avatar className="size-9 border border-gray-100 flex-shrink-0">
                    <AvatarImage src={comment.author.avatar_url} />
                    <AvatarFallback className="bg-blue-100 text-blue-600 text-xs font-bold">
                      {comment.author.username.charAt(0).toUpperCase()}
                    </AvatarFallback>
                  </Avatar>

                  <div className="flex-1">
                    <div className="bg-gray-50 rounded-2xl p-3 px-4 inline-block min-w-[200px]">
                      <div className="flex justify-between items-baseline mb-1">
                        <span className="font-bold text-sm text-gray-900 mr-2">{comment.author.username}</span>
                        <span className="text-[10px] text-gray-400">{formatDate(comment.created_at)}</span>
                      </div>
                      <p className="text-sm text-gray-700 whitespace-pre-wrap">{comment.content}</p>
                    </div>
                    
                    <div className="flex items-center gap-4 mt-1 ml-2 text-xs text-gray-500 font-medium">
                      <button className="hover:text-pink-600 transition-colors">Thích</button>
                      <button className="hover:text-blue-600 transition-colors">Trả lời</button>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}