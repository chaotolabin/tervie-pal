import React, { useState, useEffect } from 'react';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../ui/table';
import { Badge } from '../ui/badge';
import { Loader2, UserX, Search } from 'lucide-react';
import { toast } from 'sonner';

// Định nghĩa cấu trúc dữ liệu từ API
interface User {
  id: string;
  username: string;
  email: string;
  role: string;
  full_name: string | null;
  created_at: string;
  current_streak?: number;
  last_log_at?: string | null;
}

export default function UserManagement() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        setLoading(true);
        const { AdminService } = await import('../../../service/admin.service');
        const data = await AdminService.getUsers({ page, page_size: 50 });
        setUsers(data.items || []);
        setTotalPages(data.total_pages || 1);
        setTotal(data.total || 0);
      } catch (error) {
        console.error("Fetch Users Error:", error);
        toast.error("Lỗi kết nối: Không thể tải danh sách người dùng");
      } finally {
        setLoading(false);
      }
    };

    fetchUsers();
  }, [page]);

  return (
    <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
      <div className="p-6 border-b flex justify-between items-center bg-gray-50/50">
        <div>
          <h2 className="text-xl font-bold text-gray-800">Quản lý người dùng</h2>
          <p className="text-sm text-gray-500">Danh sách tất cả thành viên trong hệ thống</p>
        </div>
        <div className="text-sm font-medium bg-green-100 text-green-700 px-3 py-1 rounded-full">
          Tổng cộng: {total.toLocaleString()}
        </div>
      </div>

      <div className="p-6">
        {loading ? (
          <div className="flex flex-col items-center justify-center py-20 gap-3">
            <Loader2 className="animate-spin text-green-600 size-8" />
            <p className="text-gray-500 text-sm">Đang tải dữ liệu...</p>
          </div>
        ) : users.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-gray-400">
            <UserX className="size-12 mb-2 opacity-20" />
            <p>Chưa có dữ liệu người dùng nào.</p>
          </div>
        ) : (
          <div className="rounded-md border">
            <Table>
              <TableHeader className="bg-gray-50">
                <TableRow>
                  <TableHead className="w-[200px]">Tên người dùng</TableHead>
                  <TableHead>Email</TableHead>
                  <TableHead>Họ và tên</TableHead>
                  <TableHead>Vai trò</TableHead>
                  <TableHead>Streak</TableHead>
                  <TableHead>Ngày tham gia</TableHead>
                  <TableHead className="text-right">Trạng thái</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {users.map((user) => (
                  <TableRow key={user.id} className="hover:bg-gray-50/50 transition-colors">
                    <TableCell className="font-semibold text-gray-700">
                      {user.username}
                    </TableCell>
                    <TableCell className="text-gray-600 text-sm">
                      {user.email}
                    </TableCell>
                    <TableCell>
                      {user.full_name || <span className="text-gray-400 italic">Chưa cập nhật</span>}
                    </TableCell>
                    <TableCell>
                      <Badge 
                        variant={user.role === 'admin' ? 'default' : 'secondary'}
                        className={user.role === 'admin' ? 'bg-purple-100 text-purple-700' : ''}
                      >
                        {user.role === 'admin' ? 'Admin' : 'User'}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      {user.current_streak !== undefined ? (
                        <Badge className="bg-orange-100 text-orange-700 border-none">
                          🔥 {user.current_streak} ngày
                        </Badge>
                      ) : (
                        <span className="text-gray-400">-</span>
                      )}
                    </TableCell>
                    <TableCell className="text-gray-600">
                      {new Date(user.created_at).toLocaleDateString('vi-VN', {
                        year: 'numeric',
                        month: '2-digit',
                        day: '2-digit'
                      })}
                    </TableCell>
                    <TableCell className="text-right">
                      <Badge className="bg-green-500/10 text-green-600 border-none">
                        {user.last_log_at ? 'Hoạt động' : 'Không hoạt động'}
                      </Badge>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        )}
        
        {/* Pagination */}
        {!loading && totalPages > 1 && (
          <div className="flex items-center justify-between mt-6 pt-4 border-t">
            <div className="text-sm text-gray-600">
              Trang {page} / {totalPages}
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Trước
              </button>
              <button
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Sau
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}