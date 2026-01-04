import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Apple, Dumbbell, Activity } from 'lucide-react';
import FoodQuickAdd from './quick-add/FoodQuickAdd';
import ExerciseQuickAdd from './quick-add/ExerciseQuickAdd';
import BiometricsQuickAdd from './quick-add/BiometricsQuickAdd';

interface QuickAddModalProps {
  open: boolean;
  onClose: () => void;
}

export default function QuickAddModal({ open, onClose }: QuickAddModalProps) {
  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Thêm nhanh</DialogTitle>
        </DialogHeader>

        <Tabs defaultValue="food" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="food" className="flex items-center gap-2">
              <Apple className="size-4" />
              Thực phẩm
            </TabsTrigger>
            <TabsTrigger value="exercise" className="flex items-center gap-2">
              <Dumbbell className="size-4" />
              Tập luyện
            </TabsTrigger>
            <TabsTrigger value="biometrics" className="flex items-center gap-2">
              <Activity className="size-4" />
              Chỉ số
            </TabsTrigger>
          </TabsList>

          <TabsContent value="food" className="mt-4">
            <FoodQuickAdd onClose={onClose} />
          </TabsContent>

          <TabsContent value="exercise" className="mt-4">
            <ExerciseQuickAdd onClose={onClose} />
          </TabsContent>

          <TabsContent value="biometrics" className="mt-4">
            <BiometricsQuickAdd onClose={onClose} />
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}
