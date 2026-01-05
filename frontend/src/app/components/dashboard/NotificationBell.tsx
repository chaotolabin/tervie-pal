import React, { useState, useEffect } from 'react';
import { Bell, CheckCircle2, AlertTriangle, Trash2, Inbox } from 'lucide-react';
import { Popover, PopoverContent, PopoverTrigger } from '../ui/popover';
import { Button } from '../ui/button';
import { NotificationService } from '../../../service/notification.service';

interface Notification {
  id: number;
  type: 'approved' | 'rejected' | 'deleted' | 'deleted_article' | 'info' | 'success' | 'warning' | 'error';
  message: string;
  isRead: boolean;
  createdAt: string;
  title?: string;
  name?: string; // Name of the contribution/item
  reason?: string; // For rejected notifications
  link?: string; // Link to navigate when clicked
  entity_type?: string; // Type of entity: 'food', 'exercise', 'article', etc.
  entity_id?: number; // ID of the entity
}

interface NotificationBellProps {
  onNavigate?: (tab: string) => void; // Callback to navigate to different tabs
}

export default function NotificationBell({ onNavigate }: NotificationBellProps = {}) {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  // Generate Vietnamese notification message based on type
  const getNotificationMessage = (notification: any): string => {
    const name = notification.name || notification.title || 'mục này';
    
    switch (notification.type) {
      case 'approved':
      case 'success':
        return `Đóng góp **${name}** của bạn đã được duyệt.`;
      
      case 'rejected':
      case 'error':
        const reason = notification.reason ? ` Lý do: ${notification.reason}.` : '';
        return `Đóng góp **${name}** của bạn không được duyệt.${reason}`;
      
      case 'deleted_article':
        return `Bài viết **${name}** của bạn đã bị xóa do vi phạm quy tắc cộng đồng.`;
      
      case 'deleted':
        const deleteReason = notification.reason ? ` Lý do: ${notification.reason}.` : '';
        return `Đóng góp **${name}** của bạn đã bị xóa.${deleteReason}`;
      
      default:
        // If message already exists from API, use it; otherwise generate default
        return notification.message || `Bạn có thông báo mới về **${name}**.`;
    }
  };

  // Fetch notifications
  const fetchNotifications = async () => {
    try {
      setLoading(true);
      const response = await NotificationService.getMyNotifications({
        limit: 50,
      });
      // Transform API response to match our Notification interface
      const transformedNotifications: Notification[] = (response.items || response || []).map((item: any) => {
        const notification = {
          id: item.id,
          type: item.type || 'info',
          message: item.message || '',
          isRead: item.is_read !== undefined ? item.is_read : (item.isRead !== undefined ? item.isRead : false),
          createdAt: item.created_at || item.createdAt,
          title: item.title,
          name: item.name || item.title,
          reason: item.reason,
          link: item.link,
          entity_type: item.entity_type,
          entity_id: item.entity_id,
        };
        
        // Generate Vietnamese message if not provided
        if (!notification.message) {
          notification.message = getNotificationMessage(notification);
        }
        
        return notification;
      });
      setNotifications(transformedNotifications);
    } catch (error: any) {
      // Only use mock data if endpoint doesn't exist (404)
      // For other errors, show empty state or log error
      if (error?.response?.status === 404) {
        console.log('Notifications API endpoint not found, using mock data');
        setIsUsingMockData(true);
        setNotifications(getMockNotifications());
      } else {
        console.error('Error fetching notifications:', error);
        setIsUsingMockData(false);
        // Don't set mock data for other errors - let user see empty state
        setNotifications([]);
      }
    } finally {
      setLoading(false);
    }
  };

  // Mock data for development/testing
  const getMockNotifications = (): Notification[] => {
    const mockData = [
      {
        id: 1,
        type: 'approved' as const,
        name: 'Phở Bò',
        message: '',
        isRead: false,
        createdAt: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
      },
      {
        id: 2,
        type: 'rejected' as const,
        name: 'Chạy bộ',
        message: '',
        isRead: false,
        createdAt: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
        reason: 'Trùng lặp dữ liệu',
      },
      {
        id: 3,
        type: 'approved' as const,
        name: 'Bánh Mì',
        message: '',
        isRead: true,
        createdAt: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
      },
      {
        id: 4,
        type: 'deleted_article' as const,
        name: 'Mẹo Sống Khỏe',
        message: '',
        isRead: false,
        createdAt: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
      },
    ];
    
    // Generate Vietnamese messages for mock data
    return mockData.map(item => ({
      ...item,
      message: getNotificationMessage(item),
    }));
  };

  useEffect(() => {
    fetchNotifications();
    
    // Poll for new notifications every 30 seconds
    const interval = setInterval(fetchNotifications, 30000);
    return () => clearInterval(interval);
  }, []);

  // Calculate unread count
  const unreadCount = notifications.filter(n => !n.isRead).length;

  // Track if we're using mock data (API returns 404)
  const [isUsingMockData, setIsUsingMockData] = useState(false);

  // Mark notification as read
  const handleMarkAsRead = async (notificationId: number) => {
    // Update state immediately for better UX
    setNotifications(prev =>
      prev.map(n => (n.id === notificationId ? { ...n, isRead: true } : n))
    );

    // Skip API call if using mock data
    if (isUsingMockData) {
      return;
    }

    try {
      await NotificationService.markAsRead(notificationId);
      // Fetch again to ensure sync with backend
      await fetchNotifications();
    } catch (error: any) {
      // If API endpoint doesn't exist (404), switch to mock data mode
      if (error?.response?.status === 404) {
        setIsUsingMockData(true);
        // Keep the local update we already made
      } else {
        console.error('Error marking notification as read:', error);
        // Revert state on error (except 404)
        setNotifications(prev =>
          prev.map(n => (n.id === notificationId ? { ...n, isRead: false } : n))
        );
      }
    }
  };

  // Mark all as read
  const handleMarkAllAsRead = async () => {
    // Update state immediately
    setNotifications(prev => prev.map(n => ({ ...n, isRead: true })));

    // Skip API call if using mock data
    if (isUsingMockData) {
      return;
    }

    try {
      await NotificationService.markAllAsRead();
      // Fetch again to ensure sync with backend
      await fetchNotifications();
    } catch (error: any) {
      // If API endpoint doesn't exist (404), switch to mock data mode
      if (error?.response?.status === 404) {
        setIsUsingMockData(true);
        // Keep the local update we already made
      } else {
        console.error('Error marking all as read:', error);
        // Note: We don't revert "mark all as read" on error as it's a bulk operation
      }
    }
  };

  // Handle notification click - navigate to relevant page
  const handleNotificationClick = (notification: Notification) => {
    // Mark as read if not already read
    if (!notification.isRead) {
      handleMarkAsRead(notification.id);
    }

    // Navigate based on notification type or link
    if (notification.link) {
      // If there's a direct link, use it
      window.location.href = notification.link;
      return;
    }

    // Navigate based on entity type
    if (onNavigate) {
      switch (notification.entity_type) {
        case 'food':
        case 'contribution_food':
          onNavigate('food');
          break;
        case 'exercise':
        case 'contribution_exercise':
          onNavigate('exercise');
          break;
        case 'article':
        case 'post':
          onNavigate('blog');
          break;
        default:
          // For approved/rejected notifications, navigate to food or exercise based on type
          if (notification.type === 'approved' || notification.type === 'rejected') {
            // Try to infer from notification message
            if (notification.message.includes('đóng góp') || notification.message.includes('món ăn')) {
              onNavigate('food');
            } else if (notification.message.includes('bài tập')) {
              onNavigate('exercise');
            }
          }
      }
    }

    // Close popover after navigation
    setIsOpen(false);
  };

  // Get icon and color for notification type
  const getNotificationIcon = (type: Notification['type']) => {
    switch (type) {
      case 'approved':
      case 'success':
        return <CheckCircle2 className="h-5 w-5 text-green-500" />;
      case 'rejected':
      case 'error':
        return <AlertTriangle className="h-5 w-5 text-red-500" />;
      case 'deleted':
      case 'deleted_article':
        return <Trash2 className="h-5 w-5 text-orange-500" />;
      case 'warning':
        return <AlertTriangle className="h-5 w-5 text-yellow-500" />;
      default:
        return <CheckCircle2 className="h-5 w-5 text-blue-500" />;
    }
  };

  // Format relative time in Vietnamese
  const formatRelativeTime = (dateString: string): string => {
    try {
      const date = new Date(dateString);
      const now = new Date();
      const diff = Math.floor((now.getTime() - date.getTime()) / 1000); // Difference in seconds

      if (diff < 60) return 'Vừa xong';
      if (diff < 3600) return `${Math.floor(diff / 60)} phút trước`;
      if (diff < 86400) return `${Math.floor(diff / 3600)} giờ trước`;
      if (diff < 604800) return `${Math.floor(diff / 86400)} ngày trước`;
      if (diff < 2592000) return `${Math.floor(diff / 604800)} tuần trước`;
      if (diff < 31536000) return `${Math.floor(diff / 2592000)} tháng trước`;
      
      return date.toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric' });
    } catch {
      return 'Gần đây';
    }
  };

  return (
    <Popover open={isOpen} onOpenChange={setIsOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          className="relative h-9 w-9 rounded-full hover:bg-gray-100 transition-colors"
          aria-label="Thông báo"
        >
          <Bell className="h-5 w-5 text-yellow-500" />
          {unreadCount > 0 && (
            <span className="absolute top-0 right-0 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-[10px] font-bold text-white">
              {unreadCount > 9 ? '9+' : unreadCount}
            </span>
          )}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-80 p-0 bg-yellow-50" align="end">
        <div className="flex flex-col max-h-[400px]">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b">
            <h3 className="font-semibold text-sm">Thông báo</h3>
            {unreadCount > 0 && (
              <Button
                variant="ghost"
                size="sm"
                className="h-auto py-1 px-2 text-xs text-gray-600 hover:text-gray-900"
                onClick={handleMarkAllAsRead}
              >
                Đánh dấu đã đọc
              </Button>
            )}
          </div>

          {/* Notifications List */}
          <div className="overflow-y-auto max-h-[300px]">
            {loading ? (
              <div className="p-8 text-center text-gray-500 text-sm">
                Đang tải thông báo...
              </div>
            ) : notifications.length === 0 ? (
              <div className="p-8 text-center">
                <Inbox className="h-12 w-12 text-gray-300 mx-auto mb-2" />
                <p className="text-sm text-gray-500">Oopss!!! Chưa có thông báo nào nè! :3</p>
              </div>
            ) : (
              <div className="divide-y">
                {notifications.map((notification) => (
                  <div
                    key={notification.id}
                    className={`p-4 hover:bg-gray-50 transition-colors cursor-pointer ${
                      !notification.isRead ? 'bg-blue-50/50' : 'bg-white'
                    }`}
                    onClick={() => handleNotificationClick(notification)}
                  >
                    <div className="flex gap-3">
                      {/* Icon */}
                      <div className="flex-shrink-0 mt-0.5">
                        {getNotificationIcon(notification.type)}
                      </div>
                      
                      {/* Content */}
                      <div className="flex-1 min-w-0">
                        <p 
                          className={`text-sm ${!notification.isRead ? 'font-medium text-gray-900' : 'text-gray-700'}`}
                          dangerouslySetInnerHTML={{
                            __html: notification.message.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
                          }}
                        />
                        <p className="text-xs text-gray-400 mt-1">
                          {formatRelativeTime(notification.createdAt)}
                        </p>
                      </div>
                      
                      {/* Unread indicator */}
                      {!notification.isRead && (
                        <div className="flex-shrink-0 w-2 h-2 rounded-full bg-blue-500 mt-2" />
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </PopoverContent>
    </Popover>
  );
}

