import React from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import Login from './components/Login';
import AdminDashboard from './views/AdminDashboard';
import ManagerDashboard from './views/ManagerDashboard';
import WorkerDashboard from './views/WorkerDashboard';

function AppContent() {
  const { user, loading, isAuthenticated } = useAuth();

  console.log('🎭 AppContent - Estado actual:', {
    user: user?.name,
    role: user?.role,
    loading,
    isAuthenticated
  });

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="relative inline-block">
            <div className="animate-spin w-16 h-16 border-4 border-gray-600 border-t-blue-500 rounded-full mx-auto mb-6"></div>
            <div className="absolute inset-0 animate-ping w-16 h-16 border-4 border-gray-700 border-t-purple-500 rounded-full opacity-30"></div>
          </div>
          <p className="text-xl text-gray-300">Cargando TimeTracer...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    console.log('❌ No autenticado, mostrando Login');
    return <Login />;
  }

  console.log('✅ Autenticado, mostrando dashboard para rol:', user?.role);

  // Renderizar dashboard según el rol del usuario
  switch (user?.role) {
    case 'admin':
      return <AdminDashboard />;
    case 'manager':
      return <ManagerDashboard />;
    case 'worker':
      return <WorkerDashboard />;
    default:
      return (
        <div className="min-h-screen bg-gray-900 flex items-center justify-center">
          <div className="text-center">
            <div className="text-6xl mb-4">⚠️</div>
            <h2 className="text-2xl font-bold text-red-400 mb-2">
              Rol no reconocido
            </h2>
            <p className="text-gray-400">
              El rol "{user?.role}" no está configurado en el sistema
            </p>
          </div>
        </div>
      );
  }
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;