import { useState } from 'react';
import { HelpCircle, MessageSquare, Bug, Plus, Edit, Trash2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../ui/table';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../ui/dialog';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Textarea } from '../ui/textarea';
import { toast } from 'sonner';

const faqs = [
  { id: 1, question: 'Làm sao để tính calories chính xác?', answer: 'Để tính calories chính xác...', category: 'Thực phẩm' },
  { id: 2, question: 'Mục tiêu calories được tính như thế nào?', answer: 'Mục tiêu calories được tính...', category: 'Cài đặt' },
  { id: 3, question: 'Làm sao để theo dõi tiến độ hiệu quả?', answer: 'Hãy ghi nhận hàng ngày...', category: 'Tiến độ' },
];

const tickets = [
  { id: 1, subject: 'Không thể thêm thực phẩm tự tạo', user: 'Nguyễn Văn A', status: 'open', createdAt: '2 ngày trước', priority: 'high' },
  { id: 2, subject: 'Câu hỏi về tính năng xuất dữ liệu', user: 'Trần Thị B', status: 'handled', createdAt: '1 tuần trước', priority: 'medium' },
  { id: 3, subject: 'App bị crash khi thêm ảnh', user: 'Lê Văn C', status: 'open', createdAt: '3 giờ trước', priority: 'high' },
];

const feedback = [
  { id: 1, type: 'suggestion', content: 'Nên có chế độ dark mode', user: 'User123', createdAt: '1 ngày trước' },
  { id: 2, type: 'bug', content: 'Biểu đồ không hiển thị đúng trên mobile', user: 'User456', createdAt: '2 ngày trước' },
  { id: 3, type: 'suggestion', content: 'Thêm tính năng chia sẻ tiến độ lên social', user: 'User789', createdAt: '3 ngày trước' },
];

