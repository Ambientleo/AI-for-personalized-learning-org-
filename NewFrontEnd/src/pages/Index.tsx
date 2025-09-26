import React, { useState, useEffect } from 'react';
import Header from '@/components/Header';
import Sidebar from '@/components/Sidebar';
import Dashboard from '@/components/Dashboard';
import CourseRecommender from '@/components/CourseRecommender';
import RoadmapGenerator from '@/components/RoadmapGenerator';
import AITeacher from '@/components/AITeacher';
import QuizGenerator from '@/components/QuizGenerator';
import Profile from '@/components/Profile';
import Settings from '@/components/Settings';

const Index = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [darkMode, setDarkMode] = useState(false);

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  // Listen for navigation events from child components
  useEffect(() => {
    const handleNavigation = (event: CustomEvent) => {
      if (event.detail && event.detail.page) {
        setCurrentPage(event.detail.page);
        setSidebarOpen(false);
      }
    };

    window.addEventListener('navigateToPage', handleNavigation as EventListener);
    
    return () => {
      window.removeEventListener('navigateToPage', handleNavigation as EventListener);
    };
  }, []);

  const handlePageChange = (page: string) => {
    setCurrentPage(page);
    setSidebarOpen(false); // Close sidebar on mobile after navigation
  };

  const renderPage = () => {
    switch (currentPage) {
      case 'courses':
        return <CourseRecommender />;
      case 'roadmaps':
        return <RoadmapGenerator />;
      case 'chatbot':
        return <AITeacher />;
      case 'quiz':
        return <QuizGenerator />;
      case 'profile':
        return <Profile />;
      case 'settings':
        return <Settings />;
      default:
        return <Dashboard onPageChange={handlePageChange} />;
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Header 
        onMenuClick={() => setSidebarOpen(!sidebarOpen)}
        darkMode={darkMode}
        onToggleDarkMode={() => setDarkMode(!darkMode)}
      />
      
      <div className="flex">
        <Sidebar 
          isOpen={sidebarOpen}
          currentPage={currentPage}
          onPageChange={handlePageChange}
        />
        
        {/* Overlay for mobile */}
        {sidebarOpen && (
          <div 
            className="fixed inset-0 z-30 bg-black/50 md:hidden" 
            onClick={() => setSidebarOpen(false)}
          />
        )}
        
        <main className="flex-1 p-6 md:ml-0">
          <div className="mx-auto max-w-7xl">
            {renderPage()}
          </div>
        </main>
      </div>
    </div>
  );
};

export default Index;
