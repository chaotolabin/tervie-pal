import React, { useState, useEffect } from 'react';
import { Utensils, Dumbbell, FileText, Check, X, Loader2, Trash2, Eye } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../ui/table';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { toast } from 'sonner';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../ui/dialog';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '../ui/alert-dialog';

// --- Định nghĩa Interfaces theo Schema API của bạn ---

interface Nutrient {
  nutrient_name: string;
  unit: string;
  amount_per_100g: number;
}

interface Portion {
  id: number;
  amount: number;
  unit: string;
  grams: number;
}

interface FoodDetail {
  id: number;
  name: string;
  food_group: string | null;
  owner_user_id: string | null;
  creator_username?: string | null;
  creator_email?: string | null;
  nutrients: Nutrient[];
  portions?: Portion[];
  is_contribution?: boolean;
  contribution_status?: 'pending' | 'approved' | 'rejected';
  created_at?: string;
  // Theo API, "owner_user_id" null là global food, có ID là custom food
}

interface ExerciseResponse {
  id: number;
  description: string;
  major_heading: string;
  met_value: number;
  owner_user_id: string | null;
  creator_username?: string | null;
  creator_email?: string | null;
  is_contribution?: boolean;
  contribution_status?: 'pending' | 'approved' | 'rejected';
  created_at?: string;
}

