import React, { useState, useEffect } from 'react';
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
  message: string;
  username?: string | null;
  user_id?: string | null;
  status: 'open' | 'in_progress' | 'resolved' | 'closed';
  category?: string;
  created_at: string;
  updated_at?: string | null;
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
  const [selectedTicket, setSelectedTicket] = useState<Ticket | null>(null);
  const [showTicketDialog, setShowTicketDialog] = useState(false);

  // 1. Fetch dữ liệu từ Backend
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        // Chỉ lấy tickets từ backend (faqs và feedbacks không có endpoint)
        const { AdminService } = await import('../../../service/admin.service');
        const ticketData = await AdminService.getAllTickets();

        setFaqs([]); // FAQ feature not implemented in backend
        setTickets(ticketData.items || []);
        setFeedbacks([]); // Feedback feature not implemented in backend
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
    toast.error('Tính năng FAQ chưa được triển khai trong backend');
  };

  const handleDeleteFaq = async (id: number) => {
    toast.error('Tính năng FAQ chưa được triển khai trong backend');
  };

  // 3. Xử lý Ticket Status
  const handleUpdateTicketStatus = async (id: number, newStatus: string) => {
    try {
      const { AdminService } = await import('../../../service/admin.service');
      await AdminService.updateTicket(id, { status: newStatus as any });
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
                    <TableRow 
                      key={ticket.id}
                      className="cursor-pointer hover:bg-gray-50"
                      onClick={() => {
                        setSelectedTicket(ticket);
                        setShowTicketDialog(true);
                      }}
                    >
                      <TableCell className="text-gray-400">#{ticket.id}</TableCell>
                      <TableCell className="font-medium">{ticket.subject}</TableCell>
                      <TableCell>
                        {ticket.username || (ticket.user_id ? `User ${ticket.user_id.substring(0, 8)}` : 'Guest')}
                      </TableCell>
                      <TableCell>
                        <Badge 
                          variant={
                            ticket.status === 'open' ? 'default' : 
                            ticket.status === 'in_progress' ? 'default' :
                            'secondary'
                          }
                        >
                          {ticket.status === 'open' ? 'Đang chờ' : 
                           ticket.status === 'in_progress' ? 'Đang xử lý' :
                           ticket.status === 'resolved' ? 'Đã giải quyết' :
                           'Đã đóng'}
                        </Badge>
                      </TableCell>
                      <TableCell>{new Date(ticket.created_at).toLocaleDateString('vi-VN')}</TableCell>
                      <TableCell onClick={(e) => e.stopPropagation()}>
                        {ticket.status === 'open' && (
                          <Button 
                            size="sm" 
                            onClick={() => handleUpdateTicketStatus(ticket.id, 'resolved')}
                          >
                            Xong
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

      {/* Dialog Ticket Detail */}
      <Dialog open={showTicketDialog} onOpenChange={setShowTicketDialog}>
        <DialogContent className="sm:max-w-[700px] max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Chi tiết yêu cầu hỗ trợ #{selectedTicket?.id}</DialogTitle>
          </DialogHeader>
          {selectedTicket && (
            <div className="space-y-4 py-4">
              <div className="grid gap-2">
                <Label className="text-sm font-semibold">Tiêu đề</Label>
                <p className="text-base font-medium">{selectedTicket.subject}</p>
              </div>
              
              <div className="grid gap-2">
                <Label className="text-sm font-semibold">Người gửi</Label>
                <p className="text-base">
                  {selectedTicket.username || (selectedTicket.user_id ? `User ${selectedTicket.user_id.substring(0, 8)}` : 'Guest')}
                  {selectedTicket.user_id && (
                    <span className="text-gray-400 text-sm ml-2">({selectedTicket.user_id})</span>
                  )}
                </p>
              </div>

              <div className="grid gap-2">
                <Label className="text-sm font-semibold">Phân loại</Label>
                <Badge variant="outline">
                  {selectedTicket.category || 'Không phân loại'}
                </Badge>
              </div>

              <div className="grid gap-2">
                <Label className="text-sm font-semibold">Trạng thái</Label>
                <Badge 
                  variant={
                    selectedTicket.status === 'open' ? 'default' : 
                    selectedTicket.status === 'in_progress' ? 'default' :
                    'secondary'
                  }
                >
                  {selectedTicket.status === 'open' ? 'Đang chờ' : 
                   selectedTicket.status === 'in_progress' ? 'Đang xử lý' :
                   selectedTicket.status === 'resolved' ? 'Đã giải quyết' :
                   'Đã đóng'}
                </Badge>
              </div>

              <div className="grid gap-2">
                <Label className="text-sm font-semibold">Nội dung</Label>
                <div className="p-4 bg-gray-50 rounded-lg border">
                  <p className="text-base whitespace-pre-wrap">{selectedTicket.message}</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 text-sm text-gray-500">
                <div>
                  <Label className="text-xs">Ngày tạo</Label>
                  <p>{new Date(selectedTicket.created_at).toLocaleString('vi-VN')}</p>
                </div>
                {selectedTicket.updated_at && (
                  <div>
                    <Label className="text-xs">Cập nhật lần cuối</Label>
                    <p>{new Date(selectedTicket.updated_at).toLocaleString('vi-VN')}</p>
                  </div>
                )}
              </div>

              {selectedTicket.status === 'open' && (
                <div className="flex justify-end gap-2 pt-4 border-t">
                  <Button 
                    variant="outline" 
                    onClick={() => {
                      handleUpdateTicketStatus(selectedTicket.id, 'in_progress');
                      setShowTicketDialog(false);
                    }}
                  >
                    Đánh dấu đang xử lý
                  </Button>
                  <Button 
                    onClick={() => {
                      handleUpdateTicketStatus(selectedTicket.id, 'resolved');
                      setShowTicketDialog(false);
                    }}
                  >
                    Đánh dấu đã giải quyết
                  </Button>
                </div>
              )}
            </div>
          )}
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