import React from 'react';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { cn } from '@/lib/utils';
import {
  Home,
  User,
  Settings,
  Star,
  MessageSquare,
  Calendar,
  Search,
  Plus
} from 'lucide-react';

interface SidebarProps {
  isOpen: boolean;
  currentPage: string;
  onPageChange: (page: string) => void;
}

const navigationItems = [
  { id: 'dashboard', label: 'Dashboard', icon: Home },
  { id: 'courses', label: 'Course Recommender', icon: Search },
  { id: 'roadmaps', label: 'Roadmap Generator', icon: Calendar },
  { id: 'chatbot', label: 'AI Teacher', icon: MessageSquare },
  { id: 'quiz', label: 'Quiz Generator', icon: Plus },
  { id: 'profile', label: 'Profile', icon: User },
  { id: 'settings', label: 'Settings', icon: Settings },
];

const Sidebar = ({ isOpen, currentPage, onPageChange }: SidebarProps) => {
  return (
    <div
      className={cn(
        "fixed left-0 top-16 z-40 h-[calc(100vh-4rem)] w-64 transform bg-card border-r transition-transform duration-200 ease-in-out md:relative md:top-0 md:h-screen md:translate-x-0",
        isOpen ? "translate-x-0" : "-translate-x-full"
      )}
    >
      <ScrollArea className="h-full py-6">
        <div className="space-y-2 px-3">
          {navigationItems.map((item) => (
            <Button
              key={item.id}
              variant={currentPage === item.id ? "secondary" : "ghost"}
              className={cn(
                "w-full justify-start",
                currentPage === item.id && "learning-gradient text-white hover:opacity-90"
              )}
              onClick={() => onPageChange(item.id)}
            >
              <item.icon className="mr-2 h-4 w-4" />
              {item.label}
            </Button>
          ))}
        </div>
      </ScrollArea>
    </div>
  );
};

export default Sidebar;
