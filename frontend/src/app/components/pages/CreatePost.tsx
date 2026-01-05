import { useState, useRef } from 'react';
import { 
  Image as ImageIcon, 
  X, 
  Loader2, 
  Hash, 
  Send, 
  Video, 
  ArrowLeft 
} from 'lucide-react';
import { Button } from '../ui/button';
import { Textarea } from '../ui/textarea';
import { Input } from '../ui/input';
import { Card, CardContent } from '../ui/card';
import { Badge } from '../ui/badge';
import { toast } from 'sonner';
import { BlogService } from '../../../service/blog.service';

interface MediaItem {
  url: string;
  file_id?: string;
  file_name?: string;
  media_type: string;
  mime_type?: string;
  width?: number;
  height?: number;
  size_bytes?: number;
  sort_order?: number;
}

interface CreatePostPageProps {
  onBack: () => void;
  onPostCreated?: () => void;
  editMode?: boolean;
  existingPost?: {
    id: number;
    title?: string;
    content_text: string;
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
  };
}

export default function CreatePostPage({ onBack, onPostCreated, editMode = false, existingPost }: CreatePostPageProps) {
  
  const [content, setContent] = useState(existingPost?.content_text || '');
  const [title, setTitle] = useState(existingPost?.title || '');
  const [tags, setTags] = useState<string[]>(existingPost?.hashtags || []);
  const [tagInput, setTagInput] = useState('');
  const [mediaList, setMediaList] = useState<MediaItem[]>(
    existingPost?.media?.map(m => ({
      url: m.url,
      media_type: m.media_type,
      mime_type: m.mime_type,
      width: m.width,
      height: m.height,
      size_bytes: m.size_bytes,
      sort_order: m.sort_order
    })) || []
  );
  
  const [isUploading, setIsUploading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleKeyDownTag = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault();
      const newTag = tagInput.trim().replace('#', '');
      if (newTag && !tags.includes(newTag)) {
        setTags([...tags, newTag]);
        setTagInput('');
      }
    }
  };

  const removeTag = (tagToRemove: string) => {
    setTags(tags.filter(tag => tag !== tagToRemove));
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setIsUploading(true);
      const files = Array.from(e.target.files);

      try {

        const uploadPromises = files.map(file => BlogService.uploadMedia(file));
        const results = await Promise.all(uploadPromises);
        
        // Lưu toàn bộ metadata từ ImageKit
        const newMedia = results.map(res => ({
          url: res.url,
          file_id: res.file_id,
          file_name: res.file_name,
          media_type: res.media_type,
          mime_type: res.mime_type,
          width: res.width,
          height: res.height,
          size_bytes: res.size_bytes,
          sort_order: res.sort_order
        }));

        setMediaList([...mediaList, ...newMedia]);
        toast.success(`Đã tải lên ${files.length} file`);
      } catch (error) {
        console.error(error);
        toast.error('Lỗi khi tải lên file ảnh/video');
      } finally {
        setIsUploading(false);
        if (fileInputRef.current) fileInputRef.current.value = '';
      }
    }
  };

  const removeMedia = (index: number) => {
    setMediaList(mediaList.filter((_, i) => i !== index));
  };

  const handleSubmit = async () => {
    if (!title.trim()) {
      toast.error('Vui lòng nhập tiêu đề bài viết');
      return;
    }

    if (!content.trim() && mediaList.length === 0) {
      toast.error('Vui lòng nhập nội dung hoặc thêm ảnh/video');
      return;
    }

    setIsSubmitting(true);
    try {
      // Gửi đầy đủ media metadata cho backend
      const mediaPayload = mediaList.map((m, index) => ({
        url: m.url,
        file_id: m.file_id,
        file_name: m.file_name,
        media_type: m.media_type,
        mime_type: m.mime_type,
        width: m.width,
        height: m.height,
        size_bytes: m.size_bytes,
        sort_order: index
      }));

      const payload = {
        title: title.trim(),
        content_text: content.trim(),
        hashtags: tags,
        media: mediaPayload
      };

      console.log(`${editMode ? 'Updating' : 'Creating'} post with payload:`, payload);

      if (editMode && existingPost) {
        // Update existing post
        await BlogService.updatePost(existingPost.id.toString(), payload);
        toast.success('Cập nhật bài viết thành công!');
      } else {
        // Create new post
        await BlogService.createPost(payload);
        toast.success('Đăng bài thành công!');
      }
      
      onPostCreated?.();
      onBack();
    } catch (error: any) {
      console.error(`${editMode ? 'Update' : 'Create'} post error:`, error);
      console.error('Error response:', error.response?.data);
      
      // Handle error message properly
      let errorMsg = editMode ? 'Cập nhật bài viết thất bại. Vui lòng thử lại.' : 'Đăng bài thất bại. Vui lòng thử lại.';
      if (error.response?.data?.detail) {
        if (typeof error.response.data.detail === 'string') {
          errorMsg = error.response.data.detail;
        } else if (Array.isArray(error.response.data.detail)) {
          errorMsg = error.response.data.detail.map((e: any) => e.msg || e.message || String(e)).join(', ');
        } else {
          errorMsg = JSON.stringify(error.response.data.detail);
        }
      }
      toast.error(errorMsg);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6 pb-10">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={onBack}>
          <ArrowLeft className="size-5" />
        </Button>
        <h1 className="text-2xl font-bold">{editMode ? 'Chỉnh sửa bài viết' : 'Tạo bài viết mới'}</h1>
      </div>

      <Card className="border-none shadow-md">
        <CardContent className="p-6 space-y-6">
          
          {/* Title Input */}
          <div className="space-y-2">
            <Input
              placeholder="Tiêu đề bài viết..."
              className="text-xl font-semibold border-none focus-visible:ring-0 p-0 h-auto"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
          </div>

          {/* Content Input */}
          <div className="space-y-2">
            <Textarea
              placeholder="Bạn đang nghĩ gì? Chia sẻ hành trình tập luyện của bạn..."
              className="min-h-[150px] text-lg border-none focus-visible:ring-0 resize-none p-0"
              value={content}
              onChange={(e) => setContent(e.target.value)}
            />
          </div>

          {/* Media Preview Grid */}
          {mediaList.length > 0 && (
            <div className="grid grid-cols-2 gap-2">
              {mediaList.map((media, idx) => (
                <div key={idx} className="relative group overflow-hidden bg-gray-100 aspect-video">
                  {media.media_type === 'video' ? (
                    <video src={media.url} className="w-full h-full object-cover" controls />
                  ) : (
                    <img src={media.url} alt="preview" className="w-full h-full object-cover" />
                  )}
                  
                  {/* Remove Button */}
                  <button
                    onClick={() => removeMedia(idx)}
                    className="absolute top-2 right-2 p-1 bg-black/50 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    <X className="size-4" />
                  </button>
                </div>
              ))}
            </div>
          )}

          {/* Upload Loading State */}
          {isUploading && (
            <div className="flex items-center justify-center p-4 bg-gray-50 text-sm text-gray-500">
              <Loader2 className="size-4 animate-spin mr-2" />
              Đang tải lên media...
            </div>
          )}

          <div className="border-t pt-4 space-y-4">
            {/* Tags Input */}
            <div className="space-y-3">
              <div className="flex flex-wrap gap-2">
                {tags.map((tag, idx) => (
                  <Badge key={idx} variant="secondary" className="px-3 py-1 text-sm bg-pink-50 text-pink-700 hover:bg-pink-100">
                    #{tag}
                    <button onClick={() => removeTag(tag)} className="ml-2 hover:text-red-500">
                      <X className="size-3" />
                    </button>
                  </Badge>
                ))}
              </div>
              <div className="flex items-center gap-2">
                <Hash className="size-4 text-gray-400" />
                <Input 
                  placeholder="Thêm hashtag (Nhấn Enter)..." 
                  className="border-none shadow-none focus-visible:ring-0 p-0 h-auto"
                  value={tagInput}
                  onChange={(e) => setTagInput(e.target.value)}
                  onKeyDown={handleKeyDownTag}
                />
              </div>
            </div>

            {/* Toolbar & Submit */}
            <div className="flex items-center justify-between pt-2">
              <div className="flex gap-2">
                <input
                  type="file"
                  multiple
                  accept="image/*,video/*"
                  className="hidden"
                  ref={fileInputRef}
                  onChange={handleFileSelect}
                />
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="text-gray-600 gap-2"
                  onClick={() => fileInputRef.current?.click()}
                  disabled={isUploading}
                >
                  <ImageIcon className="size-4" />
                  Thêm ảnh
                </Button>
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="text-gray-600 gap-2"
                  onClick={() => fileInputRef.current?.click()}
                  disabled={isUploading}
                >
                  <Video className="size-4" />
                  Thêm video
                </Button>
              </div>

              <Button 
                onClick={handleSubmit} 
                disabled={isSubmitting || isUploading || !title.trim() || (!content.trim() && mediaList.length === 0)}
                className="bg-gradient-to-r from-pink-500 to-purple-600 gap-2"
              >
                {isSubmitting ? <Loader2 className="size-4 animate-spin" /> : <Send className="size-4" />}
                {editMode ? 'Cập nhật' : 'Đăng bài'}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}