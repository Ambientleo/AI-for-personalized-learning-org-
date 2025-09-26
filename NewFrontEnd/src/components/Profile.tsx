import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  User, 
  Mail, 
  Phone, 
  MapPin, 
  Edit, 
  Save, 
  X, 
  Award, 
  Calendar, 
  Target, 
  BookOpen, 
  MessageSquare, 
  Upload, 
  Brain, 
  Trophy, 
  Clock,
  Camera,
  Plus,
  Minus
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { Activity, getActivities, trackSkillUpdateActivity, trackAchievementActivity, trackQuizActivity, trackChatActivity, trackTopicStudyActivity, checkAndUpdateStreak } from '@/utils/activityTracker';
import { Progress } from '@/components/ui/progress';

interface UserProfile {
  id: string;
  name: string;
  email: string;
  phone: string;
  location: string;
  bio: string;
  joinDate: string;
  avatar?: string;
}

interface LearningStats {
  coursesCompleted: number;
  studyHours: number;
  quizzesTaken: number;
  currentStreak: number;
  totalXP: number;
  level: number;
  lastActivityDate: string;
}

interface Achievement {
  id: string;
  title: string;
  date: string;
  icon: string;
  description: string;
}

interface Skill {
  name: string;
  level: number;
  color: string;
  lastUpdated: string;
}

