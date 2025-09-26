import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  History, 
  BookOpen, 
  MessageSquare, 
  TrendingUp, 
  Calendar, 
  Target, 
  Award,
  Trash2,
  RefreshCw,
  Eye,
  Clock
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

interface UserStats {
  total_quizzes: number;
  total_chats: number;
  total_topics: number;
  average_score: number;
  top_topics: Array<{
    id: string;
    topic: string;
    count: number;
    first_used: string;
    last_used: string;
    source_types: string[];
  }>;
  recent_quizzes: Array<{
    id: string;
    timestamp: string;
    topic: string;
    source_type: string;
    score_percentage: number;
    total_questions: number;
  }>;
  recent_chats: Array<{
    id: string;
    timestamp: string;
    message: string;
    response: string;
    topic: string;
    type: string;
  }>;
  created_at: string;
  last_activity: string;
}

interface QuizHistory {
  id: string;
  timestamp: string;
  topic: string;
  source_type: string;
  num_questions: number;
  score: number;
  total_questions: number;
  score_percentage: number;
  ollama_used: boolean;
  questions: any[];
  results: any[];
  input_content: string;
  filename: string;
  url: string;
}

interface TopicHistory {
  id: string;
  topic: string;
  count: number;
  first_used: string;
  last_used: string;
  source_types: string[];
}

interface ChatHistory {
  id: string;
  timestamp: string;
  message: string;
  response: string;
  topic: string;
  type: string;
}

