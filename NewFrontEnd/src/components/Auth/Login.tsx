import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Eye, EyeOff, Mail, Lock, Loader2 } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

interface LoginProps {
  onSwitchToRegister: () => void;
  onLoginSuccess: (user: any) => void;
}

const Login = ({ onSwitchToRegister, onLoginSuccess }: LoginProps) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const { toast } = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      // Simulate API call - replace with actual authentication endpoint
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Mock validation
      if (!email || !password) {
        throw new Error('Please fill in all fields');
      }

      if (!email.includes('@')) {
        throw new Error('Please enter a valid email address');
      }

      if (password.length < 6) {
        throw new Error('Password must be at least 6 characters');
      }

      // Mock successful login
      // Check for existing user data to preserve avatar and profile info
      const existingUserStr = localStorage.getItem('user');
      let existingUser = null;
      
      if (existingUserStr) {
        try {
          existingUser = JSON.parse(existingUserStr);
        } catch (e) {
          console.log('Failed to parse existing user data');
        }
      }

      const mockUser = {
        id: '1',
        email: email,
        name: email.split('@')[0],
        avatar: existingUser?.avatar || null, // Preserve existing avatar
        phone: existingUser?.phone || '',
        location: existingUser?.location || '',
        bio: existingUser?.bio || '',
        joinDate: existingUser?.joinDate || new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long' }),
        role: 'user'
      };

      // Store user data in localStorage
      localStorage.setItem('user', JSON.stringify(mockUser));
      localStorage.setItem('isAuthenticated', 'true');

      // Initialize learning stats if they don't exist
      const existingStats = localStorage.getItem('learningStats');
      if (!existingStats) {
        const defaultStats = {
          coursesCompleted: 0,
          studyHours: 0,
          quizzesTaken: 0,
          currentStreak: 0,
          totalXP: 0,
          level: 1
        };
        localStorage.setItem('learningStats', JSON.stringify(defaultStats));
      }

      // Initialize skills if they don't exist
      const existingSkills = localStorage.getItem('skills');
      if (!existingSkills) {
        const defaultSkills = [
          { name: 'JavaScript', level: 0, color: 'bg-yellow-500', lastUpdated: new Date().toISOString() },
          { name: 'React', level: 0, color: 'bg-blue-500', lastUpdated: new Date().toISOString() },
          { name: 'Python', level: 0, color: 'bg-green-500', lastUpdated: new Date().toISOString() },
          { name: 'HTML/CSS', level: 0, color: 'bg-orange-500', lastUpdated: new Date().toISOString() },
          { name: 'Node.js', level: 0, color: 'bg-purple-500', lastUpdated: new Date().toISOString() },
          { name: 'TypeScript', level: 0, color: 'bg-blue-600', lastUpdated: new Date().toISOString() }
        ];
        localStorage.setItem('skills', JSON.stringify(defaultSkills));
      }

      // Initialize achievements if they don't exist
      const existingAchievements = localStorage.getItem('achievements');
      if (!existingAchievements) {
        localStorage.setItem('achievements', JSON.stringify([]));
      }

      toast({
        title: "Login successful!",
        description: "Welcome back to LearnAI",
      });

      onLoginSuccess(mockUser);
    } catch (err: any) {
      setError(err.message || 'Login failed. Please try again.');
      toast({
        title: "Login failed",
        description: err.message || "Please check your credentials and try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-purple-50 p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 h-12 w-12 learning-gradient rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-lg">AI</span>
          </div>
          <CardTitle className="text-2xl font-bold">Welcome Back</CardTitle>
          <CardDescription>
            Sign in to your LearnAI account to continue learning
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}
            
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <div className="relative">
                <Mail className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  id="email"
                  type="email"
                  placeholder="Enter your email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="pl-10"
                  disabled={isLoading}
                  required
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <div className="relative">
                <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="pl-10 pr-10"
                  disabled={isLoading}
                  required
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  className="absolute right-0 top-0 h-full px-3"
                  onClick={() => setShowPassword(!showPassword)}
                  disabled={isLoading}
                >
                  {showPassword ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </div>

            <Button
              type="submit"
              className="w-full learning-gradient"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Signing in...
                </>
              ) : (
                'Sign In'
              )}
            </Button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm text-muted-foreground">
              Don't have an account?{' '}
              <Button
                variant="link"
                className="p-0 h-auto font-semibold text-primary"
                onClick={onSwitchToRegister}
                disabled={isLoading}
              >
                Sign up here
              </Button>
            </p>
          </div>

          <div className="mt-4 text-center">
            <Button variant="link" className="text-sm text-muted-foreground">
              Forgot your password?
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Login; 