export default function SupportManagement() {
  const [showFaqDialog, setShowFaqDialog] = useState(false);
  const [editingFaq, setEditingFaq] = useState<any>(null);
  const [faqForm, setFaqForm] = useState({ question: '', answer: '', category: '' });

  const handleCreateFaq = () => {
    if (!faqForm.question || !faqForm.answer) {
      toast.error('Vui lòng điền đầy đủ thông tin');
      return;
    }
    toast.success('Đã tạo FAQ mới');
    setShowFaqDialog(false);
    setFaqForm({ question: '', answer: '', category: '' });
  };

  const handleEditFaq = (faq: any) => {
    setEditingFaq(faq);
    setFaqForm({ question: faq.question, answer: faq.answer, category: faq.category });
    setShowFaqDialog(true);
  };

  const handleDeleteFaq = (id: number) => {
    toast.success('Đã xóa FAQ');
  };

  const handleUpdateTicketStatus = (id: number, status: string) => {
    toast.success(`Đã cập nhật trạng thái ticket #${id}`);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Quản lý hỗ trợ</h1>
        <p className="text-gray-600 mt-1">FAQ, Support Tickets, và Feedback</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between mb-2">
              <div>
                <p className="text-sm text-gray-600">Tổng FAQ</p>
                <p className="text-3xl font-bold">{faqs.length}</p>
              </div>
              <HelpCircle className="size-10 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between mb-2">
              <div>
                <p className="text-sm text-gray-600">Tickets mở</p>
                <p className="text-3xl font-bold">{tickets.filter(t => t.status === 'open').length}</p>
              </div>
              <MessageSquare className="size-10 text-orange-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between mb-2">
              <div>
                <p className="text-sm text-gray-600">Feedback mới</p>
                <p className="text-3xl font-bold">{feedback.length}</p>
              </div>
              <Bug className="size-10 text-purple-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Content Tabs */}
      <Tabs defaultValue="faq" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="faq">FAQ ({faqs.length})</TabsTrigger>
          <TabsTrigger value="tickets">Tickets ({tickets.length})</TabsTrigger>
          <TabsTrigger value="feedback">Feedback ({feedback.length})</TabsTrigger>
        </TabsList>

        {/* FAQ Tab */}
        <TabsContent value="faq" className="mt-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>Quản lý FAQ</CardTitle>
              <Button onClick={() => setShowFaqDialog(true)}>
                <Plus className="size-4 mr-2" />
                Tạo FAQ mới
              </Button>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Câu hỏi</TableHead>
                    <TableHead>Danh mục</TableHead>
                    <TableHead>Câu trả lời</TableHead>
                    <TableHead></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {faqs.map((faq) => (
                    <TableRow key={faq.id}>
                      <TableCell className="font-medium max-w-xs">{faq.question}</TableCell>
                      <TableCell>
                        <Badge variant="outline">{faq.category}</Badge>
                      </TableCell>
                      <TableCell className="max-w-md truncate text-sm text-gray-600">
                        {faq.answer}
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-2">
                          <Button size="sm" variant="outline" onClick={() => handleEditFaq(faq)}>
                            <Edit className="size-4" />
                          </Button>
                          <Button size="sm" variant="destructive" onClick={() => handleDeleteFaq(faq.id)}>
                            <Trash2 className="size-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tickets Tab */}
        <TabsContent value="tickets" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Support Tickets</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>ID</TableHead>
                    <TableHead>Tiêu đề</TableHead>
                    <TableHead>Người dùng</TableHead>
                    <TableHead>Ưu tiên</TableHead>
                    <TableHead>Trạng thái</TableHead>
                    <TableHead>Ngày tạo</TableHead>
                    <TableHead></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {tickets.map((ticket) => (
                    <TableRow key={ticket.id}>
                      <TableCell>#{ticket.id}</TableCell>
                      <TableCell className="font-medium max-w-xs">{ticket.subject}</TableCell>
                      <TableCell>{ticket.user}</TableCell>
                      <TableCell>
                        <Badge variant={ticket.priority === 'high' ? 'destructive' : 'secondary'}>
                          {ticket.priority === 'high' ? 'Cao' : 'Trung bình'}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <Badge variant={ticket.status === 'open' ? 'default' : 'secondary'}>
                          {ticket.status === 'open' ? 'Đang xử lý' : 'Đã xử lý'}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-sm text-gray-600">{ticket.createdAt}</TableCell>
                      <TableCell>
                        {ticket.status === 'open' ? (
                          <Button size="sm" onClick={() => handleUpdateTicketStatus(ticket.id, 'handled')}>
                            Đánh dấu đã xử lý
                          </Button>
                        ) : (
                          <Button size="sm" variant="outline">
                            Xem chi tiết
                          </Button>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Feedback Tab */}
        <TabsContent value="feedback" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Feedback từ người dùng</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Loại</TableHead>
                    <TableHead>Nội dung</TableHead>
                    <TableHead>Người dùng</TableHead>
                    <TableHead>Ngày tạo</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {feedback.map((item) => (
                    <TableRow key={item.id}>
                      <TableCell>
                        <Badge variant={item.type === 'bug' ? 'destructive' : 'default'}>
                          {item.type === 'bug' ? 'Báo lỗi' : 'Góp ý'}
                        </Badge>
                      </TableCell>
                      <TableCell className="font-medium max-w-md">{item.content}</TableCell>
                      <TableCell>{item.user}</TableCell>
                      <TableCell className="text-sm text-gray-600">{item.createdAt}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* FAQ Dialog */}
      <Dialog open={showFaqDialog} onOpenChange={setShowFaqDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>{editingFaq ? 'Chỉnh sửa FAQ' : 'Tạo FAQ mới'}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="question">Câu hỏi</Label>
              <Input
                id="question"
                placeholder="Câu hỏi thường gặp..."
                value={faqForm.question}
                onChange={(e) => setFaqForm({ ...faqForm, question: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="category">Danh mục</Label>
              <Input
                id="category"
                placeholder="VD: Thực phẩm, Tập luyện..."
                value={faqForm.category}
                onChange={(e) => setFaqForm({ ...faqForm, category: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="answer">Câu trả lời</Label>
              <Textarea
                id="answer"
                placeholder="Câu trả lời chi tiết..."
                value={faqForm.answer}
                onChange={(e) => setFaqForm({ ...faqForm, answer: e.target.value })}
                rows={5}
              />
            </div>
            <div className="flex gap-2">
              <Button onClick={handleCreateFaq} className="flex-1">
                {editingFaq ? 'Cập nhật' : 'Tạo mới'}
              </Button>
              <Button variant="outline" onClick={() => {
                setShowFaqDialog(false);
                setEditingFaq(null);
                setFaqForm({ question: '', answer: '', category: '' });
              }}>
                Hủy
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
