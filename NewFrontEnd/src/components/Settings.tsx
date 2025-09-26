import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  User, 
  Mail, 
  Lock, 
  Edit, 
  Save, 
  X, 
  Camera,
  Bell,
  Moon,
  Sun,
  Shield,
  Download,
  Trash2,
  Eye,
  EyeOff
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

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

const Settings = () => {
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
  const [isEditing, setIsEditing] = useState(false);
  const [isUploadingAvatar, setIsUploadingAvatar] = useState(false);
  const [avatarKey, setAvatarKey] = useState(0);
  
  // Settings states
  const [isChangingPassword, setIsChangingPassword] = useState(false);
  const [isChangingEmail, setIsChangingEmail] = useState(false);
  const [passwordForm, setPasswordForm] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });
  const [emailForm, setEmailForm] = useState({
    currentEmail: '',
    newEmail: '',
    password: ''
  });

  // App preferences
  const [preferences, setPreferences] = useState({
    notifications: true,
    emailNotifications: true,
    darkMode: false,
    language: 'en'
  });

  // Password visibility states
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [showEmailPassword, setShowEmailPassword] = useState(false);

  // Load data on component mount
  useEffect(() => {
    const userData = getUserData();
    if (userData) {
      setProfile(userData);
    }
  }, []);

  const saveProfile = () => {
    try {
      localStorage.setItem('user', JSON.stringify(profile));
      setIsEditing(false);
      toast({
        title: "Profile updated!",
        description: "Your profile information has been saved successfully.",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to save profile. Please try again.",
        variant: "destructive",
      });
    }
  };

  // Handle avatar upload
  const handleAvatarUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      toast({
        title: "Invalid file type",
        description: "Please select an image file (JPEG, PNG, GIF, etc.)",
        variant: "destructive",
      });
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      toast({
        title: "File too large",
        description: "Please select an image smaller than 5MB",
        variant: "destructive",
      });
      return;
    }

    setIsUploadingAvatar(true);

    const reader = new FileReader();
    reader.onload = (e) => {
      const result = e.target?.result as string;
      if (result && result.startsWith('data:image/')) {
        const updatedProfile = { ...profile, avatar: result };
        setProfile(updatedProfile);
        localStorage.setItem('user', JSON.stringify(updatedProfile));
        
        toast({
          title: "Profile picture updated!",
          description: "Your profile picture has been uploaded successfully.",
        });
        setAvatarKey(prevKey => prevKey + 1);
        
        // Dispatch custom event to notify other components
        window.dispatchEvent(new CustomEvent('profileUpdated'));
      } else {
        toast({
          title: "Upload failed",
          description: "Invalid image data. Please try again.",
          variant: "destructive",
        });
      }
      setIsUploadingAvatar(false);
    };

    reader.onerror = () => {
      toast({
        title: "Upload failed",
        description: "Failed to upload the image. Please try again.",
        variant: "destructive",
      });
      setIsUploadingAvatar(false);
    };

    reader.readAsDataURL(file);
  };

  // Handle password change
  const handlePasswordChange = () => {
    if (!passwordForm.currentPassword || !passwordForm.newPassword || !passwordForm.confirmPassword) {
      toast({
        title: "Missing fields",
        description: "Please fill in all password fields.",
        variant: "destructive",
      });
      return;
    }

    if (passwordForm.newPassword.length < 6) {
      toast({
        title: "Password too short",
        description: "New password must be at least 6 characters long.",
        variant: "destructive",
      });
      return;
    }

    if (passwordForm.newPassword !== passwordForm.confirmPassword) {
      toast({
        title: "Passwords don't match",
        description: "New password and confirm password must match.",
        variant: "destructive",
      });
      return;
    }

    const hasUpperCase = /[A-Z]/.test(passwordForm.newPassword);
    const hasLowerCase = /[a-z]/.test(passwordForm.newPassword);
    const hasNumbers = /\d/.test(passwordForm.newPassword);
    
    if (!hasUpperCase || !hasLowerCase || !hasNumbers) {
      toast({
        title: "Weak password",
        description: "Password must contain uppercase, lowercase, and numbers.",
        variant: "destructive",
      });
      return;
    }

    try {
      localStorage.setItem('userPassword', passwordForm.newPassword);
      
      setPasswordForm({
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      });
      setIsChangingPassword(false);
      
      toast({
        title: "Password updated!",
        description: "Your password has been changed successfully.",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update password. Please try again.",
        variant: "destructive",
      });
    }
  };

  // Handle email change
  const handleEmailChange = () => {
    if (!emailForm.currentEmail || !emailForm.newEmail || !emailForm.password) {
      toast({
        title: "Missing fields",
        description: "Please fill in all email fields.",
        variant: "destructive",
      });
      return;
    }

    if (!emailForm.newEmail.includes('@')) {
      toast({
        title: "Invalid email",
        description: "Please enter a valid email address.",
        variant: "destructive",
      });
      return;
    }

    if (emailForm.newEmail === emailForm.currentEmail) {
      toast({
        title: "Same email",
        description: "New email must be different from current email.",
        variant: "destructive",
      });
      return;
    }

    try {
      const updatedProfile = { ...profile, email: emailForm.newEmail };
      setProfile(updatedProfile);
      localStorage.setItem('user', JSON.stringify(updatedProfile));
      
      setEmailForm({
        currentEmail: '',
        newEmail: '',
        password: ''
      });
      setIsChangingEmail(false);
      
      window.dispatchEvent(new CustomEvent('profileUpdated'));
      
      toast({
        title: "Email updated!",
        description: "Your email has been changed successfully.",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update email. Please try again.",
        variant: "destructive",
      });
    }
  };

  // Handle preferences update
  const updatePreferences = (key: string, value: any) => {
    const updatedPreferences = { ...preferences, [key]: value };
    setPreferences(updatedPreferences);
    localStorage.setItem('userPreferences', JSON.stringify(updatedPreferences));
    
    toast({
      title: "Preferences updated!",
      description: "Your preferences have been saved.",
    });
  };

  // Export user data
  const exportUserData = () => {
    const userData = {
      profile,
      preferences,
      exportDate: new Date().toISOString()
    };
    
    const dataStr = JSON.stringify(userData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `user-data-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    
    URL.revokeObjectURL(url);
    
    toast({
      title: "Data exported!",
      description: "Your data has been downloaded successfully.",
    });
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold mb-2">Settings</h1>
        <p className="text-muted-foreground">Manage your account settings and preferences</p>
      </div>

      <Tabs defaultValue="account" className="space-y-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="account">Account</TabsTrigger>
          <TabsTrigger value="preferences">Preferences</TabsTrigger>
          <TabsTrigger value="security">Security</TabsTrigger>
        </TabsList>

        <TabsContent value="account" className="space-y-6">
          {/* Personal Information */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Personal Information</CardTitle>
                  <CardDescription>Update your profile details</CardDescription>
                </div>
                <Button variant="outline" onClick={() => setIsEditing(!isEditing)}>
                  {isEditing ? <X className="h-4 w-4 mr-2" /> : <Edit className="h-4 w-4 mr-2" />}
                  {isEditing ? 'Cancel' : 'Edit'}
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center space-x-4">
                <div className="relative">
                  <Avatar className="h-16 w-16">
                    <AvatarImage 
                      src={profile.avatar || "/placeholder.svg"} 
                      alt={profile.name}
                    />
                    <AvatarFallback className="text-lg">
                      {profile.name ? profile.name.split(' ').map(n => n[0]).join('') : 'U'}
                    </AvatarFallback>
                  </Avatar>
                  <Button 
                    size="icon" 
                    variant="outline" 
                    className="absolute -bottom-1 -right-1 h-6 w-6 rounded-full"
                    disabled={isUploadingAvatar}
                    onClick={() => document.getElementById('avatar-upload')?.click()}
                  >
                    {isUploadingAvatar ? (
                      <div className="h-3 w-3 animate-spin rounded-full border-2 border-primary border-t-transparent" />
                    ) : (
                      <Camera className="h-3 w-3" />
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
                <div>
                  <h3 className="font-semibold">{profile.name || 'User'}</h3>
                  <p className="text-sm text-muted-foreground">{profile.email}</p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="name">Full Name</Label>
                  <Input 
                    id="name" 
                    value={profile.name} 
                    disabled={!isEditing}
                    onChange={(e) => setProfile({...profile, name: e.target.value})}
                  />
                </div>
                <div>
                  <Label htmlFor="phone">Phone</Label>
                  <Input 
                    id="phone" 
                    value={profile.phone} 
                    disabled={!isEditing}
                    onChange={(e) => setProfile({...profile, phone: e.target.value})}
                    placeholder="+1 (555) 123-4567"
                  />
                </div>
                <div>
                  <Label htmlFor="location">Location</Label>
                  <Input 
                    id="location" 
                    value={profile.location} 
                    disabled={!isEditing}
                    onChange={(e) => setProfile({...profile, location: e.target.value})}
                    placeholder="City, Country"
                  />
                </div>
              </div>
              <div>
                <Label htmlFor="bio">Bio</Label>
                <Textarea 
                  id="bio" 
                  value={profile.bio} 
                  disabled={!isEditing}
                  onChange={(e) => setProfile({...profile, bio: e.target.value})}
                  placeholder="Tell us about yourself..."
                  rows={4}
                />
              </div>
              {isEditing && (
                <div className="flex justify-end">
                  <Button onClick={saveProfile} className="learning-gradient">
                    <Save className="h-4 w-4 mr-2" />
                    Save Changes
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Change Email */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Change Email</CardTitle>
                  <CardDescription>Update your email address</CardDescription>
                </div>
                <Button variant="outline" onClick={() => setIsChangingEmail(!isChangingEmail)}>
                  {isChangingEmail ? <X className="h-4 w-4 mr-2" /> : <Edit className="h-4 w-4 mr-2" />}
                  {isChangingEmail ? 'Cancel' : 'Change Email'}
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {isChangingEmail ? (
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="currentEmail">Current Email</Label>
                    <Input 
                      id="currentEmail" 
                      type="email"
                      value={emailForm.currentEmail}
                      onChange={(e) => setEmailForm({...emailForm, currentEmail: e.target.value})}
                      placeholder="Enter your current email"
                    />
                  </div>
                  <div>
                    <Label htmlFor="newEmail">New Email</Label>
                    <Input 
                      id="newEmail" 
                      type="email"
                      value={emailForm.newEmail}
                      onChange={(e) => setEmailForm({...emailForm, newEmail: e.target.value})}
                      placeholder="Enter your new email"
                    />
                  </div>
                  <div>
                    <Label htmlFor="emailPassword">Password</Label>
                    <div className="relative">
                      <Input 
                        id="emailPassword" 
                        type={showEmailPassword ? "text" : "password"}
                        value={emailForm.password}
                        onChange={(e) => setEmailForm({...emailForm, password: e.target.value})}
                        placeholder="Enter your password to confirm"
                        className="pr-10"
                      />
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                        onClick={() => setShowEmailPassword(!showEmailPassword)}
                      >
                        {showEmailPassword ? (
                          <EyeOff className="h-4 w-4" />
                        ) : (
                          <Eye className="h-4 w-4" />
                        )}
                      </Button>
                    </div>
                  </div>
                  <div className="flex justify-end space-x-2">
                    <Button
                      variant="outline"
                      onClick={() => {
                        setIsChangingEmail(false);
                        setEmailForm({ currentEmail: '', newEmail: '', password: '' });
                      }}
                    >
                      Cancel
                    </Button>
                    <Button onClick={handleEmailChange} className="learning-gradient">
                      <Save className="h-4 w-4 mr-2" />
                      Update Email
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="flex items-center justify-between p-4 rounded-lg border">
                  <div>
                    <p className="font-medium">Email Address</p>
                    <p className="text-sm text-muted-foreground">{profile.email}</p>
                  </div>
                  <Button variant="outline" size="sm" onClick={() => setIsChangingEmail(true)}>
                    <Edit className="h-4 w-4 mr-2" />
                    Change
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="preferences" className="space-y-6">
          {/* App Preferences */}
          <Card>
            <CardHeader>
              <CardTitle>App Preferences</CardTitle>
              <CardDescription>Customize your learning experience</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Push Notifications</p>
                  <p className="text-sm text-muted-foreground">Receive notifications about your progress</p>
                </div>
                <Button
                  variant={preferences.notifications ? "default" : "outline"}
                  size="sm"
                  onClick={() => updatePreferences('notifications', !preferences.notifications)}
                >
                  {preferences.notifications ? 'On' : 'Off'}
                </Button>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Email Notifications</p>
                  <p className="text-sm text-muted-foreground">Receive updates via email</p>
                </div>
                <Button
                  variant={preferences.emailNotifications ? "default" : "outline"}
                  size="sm"
                  onClick={() => updatePreferences('emailNotifications', !preferences.emailNotifications)}
                >
                  {preferences.emailNotifications ? 'On' : 'Off'}
                </Button>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Dark Mode</p>
                  <p className="text-sm text-muted-foreground">Use dark theme</p>
                </div>
                <Button
                  variant={preferences.darkMode ? "default" : "outline"}
                  size="sm"
                  onClick={() => updatePreferences('darkMode', !preferences.darkMode)}
                >
                  {preferences.darkMode ? <Moon className="h-4 w-4" /> : <Sun className="h-4 w-4" />}
                </Button>
              </div>

              <div>
                <Label htmlFor="language">Language</Label>
                <select
                  id="language"
                  value={preferences.language}
                  onChange={(e) => updatePreferences('language', e.target.value)}
                  className="mt-1 block w-full rounded-md border border-input bg-background px-3 py-2"
                >
                  <option value="en">English</option>
                  <option value="es">Spanish</option>
                  <option value="fr">French</option>
                  <option value="de">German</option>
                </select>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="security" className="space-y-6">
          {/* Change Password */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Change Password</CardTitle>
                  <CardDescription>Update your account password</CardDescription>
                </div>
                <Button variant="outline" onClick={() => setIsChangingPassword(!isChangingPassword)}>
                  {isChangingPassword ? <X className="h-4 w-4 mr-2" /> : <Edit className="h-4 w-4 mr-2" />}
                  {isChangingPassword ? 'Cancel' : 'Change Password'}
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {isChangingPassword ? (
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="currentPassword">Current Password</Label>
                    <div className="relative">
                      <Input 
                        id="currentPassword" 
                        type={showCurrentPassword ? "text" : "password"}
                        value={passwordForm.currentPassword}
                        onChange={(e) => setPasswordForm({...passwordForm, currentPassword: e.target.value})}
                        placeholder="Enter your current password"
                        className="pr-10"
                      />
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                        onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                      >
                        {showCurrentPassword ? (
                          <EyeOff className="h-4 w-4" />
                        ) : (
                          <Eye className="h-4 w-4" />
                        )}
                      </Button>
                    </div>
                  </div>
                  <div>
                    <Label htmlFor="newPassword">New Password</Label>
                    <div className="relative">
                      <Input 
                        id="newPassword" 
                        type={showNewPassword ? "text" : "password"}
                        value={passwordForm.newPassword}
                        onChange={(e) => setPasswordForm({...passwordForm, newPassword: e.target.value})}
                        placeholder="Enter your new password"
                        className="pr-10"
                      />
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                        onClick={() => setShowNewPassword(!showNewPassword)}
                      >
                        {showNewPassword ? (
                          <EyeOff className="h-4 w-4" />
                        ) : (
                          <Eye className="h-4 w-4" />
                        )}
                      </Button>
                    </div>
                  </div>
                  <div>
                    <Label htmlFor="confirmPassword">Confirm New Password</Label>
                    <div className="relative">
                      <Input 
                        id="confirmPassword" 
                        type={showConfirmPassword ? "text" : "password"}
                        value={passwordForm.confirmPassword}
                        onChange={(e) => setPasswordForm({...passwordForm, confirmPassword: e.target.value})}
                        placeholder="Confirm your new password"
                        className="pr-10"
                      />
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                        onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      >
                        {showConfirmPassword ? (
                          <EyeOff className="h-4 w-4" />
                        ) : (
                          <Eye className="h-4 w-4" />
                        )}
                      </Button>
                    </div>
                  </div>
                  <div className="text-sm text-muted-foreground">
                    <p>Password must contain:</p>
                    <ul className="list-disc list-inside space-y-1">
                      <li>At least 6 characters</li>
                      <li>Uppercase and lowercase letters</li>
                      <li>At least one number</li>
                    </ul>
                  </div>
                  <div className="flex justify-end space-x-2">
                    <Button
                      variant="outline"
                      onClick={() => {
                        setIsChangingPassword(false);
                        setPasswordForm({ currentPassword: '', newPassword: '', confirmPassword: '' });
                      }}
                    >
                      Cancel
                    </Button>
                    <Button onClick={handlePasswordChange} className="learning-gradient">
                      <Save className="h-4 w-4 mr-2" />
                      Update Password
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="flex items-center justify-between p-4 rounded-lg border">
                  <div>
                    <p className="font-medium">Password</p>
                    <p className="text-sm text-muted-foreground">Last updated: Recently</p>
                  </div>
                  <Button variant="outline" size="sm" onClick={() => setIsChangingPassword(true)}>
                    <Edit className="h-4 w-4 mr-2" />
                    Change
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Data Management */}
          <Card>
            <CardHeader>
              <CardTitle>Data Management</CardTitle>
              <CardDescription>Manage your account data</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Export Data</p>
                  <p className="text-sm text-muted-foreground">Download a copy of your data</p>
                </div>
                <Button variant="outline" size="sm" onClick={exportUserData}>
                  <Download className="h-4 w-4 mr-2" />
                  Export
                </Button>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-red-600">Delete Account</p>
                  <p className="text-sm text-muted-foreground">Permanently delete your account and data</p>
                </div>
                <Button variant="destructive" size="sm">
                  <Trash2 className="h-4 w-4 mr-2" />
                  Delete
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default Settings; 