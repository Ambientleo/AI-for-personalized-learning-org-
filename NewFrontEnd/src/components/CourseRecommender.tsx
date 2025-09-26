import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Star, Clock, User, Search, Filter, ExternalLink, Loader2, Sparkles, BookOpen } from 'lucide-react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useToast } from '@/hooks/use-toast';

interface Course {
  id?: number;
  title: string;
  description?: string;
  instructor?: string;
  rating?: number;
  students?: number;
  duration?: string;
  level: string;
  category?: string;
  price?: string;
  image?: string;
  tags?: string[];
  topics?: string[];
  source: 'internal' | 'external';
  url?: string;
}

const CourseRecommender = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [category, setCategory] = useState('all');
  const [level, setLevel] = useState('all');
  const [interests, setInterests] = useState('');
  const [courses, setCourses] = useState<Course[]>([]);
  const [recommendations, setRecommendations] = useState<Course[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingRecommendations, setIsLoadingRecommendations] = useState(false);
  const [availableTopics, setAvailableTopics] = useState<string[]>([]);
  const { toast } = useToast();

  const API_BASE_URL = 'http://localhost:5001';

  // Fetch available topics on component mount
  useEffect(() => {
    fetchAvailableTopics();
  }, []);

  const fetchAvailableTopics = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/topics`);
      const data = await response.json();
      if (data.success) {
        setAvailableTopics(data.topics);
      }
    } catch (error) {
      console.error('Error fetching topics:', error);
    }
  };

  const searchCourses = async () => {
    if (!searchTerm.trim()) return;

    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/search?q=${encodeURIComponent(searchTerm)}`);
      const data = await response.json();
      
      if (data.success) {
        setCourses(data.results);
        toast({
          title: "Search completed!",
          description: `Found ${data.count} courses for "${searchTerm}"`,
        });
      } else {
        toast({
          title: "Search failed",
          description: data.error || "Failed to search courses",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Error searching courses:', error);
      toast({
        title: "Search failed",
        description: "Failed to connect to the course recommender service",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const getRecommendations = async () => {
    if (!interests.trim()) {
      toast({
        title: "No interests provided",
        description: "Please enter your learning interests to get recommendations",
        variant: "destructive",
      });
      return;
    }

    setIsLoadingRecommendations(true);
    try {
      const interestsList = interests.split(',').map(interest => interest.trim()).filter(interest => interest);
      
      const response = await fetch(`${API_BASE_URL}/api/recommend`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ interests: interestsList }),
      });
      
      const data = await response.json();
      
      if (data.success) {
        setRecommendations(data.recommendations);
        toast({
          title: "Recommendations ready!",
          description: `Found ${data.count} personalized course recommendations`,
        });
      } else {
        toast({
          title: "Recommendation failed",
          description: data.error || "Failed to get recommendations",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Error getting recommendations:', error);
      toast({
        title: "Recommendation failed",
        description: "Failed to connect to the course recommender service",
        variant: "destructive",
      });
    } finally {
      setIsLoadingRecommendations(false);
    }
  };

  const filteredCourses = courses.filter(course => {
    const matchesSearch = course.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         (course.tags && course.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase())));
    const matchesCategory = category === 'all' || course.category === category;
    const matchesLevel = level === 'all' || course.level === level;
    
    return matchesSearch && matchesCategory && matchesLevel;
  });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    searchCourses();
  };

  const handleGetRecommendations = (e: React.FormEvent) => {
    e.preventDefault();
    getRecommendations();
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-3xl font-bold mb-2">Course Recommender</h1>
        <p className="text-muted-foreground">Discover personalized courses tailored to your learning goals</p>
      </div>

      {/* Interest-Based Recommendations */}
      <Card className="learning-gradient-soft">
        <CardHeader>
          <CardTitle className="flex items-center">
            <Sparkles className="h-5 w-5 mr-2 text-primary" />
            AI-Powered Course Recommendations
          </CardTitle>
          <CardDescription>Tell us what you want to learn and get personalized recommendations</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleGetRecommendations} className="space-y-4">
            <div>
              <Label htmlFor="interests">What would you like to learn?</Label>
              <Textarea
                id="interests"
                placeholder="Enter your interests (e.g., Python, React, Machine Learning, Web Development)..."
                value={interests}
                onChange={(e) => setInterests(e.target.value)}
                className="mt-1"
                rows={3}
              />
              <p className="text-sm text-muted-foreground mt-1">
                Available topics: {availableTopics.join(', ')}
              </p>
            </div>
            <Button 
              type="submit" 
              className="learning-gradient"
              disabled={isLoadingRecommendations || !interests.trim()}
            >
              {isLoadingRecommendations ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Getting Recommendations...
                </>
              ) : (
                <>
                  <Sparkles className="h-4 w-4 mr-2" />
                  Get Personalized Recommendations
                </>
              )}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* AI Recommendations Results */}
      {recommendations.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <BookOpen className="h-5 w-5 mr-2 text-primary" />
              Recommended Courses for You
            </CardTitle>
            <CardDescription>Based on your interests: {interests}</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {recommendations.map((course, index) => (
                <Card key={index} className="overflow-hidden hover:shadow-lg transition-shadow">
                  <CardContent className="p-4">
                    <div className="flex justify-between items-start mb-2">
                      <Badge variant={course.source === 'internal' ? 'secondary' : 'outline'}>
                        {course.source}
                      </Badge>
                      <Badge variant="outline">{course.level}</Badge>
                    </div>
                    
                    <h3 className="font-semibold text-lg mb-2 line-clamp-2">{course.title}</h3>
                    {course.description && (
                      <p className="text-muted-foreground text-sm mb-3 line-clamp-2">{course.description}</p>
                    )}
                    
                    {course.topics && (
                      <div className="flex flex-wrap gap-1 mb-4">
                        {course.topics.map((topic, idx) => (
                          <Badge key={idx} variant="secondary" className="text-xs">
                            {topic}
                          </Badge>
                        ))}
                      </div>
                    )}
                    
                    <div className="flex justify-between items-center">
                      {course.url ? (
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => window.open(course.url, '_blank')}
                        >
                          <ExternalLink className="h-4 w-4 mr-1" />
                          View Course
                        </Button>
                      ) : (
                        <Button variant="outline" size="sm" disabled>
                          Internal Course
                        </Button>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Search and Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Search Courses</CardTitle>
          <CardDescription>Find specific courses by topic or skill</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSearch} className="space-y-4">
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search courses, skills, or topics..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
              <Select value={category} onValueChange={setCategory}>
                <SelectTrigger className="w-full md:w-[180px]">
                  <SelectValue placeholder="Category" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Categories</SelectItem>
                  <SelectItem value="Web Development">Web Development</SelectItem>
                  <SelectItem value="AI/ML">AI/ML</SelectItem>
                  <SelectItem value="Programming">Programming</SelectItem>
                  <SelectItem value="Design">Design</SelectItem>
                </SelectContent>
              </Select>
              <Select value={level} onValueChange={setLevel}>
                <SelectTrigger className="w-full md:w-[140px]">
                  <SelectValue placeholder="Level" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Levels</SelectItem>
                  <SelectItem value="Beginner">Beginner</SelectItem>
                  <SelectItem value="Intermediate">Intermediate</SelectItem>
                  <SelectItem value="Advanced">Advanced</SelectItem>
                </SelectContent>
              </Select>
              <Button 
                type="submit" 
                variant="outline"
                disabled={isLoading || !searchTerm.trim()}
              >
                {isLoading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Searching...
                  </>
                ) : (
                  <>
                    <Search className="h-4 w-4 mr-2" />
                    Search
                  </>
                )}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      {/* Course Grid */}
      {filteredCourses.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6">
          {filteredCourses.map((course, index) => (
            <Card key={index} className="overflow-hidden hover:shadow-lg transition-shadow">
              <div className="aspect-video bg-gradient-to-br from-blue-100 to-purple-100 flex items-center justify-center">
                <div className="text-4xl">📚</div>
              </div>
              <CardContent className="p-6">
                <div className="flex justify-between items-start mb-2">
                  <Badge variant={course.source === 'internal' ? 'secondary' : 'outline'}>
                    {course.source}
                  </Badge>
                  <Badge variant="outline">{course.level}</Badge>
                </div>
                
                <h3 className="font-semibold text-lg mb-2 line-clamp-2">{course.title}</h3>
                {course.description && (
                  <p className="text-muted-foreground text-sm mb-3 line-clamp-2">{course.description}</p>
                )}
                
                {course.tags && (
                  <div className="flex flex-wrap gap-1 mb-4">
                    {course.tags.map((tag, idx) => (
                      <Badge key={idx} variant="secondary" className="text-xs">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                )}
                
                <div className="flex justify-between items-center">
                  {course.url ? (
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => window.open(course.url, '_blank')}
                    >
                      <ExternalLink className="h-4 w-4 mr-1" />
                      View Course
                    </Button>
                  ) : (
                    <Button variant="outline" size="sm" disabled>
                      Internal Course
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* No Results */}
      {searchTerm && filteredCourses.length === 0 && !isLoading && (
        <Card>
          <CardContent className="p-8 text-center">
            <div className="text-4xl mb-4">🔍</div>
            <h3 className="text-lg font-semibold mb-2">No courses found</h3>
            <p className="text-muted-foreground">
              Try adjusting your search terms or filters to find more courses.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default CourseRecommender;
