import React from 'react';
import { User, LogOut } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '../ui/dropdown-menu';
import { Button } from '../ui/button';
import { Avatar, AvatarFallback } from '../ui/avatar';

interface UserDropdownProps {
  /** User's username */
  username: string;
  /** User's email */
  email?: string;
  /** Callback when Profile is clicked */
  onProfileClick: () => void;
  /** Callback when Logout is clicked */
  onLogoutClick: () => void;
}

export default function UserDropdown({
  username,
  email,
  onProfileClick,
  onLogoutClick,
}: UserDropdownProps) {
  const userInitial = username.charAt(0).toUpperCase();

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          className="flex items-center gap-3 hover:bg-gray-50 px-3 py-2 h-auto"
        >
          <Avatar className="size-8 bg-gradient-to-br from-pink-500 to-purple-600">
            <AvatarFallback className="text-white font-semibold text-sm">
              {userInitial}
            </AvatarFallback>
          </Avatar>
          <div className="text-left hidden sm:block">
            <p className="text-sm font-medium text-gray-900">{username}</p>
            {email && (
              <p className="text-xs text-gray-500">{email}</p>
            )}
          </div>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent 
        align="end" 
        className="w-48 z-[9999]" 
        sideOffset={8}
        side="bottom"
      >
        <DropdownMenuItem
          onClick={onProfileClick}
          className="flex items-center gap-3 cursor-pointer"
        >
          <User className="size-4 text-gray-600" />
          <span className="text-gray-700">Profile</span>
        </DropdownMenuItem>
        <DropdownMenuItem
          onClick={onLogoutClick}
          variant="destructive"
          className="flex items-center gap-3 cursor-pointer"
        >
          <LogOut className="size-4" />
          <span className="font-medium">Logout</span>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

