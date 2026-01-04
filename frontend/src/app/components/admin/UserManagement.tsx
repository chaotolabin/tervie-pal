import { useState, useEffect } from 'react';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../ui/table';
import { Badge } from '../ui/badge';
import { Loader2, UserX, Search } from 'lucide-react';
import { toast } from 'sonner';

// Định nghĩa cấu trúc dữ liệu từ API
interface User {
  user_id: string | number;
  full_name: string | null;
  gender: 'male' | 'female' | string;
  height_cm_default: number;
  created_at: string;
}

export default function UserManagement() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        setLoading(true);
        const response = await fetch('/api/v1/admin/users');
        
        if (!response.ok) {
          throw new Error('Không thể lấy danh sách người dùng');
        }

        const data = await response.json();
        // Giả sử API trả về mảng trực tiếp hoặc data.users
        setUsers(Array.isArray(data) ? data : data.users || []);
      } catch (error) {
        console.error("Fetch Users Error:", error);
        toast.error("Lỗi kết nối: Không thể tải danh sách người dùng");
      } finally {
        setLoading(false);
      }
    };

    fetchUsers();
  }, []);

  return (
    <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
      <div className="p-6 border-b flex justify-between items-center bg-gray-50/50">
        <div>
          <h2 className="text-xl font-bold text-gray-800">Quản lý người dùng</h2>
          <p className="text-sm text-gray-500">Danh sách tất cả thành viên trong hệ thống</p>
        </div>
        <div className="text-sm font-medium bg-green-100 text-green-700 px-3 py-1 rounded-full">
          Tổng cộng: {users.length}
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
                  <TableHead className="w-[250px]">Họ và tên</TableHead>
                  <TableHead>Giới tính</TableHead>
                  <TableHead>Chiều cao</TableHead>
                  <TableHead>Ngày tham gia</TableHead>
                  <TableHead className="text-right">Trạng thái</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {users.map((user) => (
                  <TableRow key={user.user_id} className="hover:bg-gray-50/50 transition-colors">
                    <TableCell className="font-semibold text-gray-700">
                      {user.full_name || 'Chưa cập nhật'}
                    </TableCell>
                    <TableCell>
                      <Badge 
                        variant="secondary" 
                        className={user.gender === 'male' ? 'bg-blue-50 text-blue-700' : 'bg-pink-50 text-pink-700'}
                      >
                        {user.gender === 'male' ? 'Nam' : 'Nữ'}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <span className="font-mono">{user.height_cm_default}</span> 
                      <span className="text-gray-400 text-xs ml-1">cm</span>
                    </TableCell>
                    <TableCell className="text-gray-600">
                      {new Date(user.created_at).toLocaleDateString('vi-VN', {
                        year: 'numeric',
                        month: '2-digit',
                        day: '2-digit'
                      })}
                    </TableCell>
                    <TableCell className="text-right">
                       <Badge className="bg-green-500/10 text-green-600 border-none">Hoạt động</Badge>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        )}
      </div>
    </div>
  );
}