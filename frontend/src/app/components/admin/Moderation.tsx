import React, { useState, useEffect } from 'react';
import { Utensils, Dumbbell, FileText, Check, X, Loader2, Trash2, Eye } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../ui/table';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { toast } from 'sonner';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../ui/dialog';

// --- Định nghĩa Interfaces theo Schema API của bạn ---

interface Nutrient {
  nutrient_name: string;
  unit: string;
  amount_per_100g: number;
}

interface FoodDetail {
  id: number;
  name: string;
  food_group: string | null;
  owner_user_id: string | null;
  nutrients: Nutrient[];
  // Theo API, "owner_user_id" null là global food, có ID là custom food
}

interface ExerciseResponse {
  id: number;
  description: string;
  major_heading: string;
  met_value: number;
  owner_user_id: string | null;
}

export default function Moderation() {
  const [foods, setFoods] = useState<FoodDetail[]>([]);
  const [exercises, setExercises] = useState<ExerciseResponse[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    setLoading(true);
    try {
      const { AdminService } = await import('../../../service/admin.service');
      
      // Fetch blog posts for moderation
      const postsData = await AdminService.getPosts({ page: 1, page_size: 50, include_deleted: false });
      
      // Map posts to exercises format for display (reusing existing UI)
      // In a real scenario, you might want separate components
      setExercises([]);
      setFoods([]);
      
      // For now, we'll focus on blog posts moderation
      // You can extend this to handle foods/exercises if needed
    } catch (error) {
      toast.error('Lỗi kết nối dữ liệu');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleApprove = async (type: 'foods' | 'exercises', id: number) => {
    toast.info('Tính năng đang phát triển');
  };

  if (loading) return <div className="flex justify-center p-20"><Loader2 className="animate-spin" /></div>;

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">Hệ thống kiểm duyệt</h1>
        <p className="text-muted-foreground">Quản lý và kiểm duyệt nội dung từ người dùng trong hệ thống</p>
      </div>

      <Tabs defaultValue="blog">
        <TabsList className="w-[400px]">
          <TabsTrigger value="blog">Bài viết</TabsTrigger>
          <TabsTrigger value="foods">Thực phẩm ({foods.length})</TabsTrigger>
          <TabsTrigger value="exercises">Bài tập ({exercises.length})</TabsTrigger>
        </TabsList>
        
        {/* Blog Posts Tab */}
        <TabsContent value="blog">
          <BlogPostsModeration />
        </TabsContent>

        {/* Cột dữ liệu cho FOODS */}
        <TabsContent value="foods">
          <Card>
            <CardContent className="pt-6">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Tên thực phẩm</TableHead>
                    <TableHead>Nhóm</TableHead>
                    <TableHead>Dinh dưỡng (100g)</TableHead>
                    <TableHead className="text-right">Thao tác</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {foods.map((food) => (
                    <TableRow key={food.id}>
                      <TableCell className="font-medium">{food.name}</TableCell>
                      <TableCell><Badge variant="outline">{food.food_group || 'N/A'}</Badge></TableCell>
                      <TableCell>
                        <div className="flex flex-wrap gap-1">
                          {food.nutrients.slice(0, 3).map((n, i) => (
                            <span key={i} className="text-xs bg-slate-100 px-1.5 py-0.5 rounded text-slate-600">
                              {n.nutrient_name}: {n.amount_per_100g}{n.unit}
                            </span>
                          ))}
                          {food.nutrients.length > 3 && <span className="text-xs text-slate-400">...</span>}
                        </div>
                      </TableCell>
                      <TableCell className="text-right space-x-2">
                        <Button size="sm" onClick={() => handleApprove('foods', food.id)}>
                          <Check className="size-4 mr-1" /> Duyệt
                        </Button>
                        <Button size="sm" variant="destructive">
                          <X className="size-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Cột dữ liệu cho EXERCISES */}
        <TabsContent value="exercises">
          <Card>
            <CardContent className="pt-6">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Mô tả bài tập</TableHead>
                    <TableHead>Nhóm bài tập</TableHead>
                    <TableHead>MET Value</TableHead>
                    <TableHead className="text-right">Thao tác</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {exercises.map((ex) => (
                    <TableRow key={ex.id}>
                      <TableCell className="font-medium">{ex.description}</TableCell>
                      <TableCell>{ex.major_heading}</TableCell>
                      <TableCell>
                        <Badge className="bg-blue-100 text-blue-700 hover:bg-blue-100 border-none">
                          {ex.met_value} MET
                        </Badge>
                      </TableCell>
                      <TableCell className="text-right space-x-2">
                        <Button size="sm" onClick={() => handleApprove('exercises', ex.id)}>
                          <Check className="size-4 mr-1" /> Duyệt
                        </Button>
                        <Button size="sm" variant="destructive">
                          <X className="size-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

// Component riêng cho Blog Posts Moderation
function BlogPostsModeration() {
  const [posts, setPosts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [selectedPost, setSelectedPost] = useState<any | null>(null);
  const [detailOpen, setDetailOpen] = useState(false);
  const [detailLoading, setDetailLoading] = useState(false);

  useEffect(() => {
    const fetchPosts = async () => {
      try {
        setLoading(true);
        const { AdminService } = await import('../../../service/admin.service');
        const data = await AdminService.getPosts({ page, page_size: 50, include_deleted: false });
        setPosts(data.items || []);
        setTotalPages(data.total_pages || 1);
      } catch (error) {
        toast.error('Không thể tải danh sách bài viết');
      } finally {
        setLoading(false);
      }
    };
    fetchPosts();
  }, [page]);

  const openPostDetail = async (post: any) => {
    setDetailOpen(true);
    setDetailLoading(true);
    try {
      // Thử lấy full content từ BlogService nếu có
      const { BlogService } = await import('../../../service/blog.service');
      const detail = await BlogService.getPost(post.id.toString());
      setSelectedPost(detail);
    } catch (error) {
      console.error('Không thể tải chi tiết bài viết:', error);
      // Fallback: dùng data từ danh sách nếu không gọi được API
      setSelectedPost(post);
      toast.error('Không thể tải chi tiết bài viết đầy đủ, hiển thị bản tóm tắt.');
    } finally {
      setDetailLoading(false);
    }
  };

  const handleDeletePost = async (postId: number) => {
    if (!confirm('Bạn có chắc chắn muốn xóa bài viết này?')) return;
    
    try {
      const { AdminService } = await import('../../../service/admin.service');
      await AdminService.deletePost(postId, 'Xóa bởi admin');
      toast.success('Đã xóa bài viết');
      setPosts(posts.filter(p => p.id !== postId));
      if (selectedPost?.id === postId) {
        setDetailOpen(false);
        setSelectedPost(null);
      }
    } catch (error) {
      toast.error('Không thể xóa bài viết');
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center p-20">
        <Loader2 className="animate-spin size-10 text-blue-600" />
      </div>
    );
  }

  return (
    <>
      <Card>
        <CardContent className="pt-6">
          <Table>
          <TableHeader>
            <TableRow>
              <TableHead>ID</TableHead>
              <TableHead>Tác giả</TableHead>
              <TableHead>Tiêu đề/Nội dung</TableHead>
              <TableHead>Likes</TableHead>
              <TableHead>Saves</TableHead>
              <TableHead>Ngày tạo</TableHead>
              <TableHead className="text-right">Thao tác</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {posts.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} className="text-center text-gray-400 py-8">
                  Chưa có bài viết nào
                </TableCell>
              </TableRow>
            ) : (
              posts.map((post) => (
                <TableRow
                  key={post.id}
                  className="hover:bg-gray-50 cursor-pointer"
                  onClick={() => openPostDetail(post)}
                >
                  <TableCell className="text-gray-400">#{post.id}</TableCell>
                  <TableCell>
                    <div className="text-sm">
                      <div className="font-medium">{post.username}</div>
                      <div className="text-gray-400 text-xs">
                        {post.user_id?.toString().substring(0, 8)}
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="max-w-md">
                      {post.title && (
                        <div className="font-semibold text-gray-900 mb-1">
                          {post.title}
                        </div>
                      )}
                      <div className="text-sm text-gray-600 truncate">
                        {post.content_preview}
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline" className="bg-red-50 text-red-700">
                      ❤️ {post.like_count}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline" className="bg-blue-50 text-blue-700">
                      🔖 {post.save_count}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-sm text-gray-600">
                    {new Date(post.created_at).toLocaleDateString('vi-VN')}
                  </TableCell>
                  <TableCell
                    className="text-right"
                    onClick={(e) => e.stopPropagation()} // tránh mở modal khi bấm nút
                  >
                    <div className="flex justify-end gap-2">
                      <Button
                        size="sm"
                        variant="destructive"
                        onClick={() => handleDeletePost(post.id)}
                      >
                        <Trash2 className="size-4 mr-1" />
                        Xóa
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between mt-6 pt-4 border-t">
            <div className="text-sm text-gray-600">
              Trang {page} / {totalPages}
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Trước
              </button>
              <button
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Sau
              </button>
            </div>
          </div>
        )}
      </CardContent>
      </Card>

      {/* Article Detail Modal */}
      <Dialog
        open={detailOpen}
        onOpenChange={(open) => {
          setDetailOpen(open);
          if (!open) setSelectedPost(null);
        }}
      >
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader className="flex flex-row items-start justify-between gap-4">
            <div>
              <DialogTitle className="text-2xl font-bold">
                {selectedPost?.title ||
                  (selectedPost ? `Bài viết #${selectedPost.id}` : 'Chi tiết bài viết')}
              </DialogTitle>
              {selectedPost && (
                <p className="mt-1 text-sm text-gray-500">
                  Tác giả:{' '}
                  <span className="font-medium text-gray-800">
                    {selectedPost.full_name || selectedPost.username || 'Không rõ tác giả'}
                  </span>
                  {selectedPost.created_at && (
                    <>
                      {' • '}
                      <span>
                        {new Date(selectedPost.created_at).toLocaleString('vi-VN')}
                      </span>
                    </>
                  )}
                </p>
              )}
            </div>

        </DialogHeader>

          {detailLoading && (
            <div className="flex items-center justify-center py-8 text-gray-500 gap-2">
              <Loader2 className="size-5 animate-spin" />
              Đang tải nội dung bài viết...
            </div>
          )}

          {!detailLoading && selectedPost && (
            <div className="space-y-4 mt-2">
              {/* Ảnh (nếu có) */}
              {Array.isArray(selectedPost.media) && selectedPost.media.length > 0 && (
                <div className="rounded-xl overflow-hidden bg-gray-100">
                  <img
                    src={selectedPost.media[0].url}
                    alt={selectedPost.title || 'Article image'}
                    className="w-full max-h-80 object-cover"
                  />
                </div>
              )}

              {/* Nội dung chính */}
              <div className="prose max-w-none text-gray-800">
                {selectedPost.content_html ? (
                  <div
                    className="prose max-w-none"
                    dangerouslySetInnerHTML={{ __html: selectedPost.content_html }}
                  />
                ) : selectedPost.content_text ? (
                  <p className="whitespace-pre-wrap">{selectedPost.content_text}</p>
                ) : (
                  <p className="whitespace-pre-wrap">
                    {selectedPost.content_preview || 'Không có nội dung để hiển thị'}
                  </p>
                )}
              </div>

            {/* Actions */}
            <div className="flex justify-end gap-2 pt-4 border-t mt-4">
              <Button
                variant="destructive"
                onClick={() => {
                  if (!selectedPost) return;
                  handleDeletePost(selectedPost.id);
                }}
              >
                <Trash2 className="size-4 mr-1" />
                Xóa bài viết
              </Button>
            </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </>
  );
}