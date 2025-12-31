import { useState } from 'react';
import { Utensils, Dumbbell, FileText, Check, X } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../ui/table';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { toast } from 'sonner';

const pendingFoods = [
  { id: 1, name: 'Phở bò đặc biệt', submittedBy: 'Nguyễn Văn A', calories: 450, protein: 25, carbs: 60, fat: 12, status: 'pending' },
  { id: 2, name: 'Bánh mì pate', submittedBy: 'Trần Thị B', calories: 350, protein: 15, carbs: 45, fat: 18, status: 'pending' },
  { id: 3, name: 'Cơm gà xối mỡ', submittedBy: 'Lê Văn C', calories: 520, protein: 30, carbs: 55, fat: 20, status: 'pending' },
];

const pendingExercises = [
  { id: 1, name: 'Jump Rope', submittedBy: 'Phạm Thị D', caloriesPerMin: 12, category: 'Cardio', status: 'pending' },
  { id: 2, name: 'Plank', submittedBy: 'Hoàng Văn E', caloriesPerMin: 4, category: 'Core', status: 'pending' },
];

const reportedContent = [
  { id: 1, type: 'food', content: 'Pizza 10000 calories', reportedBy: 'User123', reason: 'Thông tin sai', status: 'pending' },
  { id: 2, type: 'exercise', content: 'Run 5000 kcal/min', reportedBy: 'User456', reason: 'Spam', status: 'pending' },
];

export default function Moderation() {
  const [foods, setFoods] = useState(pendingFoods);
  const [exercises, setExercises] = useState(pendingExercises);
  const [reports, setReports] = useState(reportedContent);

  const handleApproveFood = (id: number) => {
    setFoods(foods.filter(f => f.id !== id));
    toast.success('Đã phê duyệt thực phẩm');
  };

  const handleRejectFood = (id: number) => {
    setFoods(foods.filter(f => f.id !== id));
    toast.warning('Đã từ chối thực phẩm');
  };

  const handleApproveExercise = (id: number) => {
    setExercises(exercises.filter(e => e.id !== id));
    toast.success('Đã phê duyệt bài tập');
  };

  const handleRejectExercise = (id: number) => {
    setExercises(exercises.filter(e => e.id !== id));
    toast.warning('Đã từ chối bài tập');
  };

  const handleResolveReport = (id: number) => {
    setReports(reports.filter(r => r.id !== id));
    toast.success('Đã xử lý báo cáo');
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Kiểm duyệt nội dung</h1>
        <p className="text-gray-600 mt-1">Phê duyệt và quản lý nội dung do người dùng tạo</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between mb-2">
              <div>
                <p className="text-sm text-gray-600">Thực phẩm chờ duyệt</p>
                <p className="text-3xl font-bold">{foods.length}</p>
              </div>
              <Utensils className="size-10 text-green-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between mb-2">
              <div>
                <p className="text-sm text-gray-600">Bài tập chờ duyệt</p>
                <p className="text-3xl font-bold">{exercises.length}</p>
              </div>
              <Dumbbell className="size-10 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between mb-2">
              <div>
                <p className="text-sm text-gray-600">Báo cáo nội dung</p>
                <p className="text-3xl font-bold">{reports.length}</p>
              </div>
              <FileText className="size-10 text-orange-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Content Tabs */}
      <Tabs defaultValue="foods" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="foods">
            Thực phẩm ({foods.length})
          </TabsTrigger>
          <TabsTrigger value="exercises">
            Bài tập ({exercises.length})
          </TabsTrigger>
          <TabsTrigger value="reports">
            Báo cáo ({reports.length})
          </TabsTrigger>
        </TabsList>

        {/* Foods Tab */}
        <TabsContent value="foods" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Thực phẩm chờ phê duyệt</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Tên thực phẩm</TableHead>
                    <TableHead>Người tạo</TableHead>
                    <TableHead>Calories</TableHead>
                    <TableHead>Protein</TableHead>
                    <TableHead>Carbs</TableHead>
                    <TableHead>Fat</TableHead>
                    <TableHead>Trạng thái</TableHead>
                    <TableHead></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {foods.map((food) => (
                    <TableRow key={food.id}>
                      <TableCell className="font-medium">{food.name}</TableCell>
                      <TableCell>{food.submittedBy}</TableCell>
                      <TableCell>{food.calories} kcal</TableCell>
                      <TableCell>{food.protein}g</TableCell>
                      <TableCell>{food.carbs}g</TableCell>
                      <TableCell>{food.fat}g</TableCell>
                      <TableCell>
                        <Badge variant="secondary">Chờ duyệt</Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-2">
                          <Button size="sm" variant="default" onClick={() => handleApproveFood(food.id)}>
                            <Check className="size-4 mr-1" />
                            Duyệt
                          </Button>
                          <Button size="sm" variant="destructive" onClick={() => handleRejectFood(food.id)}>
                            <X className="size-4 mr-1" />
                            Từ chối
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              {foods.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  Không có thực phẩm nào chờ phê duyệt
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Exercises Tab */}
        <TabsContent value="exercises" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Bài tập chờ phê duyệt</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Tên bài tập</TableHead>
                    <TableHead>Người tạo</TableHead>
                    <TableHead>Calories/phút</TableHead>
                    <TableHead>Danh mục</TableHead>
                    <TableHead>Trạng thái</TableHead>
                    <TableHead></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {exercises.map((exercise) => (
                    <TableRow key={exercise.id}>
                      <TableCell className="font-medium">{exercise.name}</TableCell>
                      <TableCell>{exercise.submittedBy}</TableCell>
                      <TableCell>{exercise.caloriesPerMin} kcal</TableCell>
                      <TableCell>
                        <Badge variant="outline">{exercise.category}</Badge>
                      </TableCell>
                      <TableCell>
                        <Badge variant="secondary">Chờ duyệt</Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-2">
                          <Button size="sm" variant="default" onClick={() => handleApproveExercise(exercise.id)}>
                            <Check className="size-4 mr-1" />
                            Duyệt
                          </Button>
                          <Button size="sm" variant="destructive" onClick={() => handleRejectExercise(exercise.id)}>
                            <X className="size-4 mr-1" />
                            Từ chối
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              {exercises.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  Không có bài tập nào chờ phê duyệt
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Reports Tab */}
        <TabsContent value="reports" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Báo cáo nội dung</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Loại</TableHead>
                    <TableHead>Nội dung</TableHead>
                    <TableHead>Người báo cáo</TableHead>
                    <TableHead>Lý do</TableHead>
                    <TableHead>Trạng thái</TableHead>
                    <TableHead></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {reports.map((report) => (
                    <TableRow key={report.id}>
                      <TableCell>
                        <Badge variant="outline">{report.type === 'food' ? 'Thực phẩm' : 'Bài tập'}</Badge>
                      </TableCell>
                      <TableCell className="font-medium">{report.content}</TableCell>
                      <TableCell>{report.reportedBy}</TableCell>
                      <TableCell>{report.reason}</TableCell>
                      <TableCell>
                        <Badge variant="secondary">Chờ xử lý</Badge>
                      </TableCell>
                      <TableCell>
                        <Button size="sm" onClick={() => handleResolveReport(report.id)}>
                          Xử lý
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              {reports.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  Không có báo cáo nào chờ xử lý
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