const Profile = () => {
  const { toast } = useToast();

  // Get user data from localStorage
  const getUserData = (): UserProfile | null => {
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

  // Get learning stats from localStorage
  const getLearningStats = (): LearningStats => {
    const statsStr = localStorage.getItem('learningStats');
    if (statsStr) {
      try {
        return JSON.parse(statsStr);
      } catch (e) {
        return getDefaultLearningStats();
      }
    }
    return getDefaultLearningStats();
  };

  const getDefaultLearningStats = (): LearningStats => ({
    coursesCompleted: 0,
    studyHours: 0,
    quizzesTaken: 0,
    currentStreak: 0,
    totalXP: 0,
    level: 1,
    lastActivityDate: ''
  });

  // Get achievements from localStorage
  const getAchievements = (): Achievement[] => {
    const achievementsStr = localStorage.getItem('achievements');
    if (achievementsStr) {
      try {
        return JSON.parse(achievementsStr);
      } catch (e) {
        return [];
      }
    }
    return [];
  };

  // Get skills from localStorage
  const getSkills = (): Skill[] => {
    const skillsStr = localStorage.getItem('skills');
    if (skillsStr) {
      try {
        return JSON.parse(skillsStr);
      } catch (e) {
        return getDefaultSkills();
      }
    }
    return getDefaultSkills();
  };

  const getDefaultSkills = (): Skill[] => [
    { name: 'JavaScript', level: 0, color: 'bg-yellow-500', lastUpdated: new Date().toISOString() },
    { name: 'React', level: 0, color: 'bg-blue-500', lastUpdated: new Date().toISOString() },
    { name: 'Python', level: 0, color: 'bg-green-500', lastUpdated: new Date().toISOString() },
    { name: 'HTML/CSS', level: 0, color: 'bg-orange-500', lastUpdated: new Date().toISOString() },
    { name: 'Node.js', level: 0, color: 'bg-purple-500', lastUpdated: new Date().toISOString() },
    { name: 'TypeScript', level: 0, color: 'bg-blue-600', lastUpdated: new Date().toISOString() }
  ];

  const [profile, setProfile] = useState<UserProfile>({
    id: '',
    name: '',
    email: '',
    phone: '',
    location: '',
    bio: '',
    joinDate: '',
    avatar: ''
  });
  const [isEditingBio, setIsEditingBio] = useState(false);
  const [learningStats, setLearningStats] = useState<LearningStats>(getDefaultLearningStats());
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [skills, setSkills] = useState<Skill[]>([]);
  const [activities, setActivities] = useState<Activity[]>([]);
  const [isUploadingAvatar, setIsUploadingAvatar] = useState(false);
  const [avatarKey, setAvatarKey] = useState(0);
  
  // Load data on component mount
  useEffect(() => {
    console.log('Profile component mounting - loading user data');
    const userData = getUserData();
    console.log('User data from localStorage:', userData);
    
    if (userData) {
      console.log('Setting profile with user data:', userData);
      setProfile(userData);
    } else {
      console.log('No user data found in localStorage');
    }
    
    const learningStatsData = getLearningStats();
    console.log('Learning stats from localStorage:', learningStatsData);
    setLearningStats(learningStatsData);
    
    const achievementsData = getAchievements();
    console.log('Achievements from localStorage:', achievementsData);
    setAchievements(achievementsData);
    
    const skillsData = getSkills();
    console.log('Skills from localStorage:', skillsData);
    setSkills(skillsData);
    
    const activitiesData = getActivities();
    console.log('Activities from localStorage:', activitiesData);
    setActivities(activitiesData);
  }, []);

  // Listen for changes in localStorage to update stats
  useEffect(() => {
    const handleStorageChange = () => {
      setLearningStats(getLearningStats());
      setAchievements(getAchievements());
      setSkills(getSkills());
      setActivities(getActivities());
    };

    window.addEventListener('storage', handleStorageChange);
    
    // Also listen for custom events when stats are updated
    const handleStatsUpdate = () => {
      console.log('Profile: Stats updated event received');
      const newStats = getLearningStats();
      console.log('Profile: New learning stats:', newStats);
      setLearningStats(newStats);
    };
    
    window.addEventListener('statsUpdated', handleStatsUpdate);
    
    return () => {
      window.removeEventListener('storage', handleStorageChange);
      window.removeEventListener('statsUpdated', handleStatsUpdate);
    };
  }, []);

  // Save bio
  const saveBio = () => {
    try {
      localStorage.setItem('user', JSON.stringify(profile));
      setIsEditingBio(false);
      toast({
        title: "Bio updated!",
        description: "Your bio has been saved successfully.",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to save bio. Please try again.",
        variant: "destructive",
      });
    }
  };

  // Add achievement
  const addAchievement = (title: string, description: string, icon: string) => {
    const newAchievement: Achievement = {
      id: Date.now().toString(),
      title,
      description,
      icon,
      date: new Date().toISOString().split('T')[0]
    };
    const updatedAchievements = [...achievements, newAchievement];
    setAchievements(updatedAchievements);
    localStorage.setItem('achievements', JSON.stringify(updatedAchievements));
    
    // Track achievement activity
    trackAchievementActivity(title);
    
    toast({
      title: "Achievement unlocked!",
      description: `Congratulations! You've earned: ${title}`,
    });
  };

  // Update skill level
  const updateSkillLevel = (skillName: string, newLevel: number) => {
    const updatedSkills = skills.map(skill => 
      skill.name === skillName 
        ? { ...skill, level: Math.max(0, Math.min(100, newLevel)), lastUpdated: new Date().toISOString() }
        : skill
    );
    setSkills(updatedSkills);
    localStorage.setItem('skills', JSON.stringify(updatedSkills));
    
    // Track skill update activity
    trackSkillUpdateActivity(skillName, newLevel);
  };

  // Format timestamp for display
  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));
    
    if (diffInMinutes < 1) return 'Just now';
    if (diffInMinutes < 60) return `${diffInMinutes} minutes ago`;
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)} hours ago`;
    return date.toLocaleDateString();
  };

  // Get activity icon component
  const getActivityIcon = (type: Activity['type']) => {
    switch (type) {
      case 'quiz': return <BookOpen className="h-5 w-5" />;
      case 'course': return <Award className="h-5 w-5" />;
      case 'chat': return <MessageSquare className="h-5 w-5" />;
      case 'file_upload': return <Upload className="h-5 w-5" />;
      case 'topic_study': return <Brain className="h-5 w-5" />;
      case 'achievement': return <Trophy className="h-5 w-5" />;
      case 'skill_update': return <Target className="h-5 w-5" />;
      default: return <Clock className="h-5 w-5" />;
    }
  };

  // Get activity color
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

  const learningStatsData = [
    { label: 'Courses Completed', value: learningStats.coursesCompleted, icon: Award },
    { label: 'Study Hours', value: learningStats.studyHours, icon: Calendar },
    { label: 'Quizzes Taken', value: learningStats.quizzesTaken, icon: Target },
    { label: 'Current Streak', value: learningStats.currentStreak, icon: Award }
  ];

  // Handle avatar upload
  const handleAvatarUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    console.log('Avatar upload triggered');
    const file = event.target.files?.[0];
    console.log('Selected file:', file);
    
    if (!file) {
      console.log('No file selected');
      return;
    }

    // Validate file type
    console.log('File type:', file.type);
    if (!file.type.startsWith('image/')) {
      console.log('Invalid file type detected');
      toast({
        title: "Invalid file type",
        description: "Please select an image file (JPEG, PNG, GIF, etc.)",
        variant: "destructive",
      });
      return;
    }

    // Validate file size (max 5MB)
    console.log('File size:', file.size);
    if (file.size > 5 * 1024 * 1024) {
      console.log('File too large');
      toast({
        title: "File too large",
        description: "Please select an image smaller than 5MB",
        variant: "destructive",
      });
      return;
    }

    console.log('Starting file upload process');
    setIsUploadingAvatar(true);

    const reader = new FileReader();
    reader.onload = (e) => {
      console.log('FileReader onload triggered');
      const result = e.target?.result as string;
      console.log('FileReader result length:', result?.length);
      console.log('FileReader result starts with:', result?.substring(0, 50));
      
      if (result && result.startsWith('data:image/')) {
        console.log('Updating profile with new avatar');
        const updatedProfile = { ...profile, avatar: result };
        setProfile(updatedProfile);
        localStorage.setItem('user', JSON.stringify(updatedProfile));
        
        console.log('Avatar saved to localStorage');
        toast({
          title: "Profile picture updated!",
          description: "Your profile picture has been uploaded successfully.",
        });
        setAvatarKey(prevKey => prevKey + 1);
        
        // Dispatch custom event to notify other components
        window.dispatchEvent(new CustomEvent('profileUpdated'));
      } else {
        console.log('Invalid base64 data received');
        toast({
          title: "Upload failed",
          description: "Invalid image data. Please try again.",
          variant: "destructive",
        });
      }
      setIsUploadingAvatar(false);
    };

    reader.onerror = (error) => {
      console.error('FileReader error:', error);
      toast({
        title: "Upload failed",
        description: "Failed to upload the image. Please try again.",
        variant: "destructive",
      });
      setIsUploadingAvatar(false);
    };

    console.log('Starting FileReader.readAsDataURL');
    reader.readAsDataURL(file);
  };

  // Handle re-entering chat session
  const handleContinueChat = (activity: Activity) => {
    // Store the chat topic in localStorage so the AI Teacher can resume the conversation
    localStorage.setItem('resumeChatTopic', activity.metadata?.topic || 'General Discussion');
    localStorage.setItem('resumeChatTimestamp', activity.timestamp);
    
    // Navigate to the AI Teacher page
    // Since we're in a component, we'll use a custom event to communicate with the parent
    const event = new CustomEvent('navigateToPage', { 
      detail: { page: 'chatbot' } 
    });
    window.dispatchEvent(event);
    
    toast({
      title: "Chat resumed!",
      description: `Continuing conversation about "${activity.metadata?.topic || 'General Discussion'}"`,
    });
  };

  // Handle retaking quiz
  const handleRetakeQuiz = (activity: Activity) => {
    // Store the quiz topic in localStorage so the Quiz Generator can use it
    localStorage.setItem('resumeQuizTopic', activity.metadata?.topic || 'General Quiz');
    localStorage.setItem('resumeQuizTimestamp', activity.timestamp);
    
    // Navigate to the Quiz Generator page
    const event = new CustomEvent('navigateToPage', { 
      detail: { page: 'quiz' } 
    });
    window.dispatchEvent(event);
    
    toast({
      title: "Quiz ready!",
      description: `Starting new quiz on "${activity.metadata?.topic || 'General Quiz'}"`,
    });
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold mb-2">Profile</h1>
        <p className="text-muted-foreground">Manage your account and track your learning progress</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Profile Overview */}
        <Card className="lg:col-span-1">
          <CardContent className="p-6">
            <div className="text-center">
              <div className="relative inline-block mb-4">
                <Avatar className="h-24 w-24" key={avatarKey}>
                  <AvatarImage 
                    src={profile.avatar || "/placeholder.svg"} 
                    alt={profile.name}
                    onLoad={() => console.log('Avatar image loaded successfully')}
                    onError={(e) => console.error('Avatar image failed to load:', e)}
                  />
                  <AvatarFallback className="text-lg">
                    {profile.name ? profile.name.split(' ').map(n => n[0]).join('') : 'U'}
                  </AvatarFallback>
                </Avatar>
                <Button 
                  size="icon" 
                  variant="outline" 
                  className="absolute -bottom-2 -right-2 h-8 w-8 rounded-full cursor-pointer"
                  disabled={isUploadingAvatar}
                  onClick={() => {
                    console.log('Camera button clicked');
                    document.getElementById('avatar-upload')?.click();
                  }}
                >
                  {isUploadingAvatar ? (
                    <div className="h-4 w-4 animate-spin rounded-full border-2 border-primary border-t-transparent" />
                  ) : (
                    <Camera className="h-4 w-4" />
                  )}
                </Button>
                <input
                  id="avatar-upload"
                  type="file"
                  accept="image/*"
                  onChange={handleAvatarUpload}
                  className="hidden"
                />
              </div>
              
              {/* Temporary debug info */}
              {profile.avatar && (
                <div className="text-xs text-muted-foreground mb-2">
                  Avatar loaded: {profile.avatar.substring(0, 30)}...
                </div>
              )}
              
              <h2 className="text-xl font-bold mb-1">{profile.name || 'User'}</h2>
              <p className="text-muted-foreground mb-4">Learner • Level {learningStats.level}</p>
              
              <div className="space-y-2 text-sm">
                <div className="flex items-center justify-center text-muted-foreground">
                  <Mail className="h-4 w-4 mr-2" />
                  {profile.email}
                </div>
                {profile.phone && (
                  <div className="flex items-center justify-center text-muted-foreground">
                    <Phone className="h-4 w-4 mr-2" />
                    {profile.phone}
                  </div>
                )}
                {profile.location && (
                  <div className="flex items-center justify-center text-muted-foreground">
                    <MapPin className="h-4 w-4 mr-2" />
                    {profile.location}
                  </div>
                )}
                <div className="flex items-center justify-center text-muted-foreground">
                  <Calendar className="h-4 w-4 mr-2" />
                  Joined {profile.joinDate || 'Recently'}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          <Tabs defaultValue="overview">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="skills">Skills</TabsTrigger>
              <TabsTrigger value="achievements">Achievements</TabsTrigger>
            </TabsList>

            <TabsContent value="overview" className="space-y-6">
              {/* Learning Stats */}
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle>Learning Statistics</CardTitle>
                      <CardDescription>Track your learning progress</CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {learningStatsData.map((stat, index) => (
                      <Card key={index}>
                        <CardContent className="p-4 text-center">
                          <stat.icon className="h-8 w-8 mx-auto mb-2 text-primary" />
                          <div className="text-2xl font-bold">{stat.value}</div>
                          <div className="text-xs text-muted-foreground">{stat.label}</div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Bio */}
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle>About</CardTitle>
                      <CardDescription>Tell others about yourself and your learning goals</CardDescription>
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setIsEditingBio(!isEditingBio)}
                    >
                      {isEditingBio ? <X className="h-4 w-4 mr-2" /> : <Edit className="h-4 w-4 mr-2" />}
                      {isEditingBio ? 'Cancel' : 'Edit'}
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  {isEditingBio ? (
                    <div className="space-y-4">
                      <Textarea
                        value={profile.bio}
                        onChange={(e) => setProfile({...profile, bio: e.target.value})}
                        placeholder="Tell us about yourself, your learning goals, and what you're passionate about..."
                        rows={4}
                        className="min-h-[100px]"
                      />
                      <div className="flex justify-end space-x-2">
                        <Button
                          variant="outline"
                          onClick={() => setIsEditingBio(false)}
                        >
                          Cancel
                        </Button>
                        <Button 
                          onClick={saveBio}
                          className="learning-gradient"
                        >
                          <Save className="h-4 w-4 mr-2" />
                          Save Bio
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <div>
                      {profile.bio ? (
                        <p className="text-muted-foreground whitespace-pre-wrap">{profile.bio}</p>
                      ) : (
                        <div className="text-center py-8">
                          <p className="text-muted-foreground mb-4">No bio added yet.</p>
                          <Button
                            variant="outline"
                            onClick={() => setIsEditingBio(true)}
                          >
                            <Edit className="h-4 w-4 mr-2" />
                            Add Bio
                          </Button>
                        </div>
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Recent Activity */}
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle>Recent Activity</CardTitle>
                      <CardDescription>Your latest learning activities and achievements</CardDescription>
                    </div>
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => {
                        // Add some sample activities for testing
                        trackQuizActivity('React Hooks', 8, 10);
                        trackChatActivity('JavaScript Promises');
                        trackTopicStudyActivity('Machine Learning Basics');
                        setActivities(getActivities()); // Refresh the activities list
                        toast({
                          title: "Sample activities added!",
                          description: "Check the recent activity section to see the new entries.",
                        });
                      }}
                    >
                      Add Sample Activities
                    </Button>
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => {
                        // Manually check and update streak
                        const currentStreak = checkAndUpdateStreak();
                        const learningStats = getLearningStats();
                        console.log('Manual streak check:', {
                          currentStreak,
                          lastActivityDate: learningStats.lastActivityDate,
                          today: new Date().toDateString()
                        });
                        setLearningStats(getLearningStats()); // Refresh stats
                        toast({
                          title: "Streak Checked!",
                          description: `Current streak: ${currentStreak} days. Check console for details.`,
                        });
                      }}
                    >
                      Check Streak
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {activities.length > 0 ? (
                      activities.slice(0, 10).map((activity) => (
                        <div key={activity.id} className="flex items-center space-x-3 p-4 rounded-lg bg-muted/50 hover:bg-muted/70 transition-colors border border-border/50">
                          <div className={`p-2 rounded-full ${getActivityColor(activity.type)}`}>
                            {getActivityIcon(activity.type)}
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="font-medium text-sm">{activity.title}</p>
                            <p className="text-xs text-muted-foreground truncate">{activity.description}</p>
                            {activity.metadata?.score !== undefined && (
                              <Badge variant="secondary" className="mt-1 text-xs">
                                Score: {activity.metadata.score}/{activity.metadata.totalQuestions}
                              </Badge>
                            )}
                          </div>
                          <div className="flex items-center space-x-3">
                            <div className="text-xs text-muted-foreground whitespace-nowrap">
                              {formatTimestamp(activity.timestamp)}
                            </div>
                            {activity.type === 'chat' && (
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => handleContinueChat(activity)}
                                className="text-xs px-3 py-1 h-7 bg-blue-50 hover:bg-blue-100 border-blue-200 text-blue-700"
                              >
                                <MessageSquare className="h-3 w-3 mr-1" />
                                Continue
                              </Button>
                            )}
                            {activity.type === 'quiz' && (
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => handleRetakeQuiz(activity)}
                                className="text-xs px-3 py-1 h-7 bg-green-50 hover:bg-green-100 border-green-200 text-green-700"
                              >
                                <BookOpen className="h-3 w-3 mr-1" />
                                Retake
                              </Button>
                            )}
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="text-center py-8">
                        <Clock className="h-12 w-12 mx-auto mb-4 text-muted-foreground opacity-50" />
                        <p className="text-muted-foreground mb-4">No recent activity yet.</p>
                        <p className="text-sm text-muted-foreground">Start using the platform to see your activities here!</p>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="skills" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Skill Progress</CardTitle>
                  <CardDescription>Your expertise across different technologies</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {skills.map((skill, index) => (
                      <div key={index}>
                        <div className="flex justify-between text-sm mb-1">
                          <span className="font-medium">{skill.name}</span>
                          <div className="flex items-center space-x-2">
                            <span>{skill.level}%</span>
                            <div className="flex space-x-1">
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => updateSkillLevel(skill.name, skill.level - 5)}
                                disabled={skill.level <= 0}
                              >
                                <Minus className="h-3 w-3" />
                              </Button>
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => updateSkillLevel(skill.name, skill.level + 5)}
                                disabled={skill.level >= 100}
                              >
                                <Plus className="h-3 w-3" />
                              </Button>
                            </div>
                          </div>
                        </div>
                        <div className="w-full bg-muted rounded-full h-2">
                          <div 
                            className={`${skill.color} h-2 rounded-full transition-all duration-300`}
                            style={{ width: `${skill.level}%` }}
                          ></div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Skill Recommendations</CardTitle>
                  <CardDescription>Based on your current progress</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {['Next.js', 'GraphQL', 'Docker', 'AWS'].map((skill, index) => (
                      <div key={index} className="flex items-center justify-between p-3 rounded-lg border">
                        <span className="font-medium">{skill}</span>
                        <Button size="sm" variant="outline">Learn</Button>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="achievements" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Achievements</CardTitle>
                  <CardDescription>Your learning milestones and badges</CardDescription>
                </CardHeader>
                <CardContent>
                  {achievements.length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {achievements.map((achievement) => (
                        <div key={achievement.id} className="flex items-center space-x-4 p-4 rounded-lg border">
                          <div className="text-2xl">{achievement.icon}</div>
                          <div className="flex-1">
                            <h3 className="font-semibold">{achievement.title}</h3>
                            <p className="text-sm text-muted-foreground">{achievement.description}</p>
                            <p className="text-xs text-muted-foreground">{achievement.date}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <p className="text-muted-foreground mb-4">No achievements yet. Start learning to earn badges!</p>
                      <Button 
                        onClick={() => addAchievement('First Step', 'Started your learning journey', '🎯')}
                        className="learning-gradient"
                      >
                        Add Sample Achievement
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
};

export default Profile;
