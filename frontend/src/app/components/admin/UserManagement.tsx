import { useState, useEffect } from 'react';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../ui/table';
import { Badge } from '../ui/badge';
import { Loader2 } from 'lucide-react';

export default function UserManagement() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/v1/admin/users') 
      .then(res => res.json())
      .then(data => {
        setUsers(data);
        setLoading(false);
      });
  }, []);

  return (
    <div className="bg-white rounded-xl shadow-sm border">
      <div className="p-6 border-b">
        <h2 className="text-xl font-bold">Danh sách người dùng hệ thống</h2>
      </div>
      <div className="p-6">
        {loading ? <Loader2 className="animate-spin mx-auto" /> : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Họ và tên</TableHead>
                <TableHead>Giới tính</TableHead>
                <TableHead>Chiều cao (cm)</TableHead>
                <TableHead>Ngày tham gia</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {users.map((user: any) => (
                <TableRow key={user.user_id}>
                  <TableCell className="font-medium">{user.full_name || 'N/A'}</TableCell>
                  <TableCell>
                    <Badge variant="outline">
                      {user.gender === 'male' ? 'Nam' : 'Nữ'}
                    </Badge>
                  </TableCell>
                  <TableCell>{user.height_cm_default} cm</TableCell>
                  <TableCell>{new Date(user.created_at).toLocaleDateString('vi-VN')}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </div>
    </div>
  );
}