import { useState } from 'react';
import { Search, Filter, MoreVertical, Shield, Ban, RefreshCw } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Input } from '../ui/input';
import { Button } from '../ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../ui/table';
import { Badge } from '../ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '../ui/dropdown-menu';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../ui/dialog';
import { toast } from 'sonner';

const users = [
  { id: 1, name: 'Nguyễn Văn A', email: 'nguyenvana@email.com', role: 'user', status: 'active', streak: 7, lastActive: '2 phút trước' },
  { id: 2, name: 'Trần Thị B', email: 'tranthib@email.com', role: 'user', status: 'active', streak: 15, lastActive: '1 giờ trước' },
  { id: 3, name: 'Lê Văn C', email: 'levanc@email.com', role: 'premium', status: 'active', streak: 30, lastActive: '5 phút trước' },
  { id: 4, name: 'Phạm Thị D', email: 'phamthid@email.com', role: 'user', status: 'inactive', streak: 0, lastActive: '2 ngày trước' },
  { id: 5, name: 'Hoàng Văn E', email: 'hoangvane@email.com', role: 'user', status: 'active', streak: 3, lastActive: '30 phút trước' },
];

export default function UserManagement() {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterRole, setFilterRole] = useState('all');
  const [filterStatus, setFilterStatus] = useState('all');
  const [selectedUser, setSelectedUser] = useState<any>(null);

  const handleGrantRole = (userId: number, role: string) => {
    toast.success(`Đã cấp quyền ${role} cho người dùng #${userId}`);
  };

  const handleResetUser = (userId: number) => {
    toast.success(`Đã reset dữ liệu người dùng #${userId}`);
  };

  const handleBanUser = (userId: number) => {
    toast.warning(`Đã khóa tài khoản #${userId}`);
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Quản lý người dùng</h1>
          <p className="text-gray-600 mt-1">Tổng số: {users.length} người dùng</p>
        </div>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="md:col-span-2">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-gray-400" />
                <Input
                  placeholder="Tìm kiếm theo tên hoặc email..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>

            <Select value={filterRole} onValueChange={setFilterRole}>
              <SelectTrigger>
                <SelectValue placeholder="Lọc theo vai trò" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tất cả vai trò</SelectItem>
                <SelectItem value="user">User</SelectItem>
                <SelectItem value="premium">Premium</SelectItem>
                <SelectItem value="admin">Admin</SelectItem>
              </SelectContent>
            </Select>

            <Select value={filterStatus} onValueChange={setFilterStatus}>
              <SelectTrigger>
                <SelectValue placeholder="Lọc theo trạng thái" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tất cả trạng thái</SelectItem>
                <SelectItem value="active">Hoạt động</SelectItem>
                <SelectItem value="inactive">Không hoạt động</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Users Table */}
      <Card>
        <CardHeader>
          <CardTitle>Danh sách người dùng</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>ID</TableHead>
                <TableHead>Tên</TableHead>
                <TableHead>Email</TableHead>
                <TableHead>Vai trò</TableHead>
                <TableHead>Trạng thái</TableHead>
                <TableHead>Streak</TableHead>
                <TableHead>Hoạt động</TableHead>
                <TableHead></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {users.map((user) => (
                <TableRow key={user.id}>
                  <TableCell>#{user.id}</TableCell>
                  <TableCell className="font-medium">{user.name}</TableCell>
                  <TableCell>{user.email}</TableCell>
                  <TableCell>
                    <Badge variant={user.role === 'admin' ? 'default' : user.role === 'premium' ? 'secondary' : 'outline'}>
                      {user.role}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Badge variant={user.status === 'active' ? 'default' : 'secondary'}>
                      {user.status === 'active' ? 'Hoạt động' : 'Không hoạt động'}
                    </Badge>
                  </TableCell>
                  <TableCell>{user.streak} ngày</TableCell>
                  <TableCell className="text-sm text-gray-600">{user.lastActive}</TableCell>
                  <TableCell>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="icon">
                          <MoreVertical className="size-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem onClick={() => setSelectedUser(user)}>
                          Xem chi tiết
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => handleGrantRole(user.id, 'premium')}>
                          <Shield className="size-4 mr-2" />
                          Cấp Premium
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => handleResetUser(user.id)}>
                          <RefreshCw className="size-4 mr-2" />
                          Reset dữ liệu
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => handleBanUser(user.id)} className="text-red-600">
                          <Ban className="size-4 mr-2" />
                          Khóa tài khoản
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* User Detail Dialog */}
      <Dialog open={!!selectedUser} onOpenChange={() => setSelectedUser(null)}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Chi tiết người dùng</DialogTitle>
          </DialogHeader>
          {selectedUser && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Tên</p>
                  <p className="font-semibold">{selectedUser.name}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Email</p>
                  <p className="font-semibold">{selectedUser.email}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Vai trò</p>
                  <Badge>{selectedUser.role}</Badge>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Streak</p>
                  <p className="font-semibold">{selectedUser.streak} ngày 🔥</p>
                </div>
              </div>

              <div className="pt-4 border-t">
                <h3 className="font-semibold mb-3">Thống kê</h3>
                <div className="grid grid-cols-3 gap-4">
                  <Card>
                    <CardContent className="pt-4">
                      <p className="text-sm text-gray-600">Tổng bữa ăn</p>
                      <p className="text-2xl font-bold">156</p>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardContent className="pt-4">
                      <p className="text-sm text-gray-600">Tổng bài tập</p>
                      <p className="text-2xl font-bold">48</p>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardContent className="pt-4">
                      <p className="text-sm text-gray-600">Cân nặng giảm</p>
                      <p className="text-2xl font-bold">-3.5 kg</p>
                    </CardContent>
                  </Card>
                </div>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
