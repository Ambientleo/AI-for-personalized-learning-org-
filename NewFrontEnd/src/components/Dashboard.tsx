import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, BarChart, Bar, AreaChart, Area } from 'recharts';
import { Search, Calendar, MessageSquare, Plus, TrendingUp, Clock, Award, Target, BookOpen, Upload, Brain, Trophy, BarChart3, List, TrendingDown } from 'lucide-react';
import { checkAndUpdateStreak, getActivities, Activity } from '@/utils/activityTracker';

const Dashboard = ({ onPageChange }: { onPageChange: (page: string) => void }) => {
  const [learningStats, setLearningStats] = useState({
    coursesCompleted: 0,
    studyHours: 0,
    quizzesTaken: 0,
    currentStreak: 0,
    totalXP: 0,
    level: 1
  });
  const [activities, setActivities] = useState<Activity[]>([]);
  const [skillViewMode, setSkillViewMode] = useState<'bars' | 'chart' | 'pie'>('bars');
  const [dailyActivityViewMode, setDailyActivityViewMode] = useState<'line' | 'bar'>('line');

  const getUserInfo = () => {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      try {
        return JSON.parse(userStr);
      } catch (e) {
        return null;
      }
    }
    return null;
  };

  const getLearningStats = () => {
    const statsStr = localStorage.getItem('learningStats');
    if (statsStr) {
      try {
        return JSON.parse(statsStr);
      } catch (e) {
        return {
          coursesCompleted: 0,
          studyHours: 0,
          quizzesTaken: 0,
          currentStreak: 0,
          totalXP: 0,
          level: 1
        };
      }
    }
    return {
      coursesCompleted: 0,
      studyHours: 0,
      quizzesTaken: 0,
      currentStreak: 0,
      totalXP: 0,
      level: 1
    };
  };

  // Load data on component mount
  useEffect(() => {
    setLearningStats(getLearningStats());
    setActivities(getActivities());
    
    // Check and update streak when dashboard loads
    const currentStreak = checkAndUpdateStreak();
    console.log('Dashboard loaded - current streak:', currentStreak);
  }, []);

  // Listen for changes in localStorage to update stats
  useEffect(() => {
    const handleStatsUpdate = () => {
      console.log('Dashboard: Stats updated event received');
      const newStats = getLearningStats();
      console.log('Dashboard: New learning stats:', newStats);
      setLearningStats(newStats);
      setActivities(getActivities()); // Also refresh activities
    };
    
    window.addEventListener('statsUpdated', handleStatsUpdate);
    
    return () => {
      window.removeEventListener('statsUpdated', handleStatsUpdate);
    };
  }, []);

  // Helper functions for activity display
  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));
    
    if (diffInMinutes < 1) return 'Just now';
    if (diffInMinutes < 60) return `${diffInMinutes} minutes ago`;
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)} hours ago`;
    return date.toLocaleDateString();
  };

  const getActivityIcon = (type: Activity['type']) => {
    switch (type) {
      case 'quiz': return <BookOpen className="h-4 w-4" />;
      case 'course': return <Award className="h-4 w-4" />;
      case 'chat': return <MessageSquare className="h-4 w-4" />;
      case 'file_upload': return <Upload className="h-4 w-4" />;
      case 'topic_study': return <Brain className="h-4 w-4" />;
      case 'achievement': return <Trophy className="h-4 w-4" />;
      case 'skill_update': return <Target className="h-4 w-4" />;
      default: return <Clock className="h-4 w-4" />;
    }
  };

  const getActivityColor = (type: Activity['type']) => {
    switch (type) {
      case 'quiz': return 'text-blue-600 bg-blue-100';
      case 'course': return 'text-green-600 bg-green-100';
      case 'chat': return 'text-purple-600 bg-purple-100';
      case 'file_upload': return 'text-orange-600 bg-orange-100';
      case 'topic_study': return 'text-indigo-600 bg-indigo-100';
      case 'achievement': return 'text-yellow-600 bg-yellow-100';
      case 'skill_update': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const user = getUserInfo();
  const userName = user?.name || user?.email?.split('@')[0] || 'User';

  // Generate real progress data based on actual activities
  const generateProgressData = () => {
    const last7Days = [];
    const today = new Date();
    
    // Get activities from localStorage
    const allActivities = getActivities();
    
    // Generate data for last 7 days
    for (let i = 6; i >= 0; i--) {
      const date = new Date(today);
      date.setDate(date.getDate() - i);
      const dateString = date.toDateString();
      
      // Count activities for this specific day
      const dayActivities = allActivities.filter(activity => {
        const activityDate = new Date(activity.timestamp).toDateString();
        return activityDate === dateString;
      });
      
      last7Days.push({
        name: date.toLocaleDateString('en-US', { weekday: 'short' }),
        date: dateString,
        activities: dayActivities.length,
        progress: dayActivities.length // Use activity count as progress
      });
    }
    
    return last7Days;
  };

  const progressData = generateProgressData();

  const skillData = [
    { name: 'JavaScript', value: 85, color: '#3b82f6' },
    { name: 'React', value: 75, color: '#8b5cf6' },
    { name: 'Python', value: 65, color: '#10b981' },
    { name: 'AI/ML', value: 45, color: '#f59e0b' },
  ];

  const features = [
    {
      id: 'courses',
      title: 'Course Recommender',
      description: 'Discover personalized courses based on your learning goals',
      icon: Search,
      color: 'bg-blue-500',
      stats: '1,200+ courses'
    },
    {
      id: 'roadmaps',
      title: 'Roadmap Generator',
      description: 'Create structured learning paths for any skill',
      icon: Calendar,
      color: 'bg-purple-500',
      stats: '50+ templates'
    },
    {
      id: 'chatbot',
      title: 'AI Teacher',
      description: 'Get instant help and explanations from our AI tutor',
      icon: MessageSquare,
      color: 'bg-green-500',
      stats: '24/7 available'
    },
    {
      id: 'quiz',
      title: 'Quiz Generator',
      description: 'Create interactive quizzes from any content',
      icon: Plus,
      color: 'bg-orange-500',
      stats: 'Unlimited quizzes'
    },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Welcome Section */}
      <div className="learning-gradient rounded-xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">Welcome back, {userName}!</h1>
            <p className="text-blue-100 mb-4">Continue your learning journey and achieve your goals</p>
            <div className="flex space-x-4 text-sm">
              <div className="flex items-center">
                <Award className="h-4 w-4 mr-1" />
                <span>Level {learningStats.level}</span>
              </div>
              <div className="flex items-center">
                <Target className="h-4 w-4 mr-1" />
                <span>{learningStats.totalXP} XP</span>
              </div>
              <div className="flex items-center">
                <TrendingUp className="h-4 w-4 mr-1" />
                <span>{learningStats.currentStreak} day streak</span>
              </div>
            </div>
          </div>
          <div className="hidden md:block animate-float">
            <div className="w-24 h-24 bg-white/20 rounded-full flex items-center justify-center">
              <Award className="h-12 w-12 text-white" />
            </div>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Courses Completed</p>
                <p className="text-2xl font-bold">{learningStats.coursesCompleted}</p>
              </div>
              <div className="h-12 w-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <Award className="h-6 w-6 text-blue-600" />
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Study Hours</p>
                <p className="text-2xl font-bold">{learningStats.studyHours}</p>
              </div>
              <div className="h-12 w-12 bg-purple-100 rounded-lg flex items-center justify-center">
                <Clock className="h-6 w-6 text-purple-600" />
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Quizzes Taken</p>
                <p className="text-2xl font-bold">{learningStats.quizzesTaken}</p>
              </div>
              <div className="h-12 w-12 bg-green-100 rounded-lg flex items-center justify-center">
                <Target className="h-6 w-6 text-green-600" />
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Current Streak</p>
                <p className="text-2xl font-bold">{learningStats.currentStreak} days</p>
              </div>
              <div className="h-12 w-12 bg-orange-100 rounded-lg flex items-center justify-center">
                <TrendingUp className="h-6 w-6 text-orange-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Features */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {features.map((feature) => (
          <Card key={feature.id} className="feature-card cursor-pointer" onClick={() => onPageChange(feature.id)}>
            <CardHeader className="flex flex-row items-center space-y-0 pb-2">
              <div className={`h-10 w-10 ${feature.color} rounded-lg flex items-center justify-center mr-4`}>
                <feature.icon className="h-5 w-5 text-white" />
              </div>
              <div className="flex-1">
                <CardTitle className="text-lg">{feature.title}</CardTitle>
                <CardDescription>{feature.description}</CardDescription>
              </div>
            </CardHeader>
            <CardContent>
              <Badge variant="secondary">{feature.stats}</Badge>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Analytics Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Daily Learning Activity</CardTitle>
                <CardDescription>Number of activities performed each day (last 7 days)</CardDescription>
              </div>
              <div className="flex space-x-1">
                <Button
                  variant={dailyActivityViewMode === 'line' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setDailyActivityViewMode('line')}
                  className="h-8 px-2"
                >
                  <TrendingUp className="h-3 w-3 mr-1" />
                  Line
                </Button>
                <Button
                  variant={dailyActivityViewMode === 'bar' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setDailyActivityViewMode('bar')}
                  className="h-8 px-2"
                >
                  <BarChart3 className="h-3 w-3 mr-1" />
                  Bar
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {dailyActivityViewMode === 'line' ? (
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={progressData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip 
                    formatter={(value, name) => [
                      `${value} activities`, 
                      'Daily Activities'
                    ]}
                    labelFormatter={(label) => `Day: ${label}`}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="progress" 
                    stroke="#8b5cf6" 
                    strokeWidth={2}
                    dot={{ fill: '#8b5cf6', strokeWidth: 2, r: 4 }}
                    activeDot={{ r: 6, stroke: '#8b5cf6', strokeWidth: 2 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={progressData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip 
                    formatter={(value, name) => [
                      `${value} activities`, 
                      'Daily Activities'
                    ]}
                    labelFormatter={(label) => `Day: ${label}`}
                  />
                  <Bar dataKey="progress" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Skill Distribution</CardTitle>
                <CardDescription>Your expertise across different areas</CardDescription>
              </div>
              <div className="flex space-x-1">
                <Button
                  variant={skillViewMode === 'bars' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setSkillViewMode('bars')}
                  className="h-8 px-2"
                >
                  <List className="h-3 w-3 mr-1" />
                  Bars
                </Button>
                <Button
                  variant={skillViewMode === 'chart' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setSkillViewMode('chart')}
                  className="h-8 px-2"
                >
                  <BarChart3 className="h-3 w-3 mr-1" />
                  Chart
                </Button>
                <Button
                  variant={skillViewMode === 'pie' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setSkillViewMode('pie')}
                  className="h-8 px-2"
                >
                  <Target className="h-3 w-3 mr-1" />
                  Pie
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {skillViewMode === 'bars' ? (
              <div className="space-y-4">
                {skillData.map((skill) => (
                  <div key={skill.name}>
                    <div className="flex justify-between text-sm">
                      <span>{skill.name}</span>
                      <span>{skill.value}%</span>
                    </div>
                    <Progress value={skill.value} className="h-2" />
                  </div>
                ))}
              </div>
            ) : skillViewMode === 'chart' ? (
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={skillData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip 
                    formatter={(value, name) => [
                      `${value}%`, 
                      'Skill Level'
                    ]}
                  />
                  <Bar dataKey="value" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie
                    data={skillData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, value }) => `${name}: ${value}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {skillData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip 
                    formatter={(value, name) => [
                      `${value}%`, 
                      'Skill Level'
                    ]}
                  />
                </PieChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
          <CardDescription>Your latest learning activities</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {activities.length > 0 ? (
              activities.slice(0, 5).map((activity) => (
                <div key={activity.id} className="flex items-center space-x-3 p-3 rounded-lg bg-muted/50 hover:bg-muted/70 transition-colors">
                  <div className={`p-2 rounded-full ${getActivityColor(activity.type)}`}>
                    {getActivityIcon(activity.type)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-sm">{activity.title}</p>
                    <p className="text-xs text-muted-foreground truncate">{activity.description}</p>
                    <p className="text-xs text-muted-foreground">{formatTimestamp(activity.timestamp)}</p>
                  </div>
                  <div className="text-right">
                    {activity.metadata?.score !== undefined && (
                      <Badge variant="secondary" className="text-xs">
                        {activity.metadata.score}%
                      </Badge>
                    )}
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <p>No activities yet</p>
                <p className="text-sm">Start learning to see your activities here!</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Dashboard;
