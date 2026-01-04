import { useState, useEffect } from 'react';
import { HelpCircle, MessageSquare, Bug, Plus, Edit, Trash2, Loader2 } from 'lucide-react';
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

// --- Interfaces cho Type Safety ---
interface FAQ {
  id: number;
  question: string;
  answer: string;
  category: string;
}

interface Ticket {
  id: number;
  subject: string;
  user_name: string;
  status: 'open' | 'handled';
  priority: 'high' | 'medium' | 'low';
  created_at: string;
}

interface Feedback {
  id: number;
  type: 'bug' | 'suggestion';
  content: string;
  user_name: string;
  created_at: string;
}

export default function SupportManagement() {
  // States dữ liệu
  const [faqs, setFaqs] = useState<FAQ[]>([]);
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [feedbacks, setFeedbacks] = useState<Feedback[]>([]);
  
  // States UI
  const [loading, setLoading] = useState(true);
  const [showFaqDialog, setShowFaqDialog] = useState(false);
  const [editingFaq, setEditingFaq] = useState<FAQ | null>(null);
  const [faqForm, setFaqForm] = useState({ question: '', answer: '', category: '' });

  // 1. Fetch dữ liệu từ Backend
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        // Bạn có thể dùng Promise.all để gọi đồng thời 3 API
        const [faqRes, ticketRes, feedbackRes] = await Promise.all([
          fetch('/api/v1/admin/faqs'),
          fetch('/api/v1/admin/tickets'),
          fetch('/api/v1/admin/feedbacks')
        ]);

        const faqData = await faqRes.json();
        const ticketData = await ticketRes.json();
        const feedbackData = await feedbackRes.json();

        setFaqs(faqData);
        setTickets(ticketData);
        setFeedbacks(feedbackData);
      } catch (error) {
        toast.error('Không thể tải dữ liệu hỗ trợ');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  // 2. Xử lý FAQ (Create/Update/Delete)
  const handleSaveFaq = async () => {
    if (!faqForm.question || !faqForm.answer) {
      toast.error('Vui lòng điền đầy đủ thông tin');
      return;
    }

    try {
      const url = editingFaq ? `/api/v1/admin/faqs/${editingFaq.id}` : '/api/v1/admin/faqs';
      const method = editingFaq ? 'PUT' : 'POST';

      const res = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(faqForm),
      });

      if (res.ok) {
        toast.success(editingFaq ? 'Đã cập nhật FAQ' : 'Đã tạo FAQ mới');
        setShowFaqDialog(false);
        setEditingFaq(null);
        setFaqForm({ question: '', answer: '', category: '' });
        // Refresh data hoặc update state cục bộ tại đây
      }
    } catch (error) {
      toast.error('Có lỗi xảy ra khi lưu FAQ');
    }
  };

  const handleDeleteFaq = async (id: number) => {
    if (!confirm('Bạn có chắc muốn xóa FAQ này?')) return;
    try {
      await fetch(`/api/v1/admin/faqs/${id}`, { method: 'DELETE' });
      setFaqs(faqs.filter(f => f.id !== id));
      toast.success('Đã xóa FAQ');
    } catch (error) {
      toast.error('Không thể xóa FAQ');
    }
  };

  // 3. Xử lý Ticket Status
  const handleUpdateTicketStatus = async (id: number, newStatus: string) => {
    try {
      await fetch(`/api/v1/admin/tickets/${id}/status`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus }),
      });
      setTickets(tickets.map(t => t.id === id ? { ...t, status: newStatus as any } : t));
      toast.success(`Đã cập nhật ticket #${id}`);
    } catch (error) {
      toast.error('Không thể cập nhật trạng thái');
    }
  };

  if (loading) return <div className="flex justify-center p-20"><Loader2 className="animate-spin size-10 text-green-600" /></div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold">Quản lý hỗ trợ</h1>
          <p className="text-gray-600 mt-1">Quản trị nội dung hướng dẫn và phản hồi người dùng</p>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard title="Tổng FAQ" value={faqs.length} icon={HelpCircle} color="text-blue-500" />
        <StatCard title="Tickets đang mở" value={tickets.filter(t => t.status === 'open').length} icon={MessageSquare} color="text-orange-500" />
        <StatCard title="Feedback mới" value={feedbacks.length} icon={Bug} color="text-purple-500" />
      </div>

      <Tabs defaultValue="faq" className="w-full">
        <TabsList className="grid w-full grid-cols-3 bg-gray-100 p-1">
          <TabsTrigger value="faq">FAQ ({faqs.length})</TabsTrigger>
          <TabsTrigger value="tickets">Tickets ({tickets.length})</TabsTrigger>
          <TabsTrigger value="feedback">Feedback ({feedbacks.length})</TabsTrigger>
        </TabsList>

        {/* --- FAQ Tab --- */}
        <TabsContent value="faq" className="mt-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between border-b mb-4">
              <CardTitle>Cơ sở tri thức (FAQ)</CardTitle>
              <Button onClick={() => { setEditingFaq(null); setShowFaqDialog(true); }}>
                <Plus className="size-4 mr-2" /> Tạo FAQ
              </Button>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Câu hỏi</TableHead>
                    <TableHead>Danh mục</TableHead>
                    <TableHead className="hidden md:table-cell">Câu trả lời</TableHead>
                    <TableHead className="text-right">Thao tác</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {faqs.map((faq) => (
                    <TableRow key={faq.id}>
                      <TableCell className="font-medium">{faq.question}</TableCell>
                      <TableCell><Badge variant="outline">{faq.category}</Badge></TableCell>
                      <TableCell className="max-w-md truncate text-gray-500 hidden md:table-cell">{faq.answer}</TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button size="icon" variant="ghost" onClick={() => {
                            setEditingFaq(faq);
                            setFaqForm({ question: faq.question, answer: faq.answer, category: faq.category });
                            setShowFaqDialog(true);
                          }}><Edit className="size-4" /></Button>
                          <Button size="icon" variant="ghost" className="text-red-500" onClick={() => handleDeleteFaq(faq.id)}><Trash2 className="size-4" /></Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* --- Tickets Tab --- */}
        <TabsContent value="tickets" className="mt-6">
          <Card>
            <CardHeader><CardTitle>Yêu cầu hỗ trợ</CardTitle></CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>ID</TableHead>
                    <TableHead>Tiêu đề</TableHead>
                    <TableHead>Người dùng</TableHead>
                    <TableHead>Trạng thái</TableHead>
                    <TableHead>Ngày tạo</TableHead>
                    <TableHead></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {tickets.map((ticket) => (
                    <TableRow key={ticket.id}>
                      <TableCell className="text-gray-400">#{ticket.id}</TableCell>
                      <TableCell className="font-medium">{ticket.subject}</TableCell>
                      <TableCell>{ticket.user_name}</TableCell>
                      <TableCell>
                        <Badge variant={ticket.status === 'open' ? 'default' : 'secondary'}>
                          {ticket.status === 'open' ? 'Đang chờ' : 'Đã giải quyết'}
                        </Badge>
                      </TableCell>
                      <TableCell>{new Date(ticket.created_at).toLocaleDateString('vi-VN')}</TableCell>
                      <TableCell>
                        {ticket.status === 'open' && (
                          <Button size="sm" onClick={() => handleUpdateTicketStatus(ticket.id, 'handled')}>Xong</Button>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* --- Feedback Tab --- */}
        <TabsContent value="feedback" className="mt-6">
          <Card>
            <CardHeader><CardTitle>Ý kiến phản hồi</CardTitle></CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Loại</TableHead>
                    <TableHead>Nội dung</TableHead>
                    <TableHead>Người dùng</TableHead>
                    <TableHead>Thời gian</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {feedbacks.map((item) => (
                    <TableRow key={item.id}>
                      <TableCell>
                        <Badge variant={item.type === 'bug' ? 'destructive' : 'outline'}>
                          {item.type === 'bug' ? 'Lỗi' : 'Góp ý'}
                        </Badge>
                      </TableCell>
                      <TableCell className="max-w-lg italic">"{item.content}"</TableCell>
                      <TableCell>{item.user_name}</TableCell>
                      <TableCell className="text-xs text-gray-400">
                        {new Date(item.created_at).toLocaleString('vi-VN')}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Dialog FAQ */}
      <Dialog open={showFaqDialog} onOpenChange={setShowFaqDialog}>
        <DialogContent className="sm:max-w-[600px]">
          <DialogHeader>
            <DialogTitle>{editingFaq ? 'Chỉnh sửa câu hỏi' : 'Tạo hướng dẫn mới'}</DialogTitle>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label>Câu hỏi</Label>
              <Input value={faqForm.question} onChange={e => setFaqForm({...faqForm, question: e.target.value})} />
            </div>
            <div className="grid gap-2">
              <Label>Danh mục</Label>
              <Input value={faqForm.category} onChange={e => setFaqForm({...faqForm, category: e.target.value})} />
            </div>
            <div className="grid gap-2">
              <Label>Câu trả lời</Label>
              <Textarea rows={6} value={faqForm.answer} onChange={e => setFaqForm({...faqForm, answer: e.target.value})} />
            </div>
          </div>
          <div className="flex justify-end gap-3">
            <Button variant="outline" onClick={() => setShowFaqDialog(false)}>Hủy</Button>
            <Button onClick={handleSaveFaq}>Lưu thay đổi</Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}

// Component phụ cho Card thống kê
function StatCard({ title, value, icon: Icon, color }: any) {
  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-500 uppercase tracking-wider">{title}</p>
            <p className="text-3xl font-bold mt-1">{value}</p>
          </div>
          <div className={`p-3 rounded-lg bg-gray-50 ${color}`}><Icon className="size-6" /></div>
        </div>
      </CardContent>
    </Card>
  );
}