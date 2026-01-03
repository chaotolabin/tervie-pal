import { useState } from 'react';
import { HelpCircle, MessageSquare, Bug, Info, ChevronRight, Send } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../ui/dialog';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Textarea } from '../ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '../ui/accordion';
import { Badge } from '../ui/badge';
import { toast } from 'sonner';

const faqs = [
  {
    id: 1,
    question: 'Làm sao để tính calories chính xác?',
    answer: 'Để tính calories chính xác, bạn nên cân đo thực phẩm và sử dụng cơ sở dữ liệu thực phẩm của chúng tôi. Nếu không tìm thấy thực phẩm, bạn có thể tự thêm vào với thông tin dinh dưỡng từ bao bì.'
  },
  {
    id: 2,
    question: 'Mục tiêu calories được tính như thế nào?',
    answer: 'Mục tiêu calories được tính dựa trên TDEE (Total Daily Energy Expenditure) của bạn, bao gồm BMR và mức độ hoạt động. Bạn có thể điều chỉnh mục tiêu trong phần Cài đặt.'
  },
  {
    id: 3,
    question: 'Làm sao để theo dõi tiến độ hiệu quả?',
    answer: 'Hãy ghi nhận thực phẩm và tập luyện hàng ngày, cân nặng ít nhất 1 tuần/lần vào cùng thời điểm. Xem biểu đồ trong tab Tiến độ để theo dõi xu hướng.'
  },
  {
    id: 4,
    question: 'Tôi có thể xuất dữ liệu không?',
    answer: 'Có, bạn có thể xuất dữ liệu dưới dạng CSV trong phần Cài đặt > Dữ liệu & Tài khoản > Xuất dữ liệu.'
  }
];

const myTickets = [
  { id: 1, subject: 'Không thể thêm thực phẩm tự tạo', status: 'open', date: '2 ngày trước' },
  { id: 2, subject: 'Câu hỏi về tính năng xuất dữ liệu', status: 'handled', date: '1 tuần trước' }
];

