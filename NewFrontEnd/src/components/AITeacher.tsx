import React, { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Send, MessageSquare, Bot, User, ExternalLink, BookOpen, Lightbulb } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { trackChatActivity } from '@/utils/activityTracker';

interface Message {
  id: number;
  text: string;
  sender: 'user' | 'ai';
  timestamp: Date;
  sources?: Source[];
}

interface Source {
  title: string;
  url: string;
}

interface Suggestion {
  category: string;
  questions: string[];
}

interface Topic {
  name: string;
  subtopics: string[];
  icon: string;
}

const AITeacher = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      text: "Hello! I'm your AI teaching assistant. I'm here to help you learn anything you'd like. What would you like to explore today?",
      sender: 'ai',
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [topics, setTopics] = useState<Topic[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const { toast } = useToast();

  const API_BASE_URL = 'http://localhost:5003';

  useEffect(() => {
    fetchSuggestions();
    fetchTopics();
    
    // Check if we're resuming a chat session
    const resumeTopic = localStorage.getItem('resumeChatTopic');
    const resumeTimestamp = localStorage.getItem('resumeChatTimestamp');
    
    if (resumeTopic && resumeTimestamp) {
      // Clear the resume data
      localStorage.removeItem('resumeChatTopic');
      localStorage.removeItem('resumeChatTimestamp');
      
      // Add a welcome back message
      const welcomeMessage: Message = {
        id: Date.now(),
        text: `Welcome back! I see you were previously discussing "${resumeTopic}". How can I help you continue with this topic or explore something new?`,
        sender: 'ai',
        timestamp: new Date()
      };
      
      setMessages(prev => [prev[0], welcomeMessage]); // Keep the initial greeting and add the welcome message
      
      toast({
        title: "Chat resumed!",
        description: `Continuing conversation about "${resumeTopic}"`,
      });
    }
  }, []);

  const fetchSuggestions = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/suggestions`);
      if (response.ok) {
        const data = await response.json();
        setSuggestions(data.suggestions || []);
      }
    } catch (error) {
      console.error('Error fetching suggestions:', error);
    }
  };

  const fetchTopics = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/topics`);
      if (response.ok) {
        const data = await response.json();
        setTopics(data.topics || []);
      }
    } catch (error) {
      console.error('Error fetching topics:', error);
    }
  };

  const sendMessage = async (text: string) => {
    if (!text.trim()) return;

    const userMessage: Message = {
      id: Date.now(),
      text: text.trim(),
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsTyping(true);
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: text.trim(),
          user_id: 'user123' // In real app, get from auth
        }),
      });

      if (response.ok) {
        const data = await response.json();
        
        const aiResponse: Message = {
          id: Date.now() + 1,
          text: data.response.answer,
          sender: 'ai',
          timestamp: new Date(),
          sources: data.response.sources || []
        };
        
        setMessages(prev => [...prev, aiResponse]);

        // Track chat activity
        trackChatActivity(text.substring(0, 50) + (text.length > 50 ? '...' : ''));

      } else {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to get response');
      }
    } catch (error) {
      console.error('Error sending message:', error);
      
      const errorMessage: Message = {
        id: Date.now() + 1,
        text: "I'm sorry, I'm having trouble connecting to my knowledge base right now. Please try again in a moment, or check if the AI Teacher service is running.",
        sender: 'ai',
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, errorMessage]);
      
      toast({
        title: "Connection Error",
        description: "Unable to connect to AI Teacher service. Please check if the backend is running.",
        variant: "destructive",
      });
    } finally {
      setIsTyping(false);
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(inputMessage);
    }
  };

  useEffect(() => {
    if (scrollAreaRef.current) {
      const scrollContainer = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]');
      if (scrollContainer) {
        scrollContainer.scrollTop = scrollContainer.scrollHeight;
      }
    }
  }, [messages]);

  const renderMessage = (message: Message) => (
    <div key={message.id} className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
      <div className={`flex max-w-[80%] space-x-2 ${message.sender === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
        <Avatar className="h-8 w-8 flex-shrink-0">
          <AvatarFallback className={message.sender === 'ai' ? 'learning-gradient text-white' : 'bg-primary text-primary-foreground'}>
            {message.sender === 'ai' ? <Bot className="h-4 w-4" /> : <User className="h-4 w-4" />}
          </AvatarFallback>
        </Avatar>
        <div className={`rounded-lg p-3 ${
          message.sender === 'user' 
            ? 'bg-primary text-primary-foreground' 
            : 'bg-muted'
        }`}>
          <div className="whitespace-pre-wrap text-sm">{message.text}</div>
          
          {/* Sources */}
          {message.sources && message.sources.length > 0 && (
            <div className="mt-3 pt-3 border-t border-border">
              <div className="text-xs font-medium mb-2 flex items-center">
                <BookOpen className="h-3 w-3 mr-1" />
                Sources:
              </div>
              <div className="space-y-1">
                {message.sources.map((source, index) => (
                  <a
                    key={index}
                    href={source.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block text-xs text-blue-600 hover:text-blue-800 flex items-center"
                  >
                    <ExternalLink className="h-3 w-3 mr-1" />
                    {source.title}
                  </a>
                ))}
              </div>
            </div>
          )}
          
          <div className={`text-xs mt-1 opacity-70`}>
            {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="h-[calc(100vh-8rem)] flex flex-col animate-fade-in">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">AI Teacher</h1>
        <p className="text-muted-foreground">Get instant help and explanations from your personal AI tutor</p>
      </div>

      <div className="flex-1 grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Chat Area */}
        <Card className="lg:col-span-3 flex flex-col">
          <CardHeader className="border-b">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Avatar className="h-8 w-8">
                  <AvatarFallback className="learning-gradient text-white">
                    <Bot className="h-4 w-4" />
                  </AvatarFallback>
                </Avatar>
                <div>
                  <CardTitle className="text-sm">AI Teaching Assistant</CardTitle>
                  <CardDescription className="text-xs">Available 24/7 • Powered by advanced AI</CardDescription>
                </div>
              </div>
              <Badge variant="secondary" className={isLoading ? "bg-yellow-100 text-yellow-700" : "bg-green-100 text-green-700"}>
                {isLoading ? "Processing..." : "Online"}
              </Badge>
            </div>
          </CardHeader>
          
          <CardContent className="flex-1 p-0">
            <ScrollArea ref={scrollAreaRef} className="h-[400px] lg:h-[500px] p-4">
              <div className="space-y-4">
                {messages.map(renderMessage)}
                
                {isTyping && (
                  <div className="flex justify-start">
                    <div className="flex space-x-2">
                      <Avatar className="h-8 w-8">
                        <AvatarFallback className="learning-gradient text-white">
                          <Bot className="h-4 w-4" />
                        </AvatarFallback>
                      </Avatar>
                      <div className="bg-muted rounded-lg p-3">
                        <div className="flex space-x-1">
                          <div className="w-2 h-2 bg-muted-foreground rounded-full animate-pulse"></div>
                          <div className="w-2 h-2 bg-muted-foreground rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                          <div className="w-2 h-2 bg-muted-foreground rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </ScrollArea>
          </CardContent>
          
          <div className="border-t p-4">
            <div className="flex space-x-2">
              <Input
                placeholder="Ask me anything..."
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                className="flex-1"
                disabled={isLoading}
              />
              <Button 
                onClick={() => sendMessage(inputMessage)} 
                size="icon" 
                disabled={!inputMessage.trim() || isLoading}
              >
                <Send className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </Card>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Suggested Questions */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm flex items-center">
                <Lightbulb className="h-4 w-4 mr-2" />
                Suggested Questions
              </CardTitle>
              <CardDescription className="text-xs">Click to ask instantly</CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              {suggestions.slice(0, 2).map((category, categoryIndex) => (
                <div key={categoryIndex} className="space-y-1">
                  <div className="text-xs font-medium text-muted-foreground">{category.category}</div>
                  {category.questions.slice(0, 2).map((question, questionIndex) => (
                    <Button
                      key={questionIndex}
                      variant="outline"
                      size="sm"
                      className="w-full justify-start text-left h-auto p-2 text-xs"
                      onClick={() => sendMessage(question)}
                      disabled={isLoading}
                    >
                      {question}
                    </Button>
                  ))}
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Learning Topics */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm flex items-center">
                <BookOpen className="h-4 w-4 mr-2" />
                Learning Topics
              </CardTitle>
              <CardDescription className="text-xs">Explore different subjects</CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              {topics.slice(0, 4).map((topic, index) => (
                <Button
                  key={index}
                  variant="outline"
                  size="sm"
                  className="w-full justify-start text-left h-auto p-2 text-xs"
                  onClick={() => sendMessage(`Tell me about ${topic.name}`)}
                  disabled={isLoading}
                >
                  <span className="mr-2">{topic.icon}</span>
                  {topic.name}
                </Button>
              ))}
            </CardContent>
          </Card>

          {/* Learning Tips */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Learning Tips</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-xs">
              <div className="flex items-start space-x-2">
                <div className="w-2 h-2 learning-gradient rounded-full mt-1 flex-shrink-0"></div>
                <p>Ask specific questions for better answers</p>
              </div>
              <div className="flex items-start space-x-2">
                <div className="w-2 h-2 learning-gradient rounded-full mt-1 flex-shrink-0"></div>
                <p>Request examples and code snippets</p>
              </div>
              <div className="flex items-start space-x-2">
                <div className="w-2 h-2 learning-gradient rounded-full mt-1 flex-shrink-0"></div>
                <p>Ask for step-by-step explanations</p>
              </div>
              <div className="flex items-start space-x-2">
                <div className="w-2 h-2 learning-gradient rounded-full mt-1 flex-shrink-0"></div>
                <p>Don't hesitate to ask follow-up questions</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default AITeacher;
