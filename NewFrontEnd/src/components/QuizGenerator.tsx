import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Upload, FileText, MessageSquare, CheckCircle, XCircle, RotateCcw, AlertCircle } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { trackQuizActivity, trackFileUploadActivity, trackTopicStudyActivity, updateStreak } from '@/utils/activityTracker';

type QuizState = 'input' | 'generating' | 'quiz' | 'results';

interface Question {
  type: 'mcq' | 'fill_blank' | 'true_false';
  question: string;
  options?: string[];
  correct_answer: string;
  explanation: string;
}

interface QuizResult {
  question_index: number;
  is_correct: boolean;
  user_answer: string;
  correct_answer: string;
  explanation: string;
}

const QuizGenerator = () => {
  const { toast } = useToast();
  const [quizState, setQuizState] = useState<QuizState>('input');
  const [inputMethod, setInputMethod] = useState('topic');
  const [topic, setTopic] = useState('');
  const [customText, setCustomText] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState<string[]>([]);
  const [score, setScore] = useState(0);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [results, setResults] = useState<QuizResult[]>([]);
  const [numQuestions, setNumQuestions] = useState(5);
  const [questionTypes, setQuestionTypes] = useState<string[]>(['mcq', 'fill_blank', 'true_false']);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const API_BASE_URL = 'http://localhost:5004';

  useEffect(() => {
    // Check if we're resuming a quiz session
    const resumeTopic = localStorage.getItem('resumeQuizTopic');
    const resumeTimestamp = localStorage.getItem('resumeQuizTimestamp');
    
    if (resumeTopic && resumeTimestamp) {
      // Clear the resume data
      localStorage.removeItem('resumeQuizTopic');
      localStorage.removeItem('resumeQuizTimestamp');
      
      // Pre-fill the topic and set input method
      setTopic(resumeTopic);
      setInputMethod('topic');
      
      toast({
        title: "Quiz ready!",
        description: `Ready to generate a new quiz on "${resumeTopic}". Click "Generate Quiz" to start!`,
      });
    }
  }, []);

  const generateQuiz = async () => {
    setLoading(true);
    setError(null);
    setQuizState('generating');

    try {
      let response;

      if (inputMethod === 'topic') {
        response = await fetch(`${API_BASE_URL}/api/generate`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            type: 'topic',
            content: topic,
            num_questions: numQuestions,
            question_types: questionTypes
          }),
        });
      } else if (inputMethod === 'text') {
        response = await fetch(`${API_BASE_URL}/api/generate`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            type: 'text',
            content: customText,
            num_questions: numQuestions,
            question_types: questionTypes
          }),
        });
      } else if (inputMethod === 'file' && selectedFile) {
        const formData = new FormData();
        formData.append('file', selectedFile);
        formData.append('num_questions', numQuestions.toString());
        formData.append('question_types', questionTypes.join(','));

        response = await fetch(`${API_BASE_URL}/api/generate/file`, {
          method: 'POST',
          body: formData,
        });
      } else {
        throw new Error('Invalid input method or missing file');
      }

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to generate quiz');
      }

      if (data.success && data.questions) {
        setQuestions(data.questions);
        setCurrentQuestion(0);
        setAnswers(new Array(data.questions.length).fill(''));
        setScore(0);
        setQuizState('quiz');
        
        const ollamaStatus = data.ollama_used ? 'with AI' : 'using fallback questions';
        toast({
          title: "Quiz Generated!",
          description: `Successfully created ${data.total_questions} questions ${ollamaStatus}.`,
        });
      } else {
        throw new Error('Invalid response from server');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to generate quiz';
      setError(errorMessage);
      setQuizState('input');
      
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const submitAnswer = (answerIndex: string) => {
    const newAnswers = [...answers];
    newAnswers[currentQuestion] = answerIndex;
    setAnswers(newAnswers);

    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    } else {
      validateQuiz(newAnswers);
    }
  };

  const validateQuiz = async (finalAnswers: string[]) => {
    setLoading(true);
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/validate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          questions: questions,
          answers: finalAnswers
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to validate quiz');
      }

      if (data.success) {
        setResults(data.results);
        setScore(data.score);
        setQuizState('results');
        
        // Update user stats in localStorage
        updateUserStats(data.score_percentage);
        
        // Track quiz activity
        const quizTopic = inputMethod === 'topic' ? topic : 
                     inputMethod === 'text' ? 'Custom Text' : 
                     inputMethod === 'file' ? selectedFile?.name || 'File Upload' : 'Unknown';
        trackQuizActivity(quizTopic, data.score, data.total_questions);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to validate quiz';
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const updateUserStats = (scorePercentage: number) => {
    try {
      const learningStats = JSON.parse(localStorage.getItem('learningStats') || '{}');
      const currentQuizzes = learningStats.quizzesTaken || 0;
      const currentXP = learningStats.totalXP || 0;
      
      // Update learning stats
      learningStats.quizzesTaken = currentQuizzes + 1;
      learningStats.totalXP = currentXP + Math.floor(scorePercentage * 10); // Add XP based on score
      
      // Calculate level based on XP (every 1000 XP = 1 level)
      learningStats.level = Math.floor(learningStats.totalXP / 1000) + 1;
      
      localStorage.setItem('learningStats', JSON.stringify(learningStats));
      
      // Update streak using the new system (will be called automatically by trackQuizActivity)
      console.log('Quiz completed with score:', scorePercentage + '%');
    } catch (error) {
      console.error('Failed to update learning stats:', error);
    }
  };

  const resetQuiz = () => {
    setQuizState('input');
    setCurrentQuestion(0);
    setAnswers([]);
    setScore(0);
    setQuestions([]);
    setResults([]);
    setTopic('');
    setCustomText('');
    setSelectedFile(null);
    setError(null);
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      // Track file upload activity
      trackFileUploadActivity(file.name, file.type);
    }
  };

  const renderInput = () => (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold mb-2">Quiz Generator</h1>
        <p className="text-muted-foreground">Create interactive quizzes from any content using AI</p>
      </div>

      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2 text-red-600">
              <AlertCircle className="h-4 w-4" />
              <span>{error}</span>
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Input Method</CardTitle>
          <CardDescription>Select how you want to provide content for your quiz</CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs value={inputMethod} onValueChange={setInputMethod}>
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="topic">Topic</TabsTrigger>
              <TabsTrigger value="text">Custom Text</TabsTrigger>
              <TabsTrigger value="file">File Upload</TabsTrigger>
            </TabsList>
            
            <TabsContent value="topic" className="space-y-4">
              <div>
                <Label htmlFor="topic">Enter a topic</Label>
                <Input
                  id="topic"
                  placeholder="e.g., React Hooks, Machine Learning, History of Rome..."
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                />
              </div>
              <Button 
                onClick={generateQuiz} 
                disabled={!topic.trim() || loading}
                className="w-full learning-gradient"
              >
                <MessageSquare className="h-4 w-4 mr-2" />
                {loading ? 'Generating...' : 'Generate Quiz from Topic'}
              </Button>
            </TabsContent>
            
            <TabsContent value="text" className="space-y-4">
              <div>
                <Label htmlFor="customText">Paste your content</Label>
                <Textarea
                  id="customText"
                  placeholder="Paste any text content here and we'll create a quiz based on it..."
                  value={customText}
                  onChange={(e) => setCustomText(e.target.value)}
                  rows={6}
                />
              </div>
              <Button 
                onClick={generateQuiz} 
                disabled={!customText.trim() || loading}
                className="w-full learning-gradient"
              >
                <FileText className="h-4 w-4 mr-2" />
                {loading ? 'Generating...' : 'Generate Quiz from Text'}
              </Button>
            </TabsContent>
            
            <TabsContent value="file" className="space-y-4">
              <div className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-8 text-center">
                <Upload className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">Upload File</h3>
                <p className="text-muted-foreground mb-4">Drop your file here or click to browse (PDF, DOCX, TXT)</p>
                <input
                  type="file"
                  accept=".pdf,.docx,.txt"
                  onChange={handleFileChange}
                  className="hidden"
                  id="file-upload"
                />
                <label htmlFor="file-upload">
                  <Button variant="outline" asChild>
                    <span>Select File</span>
                  </Button>
                </label>
                {selectedFile && (
                  <p className="mt-2 text-sm text-green-600">{selectedFile.name}</p>
                )}
              </div>
              <Button 
                onClick={generateQuiz} 
                disabled={!selectedFile || loading}
                className="w-full learning-gradient"
              >
                <Upload className="h-4 w-4 mr-2" />
                {loading ? 'Generating...' : 'Generate Quiz from File'}
              </Button>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Quiz Settings</CardTitle>
          <CardDescription>Customize your quiz generation</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="numQuestions">Number of Questions</Label>
              <Select value={numQuestions.toString()} onValueChange={(value) => setNumQuestions(parseInt(value))}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="3">3 Questions</SelectItem>
                  <SelectItem value="5">5 Questions</SelectItem>
                  <SelectItem value="10">10 Questions</SelectItem>
                  <SelectItem value="15">15 Questions</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Question Types</Label>
              <div className="space-y-2 mt-2">
                {['mcq', 'fill_blank', 'true_false'].map((type) => (
                  <div key={type} className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id={type}
                      checked={questionTypes.includes(type)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setQuestionTypes([...questionTypes, type]);
                        } else {
                          setQuestionTypes(questionTypes.filter(t => t !== type));
                        }
                      }}
                    />
                    <Label htmlFor={type} className="text-sm capitalize">
                      {type.replace('_', ' ')}
                    </Label>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Features</CardTitle>
          <CardDescription>What makes our quiz generator special</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-start space-x-3">
              <div className="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center">
                <MessageSquare className="h-4 w-4 text-blue-600" />
              </div>
              <div>
                <h4 className="font-medium">AI-Powered Generation</h4>
                <p className="text-sm text-muted-foreground">Uses Ollama AI to create intelligent, contextual questions</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="h-8 w-8 rounded-full bg-purple-100 flex items-center justify-center">
                <FileText className="h-4 w-4 text-purple-600" />
              </div>
              <div>
                <h4 className="font-medium">Multiple Formats</h4>
                <p className="text-sm text-muted-foreground">Support for PDF, DOCX, and text files</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="h-8 w-8 rounded-full bg-orange-100 flex items-center justify-center">
                <CheckCircle className="h-4 w-4 text-orange-600" />
              </div>
              <div>
                <h4 className="font-medium">Smart Validation</h4>
                <p className="text-sm text-muted-foreground">Automatic answer validation with detailed explanations</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="h-8 w-8 rounded-full bg-green-100 flex items-center justify-center">
                <Upload className="h-4 w-4 text-green-600" />
              </div>
              <div>
                <h4 className="font-medium">Easy Upload</h4>
                <p className="text-sm text-muted-foreground">Simple file upload with drag-and-drop support</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Recent Quizzes</CardTitle>
          <CardDescription>Your recently generated quizzes</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[
              { title: 'React Hooks Quiz', questions: 10, score: 85, date: '2 hours ago' },
              { title: 'JavaScript Fundamentals', questions: 15, score: 92, date: '1 day ago' },
              { title: 'CSS Grid Layout', questions: 8, score: 78, date: '3 days ago' }
            ].map((quiz, index) => (
              <div key={index} className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                <div>
                  <p className="font-medium">{quiz.title}</p>
                  <p className="text-sm text-muted-foreground">{quiz.questions} questions • {quiz.date}</p>
                </div>
                <div className="text-right">
                  <Badge variant={quiz.score >= 80 ? 'default' : 'secondary'}>
                    {quiz.score}%
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );

  const renderGenerating = () => (
    <div className="space-y-6">
      <Card>
        <CardContent className="p-12 text-center">
          <div className="animate-pulse-slow mb-6">
            <div className="h-16 w-16 learning-gradient rounded-full mx-auto flex items-center justify-center">
              <MessageSquare className="h-8 w-8 text-white" />
            </div>
          </div>
          <h2 className="text-2xl font-bold mb-2">Generating Your Quiz</h2>
          <p className="text-muted-foreground mb-6">Our AI is analyzing your content and creating personalized questions...</p>
          <Progress value={66} className="w-full max-w-md mx-auto" />
        </CardContent>
      </Card>
    </div>
  );

  const renderQuiz = () => {
    if (!questions.length || currentQuestion >= questions.length) {
      return <div>No questions available</div>;
    }

    const question = questions[currentQuestion];

    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold">Quiz</h1>
          <Badge variant="outline">
            Question {currentQuestion + 1} of {questions.length}
          </Badge>
        </div>

        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Question {currentQuestion + 1}</CardTitle>
              <Progress value={((currentQuestion + 1) / questions.length) * 100} className="w-32" />
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="mb-4">
              <Badge variant="secondary" className="mb-2 capitalize">
                {question.type.replace('_', ' ')}
              </Badge>
              <h2 className="text-xl">{question.question}</h2>
            </div>
            
            {question.type === 'mcq' && question.options && (
              <RadioGroup onValueChange={submitAnswer} value={answers[currentQuestion] || ''}>
                {question.options.map((option, index) => (
                  <div key={index} className="flex items-center space-x-2 p-3 rounded-lg border hover:bg-muted/50 cursor-pointer">
                    <RadioGroupItem value={String.fromCharCode(65 + index)} id={`option-${index}`} />
                    <Label htmlFor={`option-${index}`} className="flex-1 cursor-pointer">
                      {option}
                    </Label>
                  </div>
                ))}
              </RadioGroup>
            )}
            
            {question.type === 'fill_blank' && (
              <div className="space-y-4">
                <Input
                  placeholder="Type your answer here..."
                  value={answers[currentQuestion] || ''}
                  onChange={(e) => {
                    const newAnswers = [...answers];
                    newAnswers[currentQuestion] = e.target.value;
                    setAnswers(newAnswers);
                  }}
                />
                <Button 
                  onClick={() => submitAnswer(answers[currentQuestion] || '')}
                  disabled={!answers[currentQuestion]?.trim()}
                  className="w-full"
                >
                  Next Question
                </Button>
              </div>
            )}
            
            {question.type === 'true_false' && (
              <RadioGroup onValueChange={submitAnswer} value={answers[currentQuestion] || ''}>
                <div className="flex items-center space-x-2 p-3 rounded-lg border hover:bg-muted/50 cursor-pointer">
                  <RadioGroupItem value="True" id="true" />
                  <Label htmlFor="true" className="flex-1 cursor-pointer">True</Label>
                </div>
                <div className="flex items-center space-x-2 p-3 rounded-lg border hover:bg-muted/50 cursor-pointer">
                  <RadioGroupItem value="False" id="false" />
                  <Label htmlFor="false" className="flex-1 cursor-pointer">False</Label>
                </div>
              </RadioGroup>
            )}
          </CardContent>
        </Card>
      </div>
    );
  };

  const renderResults = () => (
    <div className="space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold mb-2">Quiz Complete!</h1>
        <p className="text-muted-foreground">Here are your results</p>
      </div>

      <Card>
        <CardContent className="p-8 text-center">
          <div className="mb-6">
            <div className={`h-20 w-20 mx-auto rounded-full flex items-center justify-center ${score >= questions.length * 0.7 ? 'bg-green-100' : 'bg-orange-100'}`}>
              {score >= questions.length * 0.7 ? (
                <CheckCircle className="h-10 w-10 text-green-600" />
              ) : (
                <XCircle className="h-10 w-10 text-orange-600" />
              )}
            </div>
          </div>
          
          <h2 className="text-4xl font-bold mb-2">{Math.round((score / questions.length) * 100)}%</h2>
          <p className="text-muted-foreground mb-6">
            You got {score} out of {questions.length} questions correct
          </p>
          
          <div className="grid grid-cols-3 gap-4 mb-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{score}</div>
              <div className="text-sm text-muted-foreground">Correct</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">{questions.length - score}</div>
              <div className="text-sm text-muted-foreground">Incorrect</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{questions.length}</div>
              <div className="text-sm text-muted-foreground">Total</div>
            </div>
          </div>
          
          <div className="flex gap-4 justify-center">
            <Button onClick={resetQuiz} variant="outline">
              <RotateCcw className="h-4 w-4 mr-2" />
              Create New Quiz
            </Button>
            <Button onClick={() => setQuizState('quiz')}>
              Review Answers
            </Button>
          </div>
        </CardContent>
      </Card>

      {results.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Detailed Results</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {results.map((result, index) => (
                <div key={index} className={`p-4 rounded-lg border ${result.is_correct ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}`}>
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="font-medium">Question {index + 1}</h3>
                    <Badge variant={result.is_correct ? 'default' : 'destructive'}>
                      {result.is_correct ? 'Correct' : 'Incorrect'}
                    </Badge>
                  </div>
                  <p className="text-sm text-muted-foreground mb-2">
                    <strong>Your answer:</strong> {result.user_answer}
                  </p>
                  <p className="text-sm text-muted-foreground mb-2">
                    <strong>Correct answer:</strong> {result.correct_answer}
                  </p>
                  {result.explanation && (
                    <p className="text-sm">
                      <strong>Explanation:</strong> {result.explanation}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );

  return (
    <div className="animate-fade-in">
      {quizState === 'input' && renderInput()}
      {quizState === 'generating' && renderGenerating()}
      {quizState === 'quiz' && renderQuiz()}
      {quizState === 'results' && renderResults()}
    </div>
  );
};

export default QuizGenerator;
