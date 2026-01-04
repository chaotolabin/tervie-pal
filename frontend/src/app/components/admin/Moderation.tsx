import { useState, useEffect } from 'react';
import { Utensils, Dumbbell, FileText, Check, X, Loader2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../ui/table';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { toast } from 'sonner';

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

  // Giả định API kiểm duyệt lấy từ một endpoint admin
  // Vì API bạn cung cấp là endpoint chung, tôi viết hàm fetch tổng quát
  const fetchData = async () => {
    setLoading(true);
    try {
      // Lưu ý: Trong thực tế bạn cần endpoint admin để lấy danh sách "pending"
      // Ở đây tôi minh họa fetch từ route chính
      const [foodRes, exRes] = await Promise.all([
        fetch('/api/v1/foods/search?q=&limit=50'), 
        fetch('/api/v1/exercises/search?q=&limit=50')
      ]);

      const foodData = await foodRes.json();
      const exData = await exRes.json();

      setFoods(foodData.items);
      setExercises(exData.items);
    } catch (error) {
      toast.error('Lỗi kết nối dữ liệu');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Xử lý Duyệt (Thường là đổi flag is_public hoặc status trong DB)
  const handleApprove = async (type: 'foods' | 'exercises', id: number) => {
    try {
      // Giả định endpoint patch để duyệt
      const res = await fetch(`/api/v1/${type}/${id}`, {
        method: 'PATCH',
        body: JSON.stringify({ is_public: true }) 
      });

      if (res.ok) {
        toast.success('Đã phê duyệt nội dung');
        if (type === 'foods') setFoods(foods.filter(f => f.id !== id));
        else setExercises(exercises.filter(e => e.id !== id));
      }
    } catch (e) {
      toast.error('Thao tác thất bại');
    }
  };

  if (loading) return <div className="flex justify-center p-20"><Loader2 className="animate-spin" /></div>;

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">Hệ thống Kiểm duyệt</h1>
        <p className="text-muted-foreground">Theo đúng cấu trúc API Foods & Exercises</p>
      </div>

      <Tabs defaultValue="foods">
        <TabsList className="w-[400px]">
          <TabsTrigger value="foods">Thực phẩm ({foods.length})</TabsTrigger>
          <TabsTrigger value="exercises">Bài tập ({exercises.length})</TabsTrigger>
        </TabsList>

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