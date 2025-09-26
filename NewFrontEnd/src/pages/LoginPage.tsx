import React, { useState, useEffect } from 'react';
import Login from '@/components/Auth/Login';
import Register from '@/components/Auth/Register';
import { useNavigate } from 'react-router-dom';

const LoginPage = () => {
  const [showRegister, setShowRegister] = useState(false);
  const navigate = useNavigate();

  // Check if user is already authenticated
  useEffect(() => {
    const isAuth = localStorage.getItem('isAuthenticated') === 'true';
    if (isAuth) {
      navigate('/', { replace: true });
    }
  }, [navigate]);

  const handleLoginSuccess = (user: any) => {
    console.log('Login successful:', user);
    // Force a page reload to ensure the authentication state is properly updated
    window.location.href = '/';
  };

  const handleRegisterSuccess = (user: any) => {
    console.log('Register successful:', user);
    // Force a page reload to ensure the authentication state is properly updated
    window.location.href = '/';
  };

  return (
    <>
      {showRegister ? (
        <Register
          onSwitchToLogin={() => setShowRegister(false)}
          onRegisterSuccess={handleRegisterSuccess}
        />
      ) : (
        <Login
          onSwitchToRegister={() => setShowRegister(true)}
          onLoginSuccess={handleLoginSuccess}
        />
      )}
    </>
  );
};

export default LoginPage; 