import React, { useState, useEffect } from 'react';
import axios from 'axios';

// URL del backend - ACTUALIZAR después del deploy
const API_URL = 'https://timetracer-backend.onrender.com';

function App() {
  const [status, setStatus] = useState({
    backend: '🔄 Connecting...',
    loading: true
  });
  const [users, setUsers] = useState([]);

  useEffect(() => {
    checkBackend();
  }, []);

  const checkBackend = async () => {
    try {
      const statusResponse = await axios.get(`${API_URL}/api/status`);
      const usersResponse = await axios.get(`${API_URL}/api/users`);

      setStatus({
        ...statusResponse.data,
        loading: false
      });
      setUsers(usersResponse.data.users);

    } catch (error) {
      setStatus({
        backend: '❌ Backend not connected',
        database: '⚠️ Waiting for backend',
        deploy: '🚧 Check backend deployment',
        loading: false,
        error: 'Update API_URL in App.jsx with your backend URL'
      });
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100">
      {/* Background Pattern */}
      <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900"></div>
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(59,130,246,0.1),transparent_50%)]"></div>

      <div className="relative z-10 p-4 md:p-8">
        <div className="max-w-7xl mx-auto">

          {/* Header */}
          <div className="text-center mb-12">
            <h1 className="text-5xl md:text-7xl font-bold mb-6 gradient-text">
              ⏰ TimeTracer live
            </h1>
            <p className="text-xl md:text-2xl text-slate-300 mb-6">
              Sistema de Gestión de Jornada y Ausencias
            </p>
            <div className="inline-flex items-center space-x-2 bg-gradient-to-r from-green-600 to-emerald-600 text-white px-6 py-3 rounded-full font-medium shadow-lg">
              <span>🚀</span>
              <span>Desplegado en Render v1.0</span>
            </div>
          </div>

          {/* Error Alert */}
          {status.error && (
            <div className="dark-card bg-red-900/30 border-red-600/50 p-6 mb-8">
              <div className="flex items-center space-x-3 mb-3">
                <span className="text-red-400 text-xl">⚠️</span>
                <h3 className="text-lg font-semibold text-red-300">Configuración Requerida</h3>
              </div>
              <p className="text-red-200 mb-2">{status.error}</p>
              <div className="bg-red-800/30 rounded-lg p-3 mt-3">
                <p className="text-red-200 text-sm">
                  Backend URL: <code className="bg-red-800/50 px-2 py-1 rounded font-mono">{API_URL}</code>
                </p>
              </div>
            </div>
          )}

          {/* Status Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
            <div className="dark-card p-6 dark-hover">
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold">🔧</span>
                </div>
                <h3 className="text-xl font-semibold text-blue-400">Backend</h3>
              </div>
              <p className="text-slate-300">{status.backend}</p>
            </div>

            <div className="dark-card p-6 dark-hover">
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-10 h-10 bg-green-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold">💾</span>
                </div>
                <h3 className="text-xl font-semibold text-green-400">Database</h3>
              </div>
              <p className="text-slate-300">{status.database || '🔄 Loading...'}</p>
            </div>

            <div className="dark-card p-6 dark-hover">
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-10 h-10 bg-purple-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold">🚀</span>
                </div>
                <h3 className="text-xl font-semibold text-purple-400">Deploy</h3>
              </div>
              <p className="text-slate-300">{status.deploy || '✅ Frontend en Render'}</p>
            </div>
          </div>

          {/* Main Content */}
          <div className="dark-card p-8 mb-12">
            {status.loading ? (
              <div className="text-center py-12">
                <div className="relative">
                  <div className="animate-spin w-16 h-16 border-4 border-slate-600 border-t-blue-500 rounded-full mx-auto mb-6"></div>
                  <div className="absolute inset-0 animate-pulse">
                    <div className="w-16 h-16 border-4 border-transparent border-t-purple-500 rounded-full mx-auto opacity-50"></div>
                  </div>
                </div>
                <p className="text-xl text-slate-300">Conectando con backend...</p>
              </div>
            ) : (
              <div>
                <h2 className="text-3xl md:text-4xl font-bold mb-8 text-center gradient-text">
                  📊 Estado del Sistema
                </h2>

                {status.features && (
                  <div className="grid md:grid-cols-2 gap-8">
                    {/* Features */}
                    <div className="space-y-4">
                      <h3 className="text-2xl font-semibold text-blue-400 flex items-center space-x-2">
                        <span>✨</span>
                        <span>Características</span>
                      </h3>
                      <div className="space-y-3">
                        {status.features.map((feature, index) => (
                          <div key={index} className="flex items-center space-x-3 p-3 bg-slate-800/50 rounded-lg dark-hover">
                            <span className="text-green-400 text-lg">✅</span>
                            <span className="text-slate-300">{feature}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Next Steps */}
                    <div className="space-y-4">
                      <h3 className="text-2xl font-semibold text-yellow-400 flex items-center space-x-2">
                        <span>📋</span>
                        <span>Próximos Pasos</span>
                      </h3>
                      <div className="space-y-3">
                        {status.next_steps && status.next_steps.map((step, index) => (
                          <div key={index} className="flex items-center space-x-3 p-3 bg-slate-800/50 rounded-lg dark-hover">
                            <span className="text-yellow-400 text-lg">🔲</span>
                            <span className="text-slate-300">{step}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Users Section */}
          {users.length > 0 && (
            <div className="dark-card p-8">
              <h2 className="text-3xl font-bold mb-8 text-center gradient-text">
                👥 Usuarios del Sistema
              </h2>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                {users.map(user => (
                  <div key={user.id} className="bg-slate-800/70 rounded-xl p-6 border border-slate-600 dark-hover transform hover:scale-105 transition-all duration-200">
                    <div className="text-center">
                      {/* Avatar */}
                      <div className="relative mb-4">
                        <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto shadow-lg">
                          <span className="text-white font-bold text-2xl">{user.name.charAt(0)}</span>
                        </div>
                        <div className="absolute -bottom-1 -right-1 w-6 h-6 bg-green-500 rounded-full border-2 border-slate-800"></div>
                      </div>

                      {/* User Info */}
                      <h3 className="font-bold text-lg mb-1 text-slate-100">{user.name}</h3>
                      <p className="text-slate-400 text-sm mb-2">{user.email}</p>
                      <p className="text-slate-500 text-xs mb-4">{user.department}</p>

                      {/* Role Badge */}
                      <span className={`inline-block px-4 py-2 text-xs font-bold rounded-full ${user.role === 'admin' ? 'bg-gradient-to-r from-red-600 to-red-500 text-red-100' :
                          user.role === 'manager' ? 'bg-gradient-to-r from-blue-600 to-blue-500 text-blue-100' :
                            'bg-gradient-to-r from-green-600 to-green-500 text-green-100'
                        }`}>
                        {user.role.toUpperCase()}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Footer */}
          <div className="text-center mt-12 py-8 border-t border-slate-700">
            <p className="text-slate-400 mb-2">TimeTracer v1.0</p>
            <p className="text-slate-500 text-sm">
              Completamente desplegado en Render con modo oscuro 🌙
            </p>
          </div>

        </div>
      </div>
    </div>
  );
}

export default App;