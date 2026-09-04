import { useState } from 'react';
import { Home3D } from './pages/Home3D';
import { Login } from './pages/Login';
import { DashboardOverview } from './pages/DashboardOverview';
import { UserRole } from './context/AuthContext';

export default function App() {
  const [currentView, setCurrentView] = useState<'landing' | 'login' | 'dashboard'>('landing');
  const [loginRole, setLoginRole] = useState<UserRole | null>(null);
  const [user, setUser] = useState<{ email: string; role: UserRole; fullName: string } | null>(null);

  const handleLoginSuccess = async (email: string, role: UserRole, fullName: string) => {
    setUser({ email, role, fullName });
    setCurrentView('dashboard');
  };

  if (currentView === 'landing') {
    return (
      <Home3D 
        onLoginSuccess={handleLoginSuccess}
        onStudentLogin={() => {
          setLoginRole('student');
          setCurrentView('login');
        }}
        onFacultyLogin={() => {
          setLoginRole('faculty');
          setCurrentView('login');
        }}
      />
    );
  }

  if (currentView === 'login') {
    return (
      <Login 
        onLoginSuccess={handleLoginSuccess}
        onBackToHome={() => setCurrentView('landing')}
        preselectedRole={loginRole}
      />
    );
  }

  const handleSwitchRole = (newRole: UserRole) => {
    if (user) {
      const defaultName = newRole === 'student' ? 'Alexander Wright' : 'Dr. Sarah Jenkins';
      const defaultEmail = newRole === 'student' ? 'student1@uniagent.edu' : 'faculty@uniagent.edu';
      setUser({
        email: defaultEmail,
        role: newRole,
        fullName: defaultName
      });
    }
  };

  const handleUpdateProfile = (fullName: string, email: string) => {
    if (user) {
      setUser(prev => prev ? { ...prev, fullName, email } : null);
    }
  };

  // Dashboard Overview
  return (
    <DashboardOverview 
      user={user}
      onUpdateProfile={handleUpdateProfile}
      onLogout={() => {
        setUser(null);
        setCurrentView('landing');
      }}
      onSwitchRole={handleSwitchRole}
    />
  );
}