const UserHistory = () => {
  const { toast } = useToast();
  const [userId, setUserId] = useState<string>('user123'); // In real app, get from auth
  const [stats, setStats] = useState<UserStats | null>(null);
  const [quizHistory, setQuizHistory] = useState<QuizHistory[]>([]);
  const [topicHistory, setTopicHistory] = useState<TopicHistory[]>([]);
  const [chatHistory, setChatHistory] = useState<ChatHistory[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedQuiz, setSelectedQuiz] = useState<QuizHistory | null>(null);

  const API_BASE_URL = 'http://localhost:5004';

  useEffect(() => {
    loadUserHistory();
  }, [userId]);

  const loadUserHistory = async () => {
    setLoading(true);
    try {
      // Load stats
      const statsResponse = await fetch(`${API_BASE_URL}/api/history/${userId}/stats`);
      if (statsResponse.ok) {
        const statsData = await statsResponse.json();
        setStats(statsData.stats);
      }

      // Load quiz history
      const quizResponse = await fetch(`${API_BASE_URL}/api/history/${userId}/quizzes`);
      if (quizResponse.ok) {
        const quizData = await quizResponse.json();
        setQuizHistory(quizData.quizzes);
      }

      // Load topic history
      const topicResponse = await fetch(`${API_BASE_URL}/api/history/${userId}/topics`);
      if (topicResponse.ok) {
        const topicData = await topicResponse.json();
        setTopicHistory(topicData.topics);
      }

      // Load chat history
      const chatResponse = await fetch(`${API_BASE_URL}/api/history/${userId}/chats`);
      if (chatResponse.ok) {
        const chatData = await chatResponse.json();
        setChatHistory(chatData.chats);
      }
    } catch (error) {
      console.error('Error loading user history:', error);
      toast({
        title: "Error",
        description: "Failed to load user history",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const clearHistory = async (type: string = 'all') => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/history/${userId}/clear?type=${type}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        toast({
          title: "Success",
          description: `Cleared ${type} history successfully`,
        });
        loadUserHistory(); // Reload data
      } else {
        throw new Error('Failed to clear history');
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to clear history",
        variant: "destructive",
      });
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBadgeVariant = (score: number) => {
    if (score >= 80) return 'default';
    if (score >= 60) return 'secondary';
    return 'destructive';
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <Card>
          <CardContent className="p-12 text-center">
            <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4" />
            <p>Loading your history...</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold mb-2">Your Learning History</h1>
          <p className="text-muted-foreground">Track your progress and review past activities</p>
        </div>
        <div className="flex gap-2">
          <Button onClick={loadUserHistory} variant="outline">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button onClick={() => clearHistory('all')} variant="destructive">
            <Trash2 className="h-4 w-4 mr-2" />
            Clear All
          </Button>
        </div>
      </div>

      {/* Stats Overview */}
      {stats && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Learning Statistics
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">{stats.total_quizzes}</div>
                <div className="text-sm text-muted-foreground">Total Quizzes</div>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">{stats.average_score}%</div>
                <div className="text-sm text-muted-foreground">Average Score</div>
              </div>
              <div className="text-center p-4 bg-purple-50 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">{stats.total_topics}</div>
                <div className="text-sm text-muted-foreground">Topics Studied</div>
              </div>
              <div className="text-center p-4 bg-orange-50 rounded-lg">
                <div className="text-2xl font-bold text-orange-600">{stats.total_chats}</div>
                <div className="text-sm text-muted-foreground">Chat Interactions</div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Top Topics */}
      {stats && stats.top_topics.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="h-5 w-5" />
              Most Studied Topics
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {stats.top_topics.map((topic, index) => (
                <div key={topic.id} className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <Badge variant="outline">{index + 1}</Badge>
                    <div>
                      <div className="font-medium">{topic.topic}</div>
                      <div className="text-sm text-muted-foreground">
                        {topic.count} times • {formatDate(topic.last_used)}
                      </div>
                    </div>
                  </div>
                  <div className="flex gap-1">
                    {topic.source_types.map((type, idx) => (
                      <Badge key={idx} variant="secondary" className="text-xs">
                        {type}
                      </Badge>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Detailed History Tabs */}
      <Tabs defaultValue="quizzes" className="space-y-4">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="quizzes" className="flex items-center gap-2">
            <BookOpen className="h-4 w-4" />
            Quiz History
          </TabsTrigger>
          <TabsTrigger value="topics" className="flex items-center gap-2">
            <Target className="h-4 w-4" />
            Topic History
          </TabsTrigger>
          <TabsTrigger value="chats" className="flex items-center gap-2">
            <MessageSquare className="h-4 w-4" />
            Chat History
          </TabsTrigger>
        </TabsList>

        <TabsContent value="quizzes" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Quiz History</CardTitle>
                <Button onClick={() => clearHistory('quizzes')} variant="outline" size="sm">
                  <Trash2 className="h-4 w-4 mr-2" />
                  Clear Quizzes
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {quizHistory.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <BookOpen className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No quiz history yet. Start taking quizzes to see your progress!</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {quizHistory.map((quiz) => (
                    <div key={quiz.id} className="border rounded-lg p-4 hover:bg-muted/50 transition-colors">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-3">
                          <div>
                            <h3 className="font-medium">{quiz.topic}</h3>
                            <div className="text-sm text-muted-foreground flex items-center gap-2">
                              <Clock className="h-3 w-3" />
                              {formatDate(quiz.timestamp)}
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge variant="outline">{quiz.source_type}</Badge>
                          <Badge variant={getScoreBadgeVariant(quiz.score_percentage)}>
                            {quiz.score_percentage}%
                          </Badge>
                          {quiz.ollama_used && (
                            <Badge variant="secondary">AI</Badge>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span>{quiz.score}/{quiz.total_questions} questions correct</span>
                        <Button
                          onClick={() => setSelectedQuiz(quiz)}
                          variant="ghost"
                          size="sm"
                        >
                          <Eye className="h-4 w-4 mr-1" />
                          View Details
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="topics" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Topic History</CardTitle>
                <Button onClick={() => clearHistory('topics')} variant="outline" size="sm">
                  <Trash2 className="h-4 w-4 mr-2" />
                  Clear Topics
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {topicHistory.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <Target className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No topic history yet. Start exploring topics to build your history!</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {topicHistory.map((topic) => (
                    <div key={topic.id} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <h3 className="font-medium">{topic.topic}</h3>
                          <div className="text-sm text-muted-foreground">
                            Studied {topic.count} times • Last: {formatDate(topic.last_used)}
                          </div>
                        </div>
                        <div className="flex gap-1">
                          {topic.source_types.map((type, idx) => (
                            <Badge key={idx} variant="secondary" className="text-xs">
                              {type}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="chats" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Chat History</CardTitle>
                <Button onClick={() => clearHistory('chats')} variant="outline" size="sm">
                  <Trash2 className="h-4 w-4 mr-2" />
                  Clear Chats
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {chatHistory.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <MessageSquare className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No chat history yet. Start chatting to see your conversations!</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {chatHistory.map((chat) => (
                    <div key={chat.id} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <div className="text-sm text-muted-foreground">
                          {formatDate(chat.timestamp)}
                        </div>
                        <Badge variant="outline">{chat.type}</Badge>
                      </div>
                      <div className="space-y-2">
                        <div>
                          <strong>You:</strong> {chat.message}
                        </div>
                        <div>
                          <strong>Response:</strong> {chat.response}
                        </div>
                        {chat.topic && (
                          <div className="text-sm text-muted-foreground">
                            Topic: {chat.topic}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Quiz Details Modal */}
      {selectedQuiz && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold">Quiz Details: {selectedQuiz.topic}</h2>
              <Button onClick={() => setSelectedQuiz(null)} variant="ghost">
                ×
              </Button>
            </div>
            
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <strong>Score:</strong> {selectedQuiz.score}/{selectedQuiz.total_questions} ({selectedQuiz.score_percentage}%)
                </div>
                <div>
                  <strong>Source:</strong> {selectedQuiz.source_type}
                </div>
                <div>
                  <strong>Date:</strong> {formatDate(selectedQuiz.timestamp)}
                </div>
                <div>
                  <strong>AI Used:</strong> {selectedQuiz.ollama_used ? 'Yes' : 'No'}
                </div>
              </div>

              {selectedQuiz.results && selectedQuiz.results.length > 0 && (
                <div>
                  <h3 className="font-semibold mb-2">Question Results:</h3>
                  <div className="space-y-2">
                    {selectedQuiz.results.map((result, index) => (
                      <div key={index} className={`p-3 rounded-lg border ${
                        result.is_correct ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'
                      }`}>
                        <div className="flex items-center justify-between mb-1">
                          <span className="font-medium">Question {index + 1}</span>
                          <Badge variant={result.is_correct ? 'default' : 'destructive'}>
                            {result.is_correct ? 'Correct' : 'Incorrect'}
                          </Badge>
                        </div>
                        <div className="text-sm text-muted-foreground">
                          <div>Your answer: {result.user_answer}</div>
                          <div>Correct answer: {result.correct_answer}</div>
                          {result.explanation && (
                            <div className="mt-1">
                              <strong>Explanation:</strong> {result.explanation}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserHistory; 