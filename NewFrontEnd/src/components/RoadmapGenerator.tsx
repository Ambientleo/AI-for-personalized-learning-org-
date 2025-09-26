import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { CheckCircle, Circle, Clock, Star, Target, Loader2, Sparkles, BookOpen, ArrowRight, Download, Share2 } from 'lucide-react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useToast } from '@/hooks/use-toast';
import { trackCourseActivity, updateStreak } from '@/utils/activityTracker';

interface RoadmapStep {
  level: number;
  title: string;
  description: string;
  topics: string[];
  resources: string[];
}

interface Roadmap {
  title: string;
  description: string;
  steps: RoadmapStep[];
  estimated_time: string;
  prerequisites: string[];
  learning_tips?: string[];
}

interface Template {
  id: string;
  title: string;
  description: string;
  topics: string[];
  estimated_time: string;
}

const RoadmapGenerator = () => {
  const [goal, setGoal] = useState('');
  const [experience, setExperience] = useState('');
  const [timeCommitment, setTimeCommitment] = useState('');
  const [showRoadmap, setShowRoadmap] = useState(false);
  const [completedSteps, setCompletedSteps] = useState<number[]>([]);
  const [roadmap, setRoadmap] = useState<Roadmap | null>(null);
  const [templates, setTemplates] = useState<Template[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingTemplates, setIsLoadingTemplates] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<string>('');
  const { toast } = useToast();

  const API_BASE_URL = 'http://localhost:5002';

  // Fetch templates on component mount
  useEffect(() => {
    fetchTemplates();
  }, []);

  const fetchTemplates = async () => {
    setIsLoadingTemplates(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/templates`);
      const data = await response.json();
      
      if (data.success) {
        setTemplates(data.templates);
      } else {
        toast({
          title: "Failed to load templates",
          description: data.error || "Could not load roadmap templates",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Error fetching templates:', error);
      toast({
        title: "Connection error",
        description: "Failed to connect to the roadmap generator service",
        variant: "destructive",
      });
    } finally {
      setIsLoadingTemplates(false);
    }
  };

  const generateRoadmap = async () => {
    if (!goal.trim()) {
      toast({
        title: "No goal specified",
        description: "Please enter what you want to learn",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ topic: goal }),
      });
      
      const data = await response.json();
      
      if (data.success) {
        setRoadmap(data.roadmap);
        setShowRoadmap(true);
        setCompletedSteps([]);
        
        // Reset completion tracking for new roadmap
        resetCompletionTracking();
        
        toast({
          title: "Roadmap generated!",
          description: `Your personalized ${goal} roadmap is ready`,
        });
      } else {
        toast({
          title: "Generation failed",
          description: data.error || "Failed to generate roadmap",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Error generating roadmap:', error);
      toast({
        title: "Generation failed",
        description: "Failed to connect to the roadmap generator service",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const loadTemplate = async (templateId: string) => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/template/${templateId}`);
      const data = await response.json();
      
      if (data.success) {
        setRoadmap(data.template);
        setGoal(data.template.title);
        setShowRoadmap(true);
        setCompletedSteps([]);
        setSelectedTemplate(templateId);
        
        // Reset completion tracking for new roadmap
        resetCompletionTracking();
        
        toast({
          title: "Template loaded!",
          description: `${data.template.title} roadmap is ready`,
        });
      } else {
        toast({
          title: "Template loading failed",
          description: data.error || "Failed to load template",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Error loading template:', error);
      toast({
        title: "Template loading failed",
        description: "Failed to connect to the roadmap generator service",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Reset completion tracking for new roadmaps
  const resetCompletionTracking = () => {
    try {
      const learningStats = JSON.parse(localStorage.getItem('learningStats') || '{}');
      learningStats.lastRoadmapProgress = 0;
      learningStats.lastCompletedSteps = 0;
      localStorage.setItem('learningStats', JSON.stringify(learningStats));
    } catch (error) {
      console.error('Failed to reset completion tracking:', error);
    }
  };

  const toggleStepCompletion = (stepIndex: number) => {
    const newCompletedSteps = completedSteps.includes(stepIndex) 
      ? completedSteps.filter(id => id !== stepIndex)
      : [...completedSteps, stepIndex];
    
    setCompletedSteps(newCompletedSteps);
    
    // Save completed steps to localStorage
    if (roadmap) {
      const roadmapKey = `roadmap_${roadmap.title.replace(/\s+/g, '_').toLowerCase()}`;
      localStorage.setItem(roadmapKey, JSON.stringify(newCompletedSteps));
      
      // Update learning stats when steps are completed
      updateLearningStats(newCompletedSteps.length, roadmap.steps.length);
    }
  };

  // Update learning stats when roadmap progress changes
  const updateLearningStats = (completedCount: number, totalCount: number) => {
    try {
      const learningStats = JSON.parse(localStorage.getItem('learningStats') || '{}');
      
      // Calculate progress percentage
      const progressPercentage = totalCount > 0 ? (completedCount / totalCount) * 100 : 0;
      
      // Check if this is a new completion (either reaching 100% or marking all complete)
      const wasPreviouslyComplete = learningStats.lastRoadmapProgress === 100;
      const isNowComplete = progressPercentage === 100;
      const isNewCompletion = isNowComplete && !wasPreviouslyComplete;
      
      // If roadmap is newly completed, increment courses completed
      if (isNewCompletion) {
        learningStats.coursesCompleted = (learningStats.coursesCompleted || 0) + 1;
        
        // Track course completion activity
        if (roadmap) {
          trackCourseActivity(roadmap.title);
          
          // Update streak for completing a course
          updateStreak();
          
          // Show completion toast
          toast({
            title: "🎉 Course Completed!",
            description: `Congratulations! You've completed the "${roadmap.title}" roadmap!`,
          });
        }
      }
      
      // Update study hours (estimate 1 hour per completed step)
      const previousCompletedSteps = learningStats.lastCompletedSteps || 0;
      const newCompletedSteps = completedCount - previousCompletedSteps;
      if (newCompletedSteps > 0) {
        learningStats.studyHours = (learningStats.studyHours || 0) + newCompletedSteps;
      }
      
      // Store current progress for comparison
      learningStats.lastCompletedSteps = completedCount;
      learningStats.lastRoadmapProgress = progressPercentage;
      
      localStorage.setItem('learningStats', JSON.stringify(learningStats));
      
      // Dispatch custom event to notify other components
      window.dispatchEvent(new CustomEvent('statsUpdated'));
      
      console.log('Learning stats updated:', {
        completedCount,
        totalCount,
        progressPercentage,
        isNewCompletion,
        coursesCompleted: learningStats.coursesCompleted
      });
    } catch (error) {
      console.error('Failed to update learning stats:', error);
    }
  };

  // Load completed steps from localStorage
  const loadCompletedSteps = () => {
    if (roadmap) {
      const roadmapKey = `roadmap_${roadmap.title.replace(/\s+/g, '_').toLowerCase()}`;
      const savedSteps = localStorage.getItem(roadmapKey);
      if (savedSteps) {
        try {
          const parsedSteps = JSON.parse(savedSteps);
          setCompletedSteps(parsedSteps);
          
          // Update learning stats when loading completed steps
          updateLearningStats(parsedSteps.length, roadmap.steps.length);
        } catch (error) {
          console.error('Failed to load completed steps:', error);
          setCompletedSteps([]);
        }
      }
    }
  };

  // Load completed steps when roadmap changes
  useEffect(() => {
    if (roadmap) {
      loadCompletedSteps();
    }
  }, [roadmap]);

  const downloadRoadmap = () => {
    if (!roadmap) return;
    
    const roadmapText = `
${roadmap.title}
${'='.repeat(roadmap.title.length)}

${roadmap.description}

Estimated Time: ${roadmap.estimated_time}

Prerequisites:
${roadmap.prerequisites.map(p => `• ${p}`).join('\n')}

Learning Path:
${roadmap.steps.map((step, index) => `
Step ${index + 1}: ${step.title}
Level: ${step.level}
Description: ${step.description}

Topics:
${step.topics.map(t => `• ${t}`).join('\n')}

Resources:
${step.resources.map(r => `• ${r}`).join('\n')}
`).join('\n')}
    `;
    
    const blob = new Blob([roadmapText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${roadmap.title.replace(/\s+/g, '_')}_roadmap.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    toast({
      title: "Roadmap downloaded!",
      description: "Your roadmap has been saved to your device",
    });
  };

  const shareRoadmap = () => {
    if (!roadmap) return;
    
    const shareText = `Check out my ${roadmap.title} learning roadmap! Generated with LearnAI.`;
    
    if (navigator.share) {
      navigator.share({
        title: roadmap.title,
        text: shareText,
        url: window.location.href,
      });
    } else {
      navigator.clipboard.writeText(shareText);
      toast({
        title: "Roadmap shared!",
        description: "Roadmap information copied to clipboard",
      });
    }
  };

  const totalSteps = roadmap?.steps.length || 0;
  const progressPercentage = totalSteps > 0 ? (completedSteps.length / totalSteps) * 100 : 0;

  if (!showRoadmap) {
    return (
      <div className="space-y-6 animate-fade-in">
        <div>
          <h1 className="text-3xl font-bold mb-2">Roadmap Generator</h1>
          <p className="text-muted-foreground">Create a personalized learning path to achieve your goals</p>
        </div>

        {/* Custom Roadmap Generation */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Sparkles className="h-5 w-5 mr-2 text-primary" />
              AI-Powered Roadmap Generation
            </CardTitle>
            <CardDescription>Tell us what you want to learn and get a personalized roadmap</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div>
              <Label htmlFor="goal">What do you want to learn?</Label>
              <Textarea
                id="goal"
                placeholder="e.g., Full Stack Web Development, Data Science, Mobile App Development, Machine Learning..."
                value={goal}
                onChange={(e) => setGoal(e.target.value)}
                className="mt-1"
                rows={3}
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="experience">Experience Level</Label>
                <Select value={experience} onValueChange={setExperience}>
                  <SelectTrigger className="mt-1">
                    <SelectValue placeholder="Select your level" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="beginner">Complete Beginner</SelectItem>
                    <SelectItem value="some">Some Experience</SelectItem>
                    <SelectItem value="intermediate">Intermediate</SelectItem>
                    <SelectItem value="advanced">Advanced</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="timeCommitment">Time Commitment</Label>
                <Select value={timeCommitment} onValueChange={setTimeCommitment}>
                  <SelectTrigger className="mt-1">
                    <SelectValue placeholder="How much time per week?" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="5-10">5-10 hours/week</SelectItem>
                    <SelectItem value="10-20">10-20 hours/week</SelectItem>
                    <SelectItem value="20-30">20-30 hours/week</SelectItem>
                    <SelectItem value="30+">30+ hours/week</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <Button 
              onClick={generateRoadmap} 
              className="w-full learning-gradient"
              disabled={isLoading || !goal.trim()}
            >
              {isLoading ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Generating Roadmap...
                </>
              ) : (
                <>
                  <Target className="h-4 w-4 mr-2" />
                  Generate My Roadmap
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Popular Templates */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <BookOpen className="h-5 w-5 mr-2 text-primary" />
              Popular Roadmap Templates
            </CardTitle>
            <CardDescription>Choose from our curated learning paths</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoadingTemplates ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="h-6 w-6 animate-spin mr-2" />
                Loading templates...
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {templates.map((template) => (
                  <Card 
                    key={template.id} 
                    className="cursor-pointer hover:shadow-md transition-shadow"
                    onClick={() => loadTemplate(template.id)}
                  >
                    <CardContent className="p-4">
                      <h3 className="font-semibold mb-2">{template.title}</h3>
                      <p className="text-sm text-muted-foreground mb-3 line-clamp-2">
                        {template.description}
                      </p>
                      <div className="flex items-center justify-between text-sm text-muted-foreground mb-3">
                        <span className="flex items-center">
                          <Clock className="h-3 w-3 mr-1" />
                          {template.estimated_time}
                        </span>
                      </div>
                      <div className="flex flex-wrap gap-1 mb-3">
                        {template.topics.slice(0, 3).map((topic, index) => (
                          <Badge key={index} variant="secondary" className="text-xs">
                            {topic}
                          </Badge>
                        ))}
                        {template.topics.length > 3 && (
                          <Badge variant="outline" className="text-xs">
                            +{template.topics.length - 3} more
                          </Badge>
                        )}
                      </div>
                      <Button size="sm" variant="outline" className="w-full">
                        <ArrowRight className="h-3 w-3 mr-1" />
                        Use This Template
                      </Button>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!roadmap) {
    return (
      <div className="space-y-6 animate-fade-in">
        <div className="text-center py-8">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
          <h3 className="text-lg font-semibold mb-2">Loading Roadmap...</h3>
          <p className="text-muted-foreground">Please wait while we generate your personalized learning path</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold mb-2">{roadmap.title}</h1>
          <p className="text-muted-foreground">{roadmap.description}</p>
        </div>
        <div className="flex space-x-2">
          <Button variant="outline" size="sm" onClick={downloadRoadmap}>
            <Download className="h-4 w-4 mr-1" />
            Download
          </Button>
          <Button variant="outline" size="sm" onClick={shareRoadmap}>
            <Share2 className="h-4 w-4 mr-1" />
            Share
          </Button>
        </div>
      </div>

      {/* Roadmap Overview */}
      <Card>
        <CardContent className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-primary">{roadmap.steps.length}</div>
              <div className="text-sm text-muted-foreground">Learning Steps</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-primary">{roadmap.estimated_time}</div>
              <div className="text-sm text-muted-foreground">Estimated Time</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-primary">{Math.round(progressPercentage)}%</div>
              <div className="text-sm text-muted-foreground">Progress</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Prerequisites */}
      {roadmap.prerequisites && roadmap.prerequisites.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Prerequisites</CardTitle>
            <CardDescription>What you should know before starting</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {roadmap.prerequisites.map((prereq, index) => (
                <Badge key={index} variant="secondary">
                  {prereq}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Learning Tips */}
      {roadmap.learning_tips && roadmap.learning_tips.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Sparkles className="h-5 w-5 mr-2 text-primary" />
              Learning Tips
            </CardTitle>
            <CardDescription>Pro tips to help you succeed in your learning journey</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {roadmap.learning_tips.map((tip, index) => (
                <div key={index} className="flex items-start space-x-3">
                  <div className="flex items-center justify-center w-6 h-6 rounded-full bg-primary/10 text-primary text-xs font-bold mt-0.5">
                    {index + 1}
                  </div>
                  <p className="text-sm text-muted-foreground leading-relaxed">{tip}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Progress Bar */}
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium">Your Progress</span>
            <span className="text-sm text-muted-foreground">
              {completedSteps.length} of {totalSteps} steps completed
            </span>
          </div>
          <Progress value={progressPercentage} className="h-2" />
        </CardContent>
      </Card>

      {/* Learning Steps */}
      <div className="space-y-6">
        {roadmap.steps.map((step, index) => (
          <Card key={index} className="overflow-hidden">
            <CardHeader className="pb-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary text-primary-foreground text-sm font-bold">
                    {index + 1}
                  </div>
                  <div>
                    <CardTitle className="text-lg">{step.title}</CardTitle>
                    <CardDescription>Level {step.level} • {step.description}</CardDescription>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => toggleStepCompletion(index)}
                >
                  {completedSteps.includes(index) ? (
                    <CheckCircle className="h-5 w-5 text-green-500" />
                  ) : (
                    <Circle className="h-5 w-5 text-muted-foreground" />
                  )}
                </Button>
              </div>
            </CardHeader>
            <CardContent className="pt-0">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-semibold mb-2">Topics to Learn</h4>
                  <div className="flex flex-wrap gap-2">
                    {step.topics.map((topic, topicIndex) => (
                      <Badge key={topicIndex} variant="outline">
                        {topic}
                      </Badge>
                    ))}
                  </div>
                </div>
                <div>
                  <h4 className="font-semibold mb-2">Recommended Resources</h4>
                  <ul className="space-y-1">
                    {step.resources.map((resource, resourceIndex) => (
                      <li key={resourceIndex} className="text-sm text-muted-foreground">
                        • {resource}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Action Buttons */}
      <div className="flex justify-center space-x-4">
        <Button 
          variant="outline" 
          onClick={() => setShowRoadmap(false)}
        >
          Generate New Roadmap
        </Button>
        <Button 
          className="learning-gradient"
          onClick={() => {
            const allSteps = roadmap.steps.map((_, index) => index);
            setCompletedSteps(allSteps);
            
            // Save to localStorage
            if (roadmap) {
              const roadmapKey = `roadmap_${roadmap.title.replace(/\s+/g, '_').toLowerCase()}`;
              localStorage.setItem(roadmapKey, JSON.stringify(allSteps));
              
              // Force completion by resetting tracking first
              try {
                const learningStats = JSON.parse(localStorage.getItem('learningStats') || '{}');
                learningStats.lastRoadmapProgress = 0; // Reset to ensure completion is detected
                learningStats.lastCompletedSteps = 0;
                localStorage.setItem('learningStats', JSON.stringify(learningStats));
              } catch (error) {
                console.error('Failed to reset tracking:', error);
              }
              
              // Update learning stats (this should now detect completion)
              updateLearningStats(allSteps.length, roadmap.steps.length);
            }
          }}
        >
          Mark All Complete
        </Button>
      </div>
    </div>
  );
};

export default RoadmapGenerator;
