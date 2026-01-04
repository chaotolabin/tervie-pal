import React, { useEffect, useState } from 'react';
import { BlogService } from '../../../service/blog.service';
import { Loader2 } from 'lucide-react';
import { toast } from 'sonner';

export default function BlogPage() {
  const [feed, setFeed] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchFeed = async () => {
      try {
        setLoading(true);
        setError(null);
        const res = await BlogService.getFeed({ limit: 10 });
        setFeed(res.items || []); // Khớp với FeedResponse schema
      } catch (err: any) {
        console.error('Lỗi tải feed:', err);
        setError('Không thể tải bài viết. Vui lòng thử lại sau.');
        toast.error('Không thể tải bài viết');
      } finally {
        setLoading(false);
      }
    };
    fetchFeed();
  }, []);

  if (loading) {
    return (
      <div className="max-w-xl mx-auto py-8">
        <h1 className="text-2xl font-bold mb-6">Tervie blog</h1>
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-pink-600" />
          <span className="ml-3 text-gray-600">Đang tải bài viết...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-xl mx-auto py-8">
        <h1 className="text-2xl font-bold mb-6">Tervie blog</h1>
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-center">
          <p className="text-red-600">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="mt-4 px-4 py-2 bg-pink-600 text-white rounded-lg hover:bg-pink-700 transition-colors"
          >
            Thử lại
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-xl mx-auto py-8">
      <h1 className="text-2xl font-bold mb-6">Tervie blog</h1>
      {feed.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg mb-4">Chưa có bài viết nào</p>
          <p className="text-gray-400 text-sm">Hãy là người đầu tiên chia sẻ với cộng đồng!</p>
        </div>
      ) : (
        <div className="space-y-6">
          {feed.map((post) => (
            <div key={post.id} className="bg-white p-4 rounded-lg shadow hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-r from-pink-500 to-purple-600 flex items-center justify-center text-white font-bold text-sm">
                    {post.user_id ? post.user_id.toString().charAt(0).toUpperCase() : '?'}
                  </div>
                  <span className="font-semibold text-gray-800">
                    {post.author?.username || `User ${post.user_id?.toString().substring(0, 8) || 'Unknown'}`}
                  </span>
                </div>
                {post.created_at && (
                  <span className="text-xs text-gray-400">
                    {new Date(post.created_at).toLocaleDateString('vi-VN')}
                  </span>
                )}
              </div>
              {post.title && (
                <h3 className="font-semibold text-lg mb-2 text-gray-900">{post.title}</h3>
              )}
              <p className="text-gray-800 mb-3 whitespace-pre-wrap">
                {post.content_text || post.content || ''}
              </p>
              {post.media && post.media.length > 0 && (
                <div className="mb-3 grid gap-2" style={{ gridTemplateColumns: post.media.length > 1 ? 'repeat(2, 1fr)' : '1fr' }}>
                  {post.media.slice(0, 4).map((media: any, idx: number) => (
                    <div key={idx} className="rounded-lg overflow-hidden bg-gray-100">
                      {media.media_type === 'image' ? (
                        <img 
                          src={media.url} 
                          alt={`Post media ${idx + 1}`} 
                          className="w-full h-48 object-cover"
                        />
                      ) : (
                        <video 
                          src={media.url} 
                          controls 
                          className="w-full h-48 object-cover"
                        />
                      )}
                    </div>
                  ))}
                </div>
              )}
              {post.hashtags && post.hashtags.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-3">
                  {post.hashtags.map((tag: string, idx: number) => (
                    <span key={idx} className="text-xs bg-blue-50 text-blue-600 px-2 py-1 rounded">
                      #{tag}
                    </span>
                  ))}
                </div>
              )}
              <div className="flex items-center gap-4 text-sm text-gray-500 pt-2 border-t">
                <span className="flex items-center gap-1">
                  <span>❤️</span>
                  <span>{post.like_count || post.likes_count || 0}</span>
                </span>
                <span className="flex items-center gap-1">
                  <span>🔖</span>
                  <span>{post.save_count || 0}</span>
                </span>
                <span className="flex items-center gap-1">
                  <span>💬</span>
                  <span>{post.comments_count || 0}</span>
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}