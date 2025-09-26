export interface Activity {
  id: string;
  type: 'quiz' | 'course' | 'chat' | 'file_upload' | 'topic_study' | 'achievement' | 'skill_update';
  title: string;
  description: string;
  timestamp: string;
  icon: string;
  metadata?: {
    score?: number;
    topic?: string;
    duration?: number;
    fileName?: string;
    skillName?: string;
    level?: number;
    totalQuestions?: number;
  };
}

// Get activities from localStorage
export const getActivities = (): Activity[] => {
  const activitiesStr = localStorage.getItem('userActivities');
  if (activitiesStr) {
    try {
      return JSON.parse(activitiesStr);
    } catch (e) {
      return [];
    }
  }
  return [];
};

// Add activity function
export const addActivity = (activity: Omit<Activity, 'id' | 'timestamp'>) => {
  const newActivity: Activity = {
    ...activity,
    id: Date.now().toString(),
    timestamp: new Date().toISOString()
  };
  
  const currentActivities = getActivities();
  const updatedActivities = [newActivity, ...currentActivities].slice(0, 50); // Keep only last 50 activities
  
  localStorage.setItem('userActivities', JSON.stringify(updatedActivities));
  
  // Update streak for any learning activity
  updateStreak();
  
  return newActivity;
};

// Update streak based on daily activity
export const updateStreak = () => {
  try {
    const learningStats = JSON.parse(localStorage.getItem('learningStats') || '{}');
    const today = new Date().toDateString();
    const lastActivityDate = learningStats.lastActivityDate;
    
    console.log('Checking streak:', {
      today,
      lastActivityDate,
      currentStreak: learningStats.currentStreak
    });
    
    // If this is the first activity of the day
    if (lastActivityDate !== today) {
      const yesterday = new Date();
      yesterday.setDate(yesterday.getDate() - 1);
      const yesterdayString = yesterday.toDateString();
      
      // If last activity was yesterday, increment streak
      if (lastActivityDate === yesterdayString) {
        learningStats.currentStreak = (learningStats.currentStreak || 0) + 1;
        console.log('Streak incremented to:', learningStats.currentStreak);
      } 
      // If last activity was more than 1 day ago, reset streak to 1
      else if (lastActivityDate && lastActivityDate !== yesterdayString) {
        learningStats.currentStreak = 1;
        console.log('Streak reset to 1 (missed a day)');
      } 
      // If this is the first activity ever, start streak at 1
      else if (!lastActivityDate) {
        learningStats.currentStreak = 1;
        console.log('First activity - streak started at 1');
      }
      
      // Update last activity date
      learningStats.lastActivityDate = today;
      localStorage.setItem('learningStats', JSON.stringify(learningStats));
      
      console.log('Streak updated:', {
        currentStreak: learningStats.currentStreak,
        lastActivityDate: learningStats.lastActivityDate
      });
    } else {
      console.log('Activity on same day - streak unchanged');
    }
  } catch (error) {
    console.error('Failed to update streak:', error);
  }
};

// Manual function to check and update streak (can be called from any component)
export const checkAndUpdateStreak = () => {
  try {
    const learningStats = JSON.parse(localStorage.getItem('learningStats') || '{}');
    const today = new Date().toDateString();
    const lastActivityDate = learningStats.lastActivityDate;
    
    // If no activity today, don't update streak
    if (lastActivityDate !== today) {
      updateStreak();
    }
    
    return learningStats.currentStreak || 0;
  } catch (error) {
    console.error('Failed to check streak:', error);
    return 0;
  }
};

// Activity tracking functions for different actions
export const trackQuizActivity = (topic: string, score?: number, totalQuestions?: number) => {
  const scoreText = score !== undefined && totalQuestions !== undefined 
    ? ` (${score}/${totalQuestions} correct)`
    : '';
  
  addActivity({
    type: 'quiz',
    title: `Completed Quiz`,
    description: `Took a quiz on "${topic}"${scoreText}`,
    icon: '📝',
    metadata: {
      score,
      topic,
      totalQuestions
    }
  });
};

export const trackCourseActivity = (courseName: string, duration?: number) => {
  const durationText = duration ? ` (${duration} minutes)` : '';
  
  addActivity({
    type: 'course',
    title: `Completed Course`,
    description: `Finished "${courseName}"${durationText}`,
    icon: '🎓',
    metadata: {
      duration
    }
  });
};

export const trackChatActivity = (topic: string) => {
  addActivity({
    type: 'chat',
    title: `AI Chat Session`,
    description: `Had a conversation with AI about "${topic}"`,
    icon: '💬',
    metadata: {
      topic
    }
  });
};

export const trackFileUploadActivity = (fileName: string, fileType: string) => {
  addActivity({
    type: 'file_upload',
    title: `Uploaded File`,
    description: `Uploaded ${fileType} file: "${fileName}"`,
    icon: '📁',
    metadata: {
      fileName
    }
  });
};

export const trackTopicStudyActivity = (topic: string) => {
  addActivity({
    type: 'topic_study',
    title: `Studied Topic`,
    description: `Learned about "${topic}"`,
    icon: '📚',
    metadata: {
      topic
    }
  });
};

export const trackSkillUpdateActivity = (skillName: string, newLevel: number) => {
  addActivity({
    type: 'skill_update',
    title: `Skill Improved`,
    description: `Improved ${skillName} to level ${newLevel}%`,
    icon: '⚡',
    metadata: {
      skillName,
      level: newLevel
    }
  });
};

export const trackAchievementActivity = (title: string) => {
  addActivity({
    type: 'achievement',
    title: `Achievement Unlocked`,
    description: `Earned: ${title}`,
    icon: '🏆'
  });
}; 