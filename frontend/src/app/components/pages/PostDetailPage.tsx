import React, { useState, useEffect } from 'react';
import { ArrowLeft, Heart, MoreVertical, Loader2, Bookmark, Trash2, Edit } from 'lucide-react';
import { Card, CardContent, CardHeader } from '../ui/card';
import { Button } from '../ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '../ui/avatar';
import { Badge } from '../ui/badge';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '../ui/dropdown-menu';
import { toast } from 'sonner';
import { BlogService } from '../../../service/blog.service';

// --- Interfaces khớp với Backend ---
interface PostDetail {
  id: number;
  user_id: string;
  full_name: string;
  title?: string;
  content_text: string;
  created_at: string;
  updated_at?: string;
  like_count: number;
  save_count: number;
  is_liked: boolean;
  is_saved: boolean;
  hashtags?: string[];
  media?: Array<{
    id: number;
    url: string;
    media_type: string;
    mime_type?: string;
    width?: number;
    height?: number;
    size_bytes?: number;
    sort_order?: number;
  }>;
}

interface PostDetailPageProps {
  onBack: () => void;
  postId?: string;
  currentUserId?: string | null;
  onPostDeleted?: () => void;
  onEditPost?: (post: PostDetail) => void;
}

export default function PostDetailPage({ onBack, postId, currentUserId, onPostDeleted, onEditPost }: PostDetailPageProps) {
  const [post, setPost] = useState<PostDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState(false);

  const isAuthor = post && currentUserId && post.user_id === currentUserId;
  console.log('[PostDetailPage] isAuthor check:', { postUserId: post?.user_id, currentUserId, isAuthor });

  // 1. Fetch dữ liệu bài viết và bình luận
  useEffect(() => {
    if (!postId) return;

    const fetchData = async () => {
      setLoading(true);
      try {
        const postData = await BlogService.getPost(postId);
        setPost(postData);
      } catch (error) {
        console.error("Lỗi tải bài viết:", error);
        toast.error("Không thể tải bài viết này");
        onBack();
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
      like_count: newIsLiked ? post.like_count + 1 : post.like_count - 1
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

  // Handle delete post
  const handleDeletePost = async () => {
    console.log('[PostDetailPage] handleDeletePost called:', { postId, isAuthor, currentUserId });
    
    if (!post || !postId || !isAuthor) {
      console.log('[PostDetailPage] Delete blocked - missing requirements');
      return;
    }
    
    const confirmDelete = window.confirm('Bạn có chắc chắn muốn xóa bài viết này?');
    if (!confirmDelete) {
      console.log('[PostDetailPage] User cancelled deletion');
      return;
    }

    setDeleting(true);
    try {
      console.log('[PostDetailPage] Calling BlogService.deletePost...');
      await BlogService.deletePost(postId);
      console.log('[PostDetailPage] Post deleted successfully');
      toast.success('Đã xóa bài viết');
      onPostDeleted?.();
      onBack();
    } catch (error) {
      console.error('[PostDetailPage] Delete error:', error);
      toast.error('Lỗi khi xóa bài viết');
    } finally {
      setDeleting(false);
    }
  };

  // Handle edit post
  const handleEditPost = () => {
    console.log('[PostDetailPage] Edit button clicked for post:', postId);
    if (!post || !isAuthor) {
      console.log('[PostDetailPage] Edit blocked - not author or post missing');
      toast.error('Bạn không có quyền chỉnh sửa bài viết này');
      return;
    }
    if (onEditPost) {
      onEditPost(post);
    } else {
      toast.info('Tính năng chỉnh sửa đang phát triển');
    }
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
          <div className="flex items-start justify-between mb-6">
            <div className="flex items-center gap-3">
              <Avatar className="size-12 border-2 border-pink-100">
                <AvatarFallback className="bg-gradient-to-r from-pink-500 to-purple-600 text-white font-bold">
                  {post.full_name?.substring(0, 2).toUpperCase() || 'U'}
                </AvatarFallback>
              </Avatar>
              <div>
                <p className="font-bold text-gray-900">{post.full_name?.substring(0, 8)}</p>
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
                {isAuthor && (
                  <>
                    <DropdownMenuItem onSelect={handleDeletePost} disabled={deleting} className="text-red-600">
                      <Trash2 className="size-4 mr-2" />
                      {deleting ? 'Đang xóa...' : 'Xóa bài viết'}
                    </DropdownMenuItem>
                    <DropdownMenuItem onSelect={handleEditPost}>
                      <Edit className="size-4 mr-2" />
                      Chỉnh sửa bài viết
                    </DropdownMenuItem>
                  </>
                )}
                <DropdownMenuItem>Sao chép liên kết</DropdownMenuItem>
                {!isAuthor && (
                  <DropdownMenuItem className="text-red-600">Báo cáo bài viết</DropdownMenuItem>
                )}
              </DropdownMenuContent>
            </DropdownMenu>
          </div>

          {/* Blog Title */}
          <h1 className="text-4xl font-bold text-gray-900 leading-tight mb-6">
            {post.title || "Untitled Post"}
          </h1>
        </CardHeader>

        <CardContent className="space-y-6">
          {/* Media (Images/Videos) - Blog format: media first */}
          {post.media && post.media.length > 0 && (
            <div className={`grid gap-3 ${post.media.length > 1 ? 'grid-cols-2' : 'grid-cols-1'}`}>
              {post.media.map((item, idx) => (
                <div key={idx} className="overflow-hidden bg-gray-100 border shadow-sm">
                  {item.media_type === 'image' ? (
                     <img src={item.url} alt="Post content" className="w-full h-full object-cover max-h-[600px]" />
                  ) : (
                     <video src={item.url} controls className="w-full h-full object-cover max-h-[600px]" />
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Content - After media like a blog */}
          <div className="prose prose-lg max-w-none">
            <p className="whitespace-pre-wrap text-gray-800 text-lg leading-relaxed">{post.content_text}</p>
          </div>

          {/* Tags */}
          {post.hashtags && post.hashtags.length > 0 && (
            <div className="flex flex-wrap gap-2 pt-2">
              {post.hashtags.map((tag, idx) => (
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
              <span className="font-medium">{post.like_count}</span>
            </Button>
            
            <Button
              variant="ghost"
              size="sm"
              onClick={handleSavePost}
              className={`ml-auto ${post.is_saved ? 'text-blue-600' : 'text-gray-600'} hover:bg-blue-50 hover:text-blue-600`}
            >
              <Bookmark className={`size-5 ${post.is_saved ? 'fill-blue-600' : ''}`} />
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}