export default function Moderation() {
  const [foods, setFoods] = useState<FoodDetail[]>([]);
  const [exercises, setExercises] = useState<ExerciseResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<{ type: 'foods' | 'exercises'; id: number; name: string; creatorId: string | null } | null>(null);
  const [deleting, setDeleting] = useState(false);
  
  // States for detail modals
  const [selectedFood, setSelectedFood] = useState<FoodDetail | null>(null);
  const [foodDetailOpen, setFoodDetailOpen] = useState(false);
  const [selectedExercise, setSelectedExercise] = useState<ExerciseResponse | null>(null);
  const [exerciseDetailOpen, setExerciseDetailOpen] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    try {
      const { AdminService } = await import('../../../service/admin.service');
      
      console.log('[DEBUG] Starting to fetch pending contributions...');
      
      // Fetch pending contributions for foods and exercises
      const [foodsData, exercisesData] = await Promise.all([
        AdminService.getPendingContributions('foods').catch((err) => {
          console.error('[ERROR] Error fetching foods:', err);
          console.error('[ERROR] Error details:', err.response?.data || err.message);
          return [];
        }),
        AdminService.getPendingContributions('exercises').catch((err) => {
          console.error('[ERROR] Error fetching exercises:', err);
          console.error('[ERROR] Error details:', err.response?.data || err.message);
          return [];
        })
      ]);

      console.log('[DEBUG] Raw foods response:', foodsData);
      console.log('[DEBUG] Raw exercises response:', exercisesData);
      console.log('[DEBUG] Foods data type:', typeof foodsData, Array.isArray(foodsData));

      // Backend trả về array trực tiếp, không có wrapper
      const pendingFoods = Array.isArray(foodsData) ? foodsData : (foodsData?.items || []);
      const pendingExercises = Array.isArray(exercisesData) ? exercisesData : (exercisesData?.items || []);

      console.log('[DEBUG] Processed pending foods count:', pendingFoods.length);
      console.log('[DEBUG] Processed pending exercises count:', pendingExercises.length);
      console.log('[DEBUG] First food item:', pendingFoods[0]);

      setFoods(pendingFoods);
      setExercises(pendingExercises);
      
      if (pendingFoods.length === 0 && pendingExercises.length === 0) {
        console.warn('[WARN] No pending contributions found. Check database for is_contribution=true and contribution_status=pending');
      }
    } catch (error) {
      console.error('[ERROR] Unexpected error fetching contributions:', error);
      toast.error('Lỗi kết nối dữ liệu');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleApprove = async (type: 'foods' | 'exercises', id: number) => {
    try {
      const { AdminService } = await import('../../../service/admin.service');
      await AdminService.approveContribution(type, id);
      toast.success('Đã duyệt thành công');
      fetchData(); // Refresh list
    } catch (error) {
      console.error('Error approving contribution:', error);
      toast.error('Không thể duyệt đóng góp');
    }
  };

  const handleDeleteClick = (type: 'foods' | 'exercises', item: FoodDetail | ExerciseResponse) => {
    // Only show delete dialog for pending contributions
    if (item.is_contribution === true && item.contribution_status === 'pending') {
      const name = type === 'foods' ? (item as FoodDetail).name : (item as ExerciseResponse).description;
      setDeleteTarget({
        type,
        id: item.id,
        name,
        creatorId: item.owner_user_id
      });
      setDeleteDialogOpen(true);
    } else {
      toast.warning('Chỉ có thể xóa các đóng góp đang chờ duyệt');
    }
  };

  const handleDeleteConfirm = async () => {
    if (!deleteTarget) return;

    setDeleting(true);
    try {
      const { AdminService } = await import('../../../service/admin.service');

      // Delete the contribution (backend sẽ tự động tạo notification)
      await AdminService.deleteContribution(deleteTarget.type, deleteTarget.id);

      toast.success('Đã từ chối đóng góp và gửi thông báo cho người dùng');
      setDeleteDialogOpen(false);
      setDeleteTarget(null);
      fetchData(); // Refresh list
    } catch (error) {
      console.error('Error deleting contribution:', error);
      toast.error('Không thể từ chối đóng góp');
    } finally {
      setDeleting(false);
    }
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
                    <TableHead>ID</TableHead>
                    <TableHead>Tên thực phẩm</TableHead>
                    <TableHead>Người đóng góp</TableHead>
                    <TableHead>Nhóm</TableHead>
                    <TableHead>Dinh dưỡng (100g)</TableHead>
                    <TableHead>Ngày tạo</TableHead>
                    <TableHead className="text-right">Thao tác</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {foods.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={7} className="text-center text-gray-400 py-8">
                        Chưa có đóng góp thực phẩm nào đang chờ duyệt
                      </TableCell>
                    </TableRow>
                  ) : (
                    foods.map((food) => (
                      <TableRow
                        key={food.id}
                        className="hover:bg-gray-50 cursor-pointer"
                        onClick={() => {
                          setSelectedFood(food);
                          setFoodDetailOpen(true);
                        }}
                      >
                        <TableCell className="text-gray-400">#{food.id}</TableCell>
                        <TableCell className="font-medium">{food.name}</TableCell>
                        <TableCell>
                          <div className="text-sm">
                            <div className="font-medium">{food.creator_username || 'N/A'}</div>
                            {food.creator_email && (
                              <div className="text-xs text-gray-400">{food.creator_email}</div>
                            )}
                          </div>
                        </TableCell>
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
                        <TableCell className="text-sm text-gray-600">
                          {food.created_at ? new Date(food.created_at).toLocaleDateString('vi-VN') : 'N/A'}
                        </TableCell>
                        <TableCell
                          className="text-right space-x-2"
                          onClick={(e) => e.stopPropagation()} // tránh mở modal khi bấm nút
                        >
                          <Button 
                            size="sm" 
                            onClick={() => handleApprove('foods', food.id)}
                            className="bg-green-600 hover:bg-green-700 text-white"
                          >
                            <Check className="size-4 mr-1" /> Duyệt
                          </Button>
                          <Button 
                            size="sm" 
                            variant="destructive"
                            onClick={() => handleDeleteClick('foods', food)}
                            disabled={!food.is_contribution || food.contribution_status !== 'pending'}
                          >
                            <Trash2 className="size-4" />
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
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
                    <TableHead>ID</TableHead>
                    <TableHead>Mô tả bài tập</TableHead>
                    <TableHead>Người đóng góp</TableHead>
                    <TableHead>Nhóm bài tập</TableHead>
                    <TableHead>MET Value</TableHead>
                    <TableHead>Ngày tạo</TableHead>
                    <TableHead className="text-right">Thao tác</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {exercises.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={7} className="text-center text-gray-400 py-8">
                        Chưa có đóng góp bài tập nào đang chờ duyệt
                      </TableCell>
                    </TableRow>
                  ) : (
                    exercises.map((ex) => (
                      <TableRow
                        key={ex.id}
                        className="hover:bg-gray-50 cursor-pointer"
                        onClick={() => {
                          setSelectedExercise(ex);
                          setExerciseDetailOpen(true);
                        }}
                      >
                        <TableCell className="text-gray-400">#{ex.id}</TableCell>
                        <TableCell className="font-medium">{ex.description}</TableCell>
                        <TableCell>
                          <div className="text-sm">
                            <div className="font-medium">{ex.creator_username || 'N/A'}</div>
                            {ex.creator_email && (
                              <div className="text-xs text-gray-400">{ex.creator_email}</div>
                            )}
                          </div>
                        </TableCell>
                        <TableCell>{ex.major_heading || 'N/A'}</TableCell>
                        <TableCell>
                          <Badge className="bg-blue-100 text-blue-700 hover:bg-blue-100 border-none">
                            {ex.met_value} MET
                          </Badge>
                        </TableCell>
                        <TableCell className="text-sm text-gray-600">
                          {ex.created_at ? new Date(ex.created_at).toLocaleDateString('vi-VN') : 'N/A'}
                        </TableCell>
                        <TableCell
                          className="text-right space-x-2"
                          onClick={(e) => e.stopPropagation()} // tránh mở modal khi bấm nút
                        >
                          <Button 
                            size="sm" 
                            onClick={() => handleApprove('exercises', ex.id)}
                            className="bg-green-600 hover:bg-green-700 text-white"
                          >
                            <Check className="size-4 mr-1" /> Duyệt
                          </Button>
                          <Button 
                            size="sm" 
                            variant="destructive"
                            onClick={() => handleDeleteClick('exercises', ex)}
                            disabled={!ex.is_contribution || ex.contribution_status !== 'pending'}
                          >
                            <Trash2 className="size-4" />
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Xác nhận từ chối đóng góp</AlertDialogTitle>
            <AlertDialogDescription>
              Bạn có chắc chắn muốn từ chối đóng góp "{deleteTarget?.name}"? 
              Hành động này sẽ xóa đóng góp khỏi hệ thống và gửi thông báo cho người đóng góp.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={deleting}>Hủy</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteConfirm}
              disabled={deleting}
              className="bg-red-600 hover:bg-red-700"
            >
              {deleting ? (
                <>
                  <Loader2 className="size-4 mr-2 animate-spin" />
                  Đang xử lý...
                </>
              ) : (
                'Xác nhận xóa'
              )}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Food Detail Dialog */}
      <Dialog
        open={foodDetailOpen}
        onOpenChange={(open) => {
          setFoodDetailOpen(open);
          if (!open) setSelectedFood(null);
        }}
      >
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="text-2xl font-bold">
              {selectedFood?.name || 'Chi tiết thực phẩm'}
            </DialogTitle>
            {selectedFood && (
              <p className="mt-1 text-sm text-gray-500">
                Người đóng góp:{' '}
                <span className="font-medium text-gray-800">
                  {selectedFood.creator_username || 'N/A'}
                </span>
                {selectedFood.creator_email && (
                  <>
                    {' • '}
                    <span className="text-gray-600">{selectedFood.creator_email}</span>
                  </>
                )}
                {selectedFood.created_at && (
                  <>
                    {' • '}
                    <span>{new Date(selectedFood.created_at).toLocaleString('vi-VN')}</span>
                  </>
                )}
              </p>
            )}
          </DialogHeader>

          {selectedFood && (
            <div className="space-y-4 mt-2">
              {/* Basic Info */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-gray-500">ID</label>
                  <p className="text-gray-900">#{selectedFood.id}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Nhóm thực phẩm</label>
                  <p className="text-gray-900">
                    <Badge variant="outline">{selectedFood.food_group || 'N/A'}</Badge>
                  </p>
                </div>
              </div>

              {/* Nutrients */}
              <div>
                <label className="text-sm font-medium text-gray-500 mb-2 block">
                  Thông tin dinh dưỡng (trên 100g)
                </label>
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="grid grid-cols-2 gap-3">
                    {selectedFood.nutrients.map((nutrient, idx) => (
                      <div key={idx} className="flex justify-between items-center">
                        <span className="text-sm font-medium text-gray-700 capitalize">
                          {nutrient.nutrient_name}:
                        </span>
                        <span className="text-sm text-gray-900">
                          {nutrient.amount_per_100g} {nutrient.unit}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Portions (if available) */}
              {'portions' in selectedFood && selectedFood.portions && selectedFood.portions.length > 0 && (
                <div>
                  <label className="text-sm font-medium text-gray-500 mb-2 block">
                    Khẩu phần
                  </label>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <div className="space-y-2">
                      {selectedFood.portions.map((portion: Portion, idx: number) => (
                        <div key={idx} className="flex justify-between items-center text-sm">
                          <span className="text-gray-700">
                            {portion.amount} {portion.unit}
                          </span>
                          <span className="text-gray-600">
                            = {portion.grams} g
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Actions */}
              <div className="flex justify-end gap-2 pt-4 border-t mt-4">
                <Button
                  variant="outline"
                  onClick={() => {
                    if (selectedFood) {
                      handleDeleteClick('foods', selectedFood);
                    }
                  }}
                  disabled={!selectedFood.is_contribution || selectedFood.contribution_status !== 'pending'}
                >
                  <Trash2 className="size-4 mr-1" />
                  Từ chối
                </Button>
                <Button
                  onClick={() => {
                    if (selectedFood) {
                      handleApprove('foods', selectedFood.id);
                      setFoodDetailOpen(false);
                      setSelectedFood(null);
                    }
                  }}
                  className="bg-green-600 hover:bg-green-700 text-white"
                >
                  <Check className="size-4 mr-1" />
                  Duyệt đóng góp
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Exercise Detail Dialog */}
      <Dialog
        open={exerciseDetailOpen}
        onOpenChange={(open) => {
          setExerciseDetailOpen(open);
          if (!open) setSelectedExercise(null);
        }}
      >
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="text-2xl font-bold">
              {selectedExercise?.description || 'Chi tiết bài tập'}
            </DialogTitle>
            {selectedExercise && (
              <p className="mt-1 text-sm text-gray-500">
                Người đóng góp:{' '}
                <span className="font-medium text-gray-800">
                  {selectedExercise.creator_username || 'N/A'}
                </span>
                {selectedExercise.creator_email && (
                  <>
                    {' • '}
                    <span className="text-gray-600">{selectedExercise.creator_email}</span>
                  </>
                )}
                {selectedExercise.created_at && (
                  <>
                    {' • '}
                    <span>{new Date(selectedExercise.created_at).toLocaleString('vi-VN')}</span>
                  </>
                )}
              </p>
            )}
          </DialogHeader>

          {selectedExercise && (
            <div className="space-y-4 mt-2">
              {/* Basic Info */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-gray-500">ID</label>
                  <p className="text-gray-900">#{selectedExercise.id}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Nhóm bài tập</label>
                  <p className="text-gray-900">{selectedExercise.major_heading || 'N/A'}</p>
                </div>
              </div>

              {/* MET Value */}
              <div>
                <label className="text-sm font-medium text-gray-500 mb-2 block">
                  Giá trị MET (Metabolic Equivalent)
                </label>
                <div className="bg-blue-50 rounded-lg p-4">
                  <div className="flex items-center gap-2">
                    <Badge className="bg-blue-100 text-blue-700 hover:bg-blue-100 border-none text-lg px-3 py-1">
                      {selectedExercise.met_value} MET
                    </Badge>
                    <span className="text-sm text-gray-600">
                      (Cường độ hoạt động thể chất)
                    </span>
                  </div>
                </div>
              </div>

              {/* Description */}
              <div>
                <label className="text-sm font-medium text-gray-500 mb-2 block">
                  Mô tả chi tiết
                </label>
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-gray-900">{selectedExercise.description}</p>
                </div>
              </div>

              {/* Actions */}
              <div className="flex justify-end gap-2 pt-4 border-t mt-4">
                <Button
                  variant="outline"
                  onClick={() => {
                    if (selectedExercise) {
                      handleDeleteClick('exercises', selectedExercise);
                    }
                  }}
                  disabled={!selectedExercise.is_contribution || selectedExercise.contribution_status !== 'pending'}
                >
                  <Trash2 className="size-4 mr-1" />
                  Từ chối
                </Button>
                <Button
                  onClick={() => {
                    if (selectedExercise) {
                      handleApprove('exercises', selectedExercise.id);
                      setExerciseDetailOpen(false);
                      setSelectedExercise(null);
                    }
                  }}
                  className="bg-green-600 hover:bg-green-700 text-white"
                >
                  <Check className="size-4 mr-1" />
                  Duyệt đóng góp
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
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