export default function HelpSupport() {
  const [showTicketDialog, setShowTicketDialog] = useState(false);
  const [showFeedbackDialog, setShowFeedbackDialog] = useState(false);
  const [ticketForm, setTicketForm] = useState({ subject: '', message: '' });
  const [feedbackForm, setFeedbackForm] = useState({ type: 'suggestion', content: '' });

  const handleSubmitTicket = () => {
    if (!ticketForm.subject || !ticketForm.message) {
      toast.error('Vui lòng điền đầy đủ thông tin');
      return;
    }
    toast.success('Ticket đã được gửi! Chúng tôi sẽ phản hồi sớm.');
    setShowTicketDialog(false);
    setTicketForm({ subject: '', message: '' });
  };

  const handleSubmitFeedback = () => {
    if (!feedbackForm.content) {
      toast.error('Vui lòng nhập nội dung');
      return;
    }
    toast.success('Cảm ơn phản hồi của bạn!');
    setShowFeedbackDialog(false);
    setFeedbackForm({ type: 'suggestion', content: '' });
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Trợ giúp & Hỗ trợ</h2>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card className="cursor-pointer hover:shadow-md transition-shadow" onClick={() => setShowTicketDialog(true)}>
          <CardContent className="pt-6">
            <div className="flex items-start gap-4">
              <div className="size-12 bg-blue-100 rounded-full flex items-center justify-center">
                <MessageSquare className="size-6 text-blue-600" />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold mb-1">Gửi yêu cầu hỗ trợ</h3>
                <p className="text-sm text-gray-600">Liên hệ với đội ngũ hỗ trợ</p>
              </div>
              <ChevronRight className="size-5 text-gray-400" />
            </div>
          </CardContent>
        </Card>

        <Card className="cursor-pointer hover:shadow-md transition-shadow" onClick={() => setShowFeedbackDialog(true)}>
          <CardContent className="pt-6">
            <div className="flex items-start gap-4">
              <div className="size-12 bg-purple-100 rounded-full flex items-center justify-center">
                <Bug className="size-6 text-purple-600" />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold mb-1">Báo lỗi / Góp ý</h3>
                <p className="text-sm text-gray-600">Gửi feedback cho chúng tôi</p>
              </div>
              <ChevronRight className="size-5 text-gray-400" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* System Status */}
      <Card className="border-green-200 bg-green-50">
        <CardContent className="pt-6">
          <div className="flex items-start gap-4">
            <div className="size-12 bg-green-100 rounded-full flex items-center justify-center">
              <Info className="size-6 text-green-600" />
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <h3 className="font-semibold">Trạng thái hệ thống</h3>
                <Badge variant="default" className="bg-green-600">Bình thường</Badge>
              </div>
              <p className="text-sm text-gray-600">Tất cả các dịch vụ đang hoạt động tốt</p>
              <p className="text-xs text-gray-500 mt-2">Cập nhật lần cuối: 5 phút trước</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* My Tickets */}
      {myTickets.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Yêu cầu của tôi</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {myTickets.map((ticket) => (
              <div key={ticket.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex-1">
                  <p className="font-semibold text-sm">{ticket.subject}</p>
                  <p className="text-xs text-gray-600">{ticket.date}</p>
                </div>
                <Badge variant={ticket.status === 'open' ? 'default' : 'secondary'}>
                  {ticket.status === 'open' ? 'Đang xử lý' : 'Đã xử lý'}
                </Badge>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* FAQ Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <HelpCircle className="size-5" />
            Câu hỏi thường gặp
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Accordion type="single" collapsible className="w-full">
            {faqs.map((faq) => (
              <AccordionItem key={faq.id} value={`item-${faq.id}`}>
                <AccordionTrigger>{faq.question}</AccordionTrigger>
                <AccordionContent className="text-gray-600">
                  {faq.answer}
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </CardContent>
      </Card>

      {/* Submit Ticket Dialog */}
      <Dialog open={showTicketDialog} onOpenChange={setShowTicketDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Gửi yêu cầu hỗ trợ</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="subject">Tiêu đề</Label>
              <Input
                id="subject"
                placeholder="Mô tả vấn đề của bạn..."
                value={ticketForm.subject}
                onChange={(e) => setTicketForm({ ...ticketForm, subject: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="message">Chi tiết</Label>
              <Textarea
                id="message"
                placeholder="Mô tả chi tiết vấn đề bạn gặp phải..."
                value={ticketForm.message}
                onChange={(e) => setTicketForm({ ...ticketForm, message: e.target.value })}
                rows={5}
              />
            </div>
            <div className="flex gap-2">
              <Button onClick={handleSubmitTicket} className="flex-1">
                <Send className="size-4 mr-2" />
                Gửi yêu cầu
              </Button>
              <Button variant="outline" onClick={() => setShowTicketDialog(false)}>
                Hủy
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Feedback Dialog */}
      <Dialog open={showFeedbackDialog} onOpenChange={setShowFeedbackDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Báo lỗi / Góp ý</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="feedbackType">Loại</Label>
              <Select value={feedbackForm.type} onValueChange={(value) => setFeedbackForm({ ...feedbackForm, type: value })}>
                <SelectTrigger id="feedbackType">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="bug">Báo lỗi</SelectItem>
                  <SelectItem value="suggestion">Góp ý</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="feedbackContent">Nội dung</Label>
              <Textarea
                id="feedbackContent"
                placeholder="Chia sẻ ý kiến của bạn..."
                value={feedbackForm.content}
                onChange={(e) => setFeedbackForm({ ...feedbackForm, content: e.target.value })}
                rows={5}
              />
            </div>
            <div className="flex gap-2">
              <Button onClick={handleSubmitFeedback} className="flex-1">
                <Send className="size-4 mr-2" />
                Gửi feedback
              </Button>
              <Button variant="outline" onClick={() => setShowFeedbackDialog(false)}>
                Hủy
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
