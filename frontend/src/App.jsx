import React, { useState, useEffect } from 'react';
import axios from 'axios';

// URL del backend - ACTUALIZAR después del deploy
const API_URL = 'https://time-tracer-bottega.onrender.com/';

function App() {
  const [status, setStatus] = useState({
    backend: '🔄 Connecting...',
    loading: true
  });
  const [users, setUsers] = useState([]);

  useEffect(() => {
    // Asegurar modo oscuro
    document.documentElement.classList.add('dark');
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
        backend: '❌ Backend not connected fff',
        database: '⚠️ Waiting for backend fff',
        deploy: '🚧 Check backend deployment',
        loading: false,
        error: 'Update API_URL in App.jsx with your backend URL'
      });
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <div className="p-4 md:p-8">
        <div className="max-w-7xl mx-auto">
          
          {/* Header */}
          <div className="text-center mb-12">
            <h1 className="text-5xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
              ⏰ TimeTracer live test
            </h1>
            <p className="text-xl md:text-2xl text-gray-300 mb-6">
              Sistema de Gestión de Jornada y Ausencias
            </p>
            <div className="inline-flex items-center space-x-2 bg-gradient-to-r from-green-600 to-emerald-600 text-white px-6 py-3 rounded-full font-medium shadow-lg">
              <span>🌙</span>
              <span>v1.0</span>
            </div>
          </div>
    
          {/* Error Alert */}
          {status.error && (
            <div className="bg-red-900/70 border border-red-600 rounded-xl p-6 mb-8">
              <div className="flex items-center space-x-3 mb-3">
                <span className="text-red-400 text-xl">⚠️</span>
                <h3 className="text-lg font-semibold text-red-300">Configuración Requerida</h3>
              </div>
              <p className="text-red-200 mb-2">{status.error}</p>
              <div className="bg-red-800/50 rounded-lg p-3 mt-3">
                <p className="text-red-200 text-sm">
                  Backend URL: <code className="bg-red-800/70 px-2 py-1 rounded font-mono">{API_URL}</code>
                </p>
              </div>
            </div>
          )}

          {/* Status Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
            <div className="bg-gray-800 border border-gray-700 rounded-xl p-6 hover:bg-gray-700 transition-all duration-200 hover:scale-105">
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-12 h-12 bg-blue-600 rounded-xl flex items-center justify-center shadow-lg">
                  <span className="text-white text-xl">🔧</span>
                </div>
                <h3 className="text-xl font-semibold text-blue-400">Backend</h3>
              </div>
              <p className="text-gray-300">{status.backend}</p>
            </div>
            
            <div className="bg-gray-800 border border-gray-700 rounded-xl p-6 hover:bg-gray-700 transition-all duration-200 hover:scale-105">
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-12 h-12 bg-green-600 rounded-xl flex items-center justify-center shadow-lg">
                  <span className="text-white text-xl">💾</span>
                </div>
                <h3 className="text-xl font-semibold text-green-400">Database</h3>
              </div>
              <p className="text-gray-300">{status.database || '🔄 Loading...'}</p>
            </div>
            
            <div className="bg-gray-800 border border-gray-700 rounded-xl p-6 hover:bg-gray-700 transition-all duration-200 hover:scale-105">
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-12 h-12 bg-purple-600 rounded-xl flex items-center justify-center shadow-lg">
                  <span className="text-white text-xl">🚀</span>
                </div>
                <h3 className="text-xl font-semibold text-purple-400">Deploy</h3>
              </div>
              <p className="text-gray-300">{status.deploy || '✅ Frontend funcionando'}</p>
            </div>
          </div>

          {/* Main Content */}
          <div className="bg-gray-800 border border-gray-700 rounded-xl p-8 mb-12">
            {status.loading ? (
              <div className="text-center py-12">
                <div className="relative inline-block">
                  <div className="animate-spin w-16 h-16 border-4 border-gray-600 border-t-blue-500 rounded-full mx-auto mb-6"></div>
                  <div className="absolute inset-0 animate-ping w-16 h-16 border-4 border-gray-700 border-t-purple-500 rounded-full opacity-30"></div>
                </div>
                <p className="text-xl text-gray-300">Conectando con backend...</p>
                <p className="text-gray-500 text-sm mt-2">Puede tomar unos segundos si el servidor está inactivo</p>
              </div>
            ) : (
              <div>
                <h2 className="text-3xl md:text-4xl font-bold mb-8 text-center bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
                  📊 Estado del Sistema
                </h2>
                
                {status.features && (
                  <div className="grid md:grid-cols-2 gap-8">
                    {/* Features */}
                    <div className="space-y-4">
                      <h3 className="text-2xl font-semibold text-blue-400 flex items-center space-x-2 mb-6">
                        <span>✨</span>
                        <span>Características</span>
                      </h3>
                      <div className="space-y-3">
                        {status.features.map((feature, index) => (
                          <div key={index} className="flex items-center space-x-3 p-4 bg-gray-700/50 rounded-lg hover:bg-gray-700 transition-colors">
                            <span className="text-green-400 text-lg flex-shrink-0">✅</span>
                            <span className="text-gray-200">{feature}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                    
                    {/* Next Steps */}
                    <div className="space-y-4">
                      <h3 className="text-2xl font-semibold text-yellow-400 flex items-center space-x-2 mb-6">
                        <span>📋</span>
                        <span>Próximos Pasos</span>
                      </h3>
                      <div className="space-y-3">
                        {status.next_steps && status.next_steps.map((step, index) => (
                          <div key={index} className="flex items-center space-x-3 p-4 bg-gray-700/50 rounded-lg hover:bg-gray-700 transition-colors">
                            <span className="text-yellow-400 text-lg flex-shrink-0">🔲</span>
                            <span className="text-gray-200">{step}</span>
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
            <div className="bg-gray-800 border border-gray-700 rounded-xl p-8">
              <h2 className="text-3xl font-bold mb-8 text-center bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
                👥 Usuarios del Sistema
              </h2>
              
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                {users.map(user => (
                  <div key={user.id} className="bg-gray-700/70 border border-gray-600 rounded-xl p-6 hover:bg-gray-700 hover:scale-105 transition-all duration-200 hover:shadow-xl">
                    <div className="text-center">
                      {/* Avatar */}
                      <div className="relative mb-4">
                        <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto shadow-lg ring-4 ring-gray-600">
                          <span className="text-white font-bold text-2xl">{user.name.charAt(0)}</span>
                        </div>
                        <div className="absolute -bottom-1 -right-1 w-6 h-6 bg-green-500 rounded-full border-2 border-gray-700 shadow-md"></div>
                      </div>
                      
                      {/* User Info */}
                      <h3 className="font-bold text-lg mb-1 text-white">{user.name}</h3>
                      <p className="text-gray-400 text-sm mb-2">{user.email}</p>
                      <p className="text-gray-500 text-xs mb-4">{user.department}</p>
                      
                      {/* Role Badge */}
                      <span className={`inline-block px-4 py-2 text-xs font-bold rounded-full shadow-md ${
                        user.role === 'admin' ? 'bg-red-600 text-red-100 ring-2 ring-red-500/30' :
                        user.role === 'manager' ? 'bg-blue-600 text-blue-100 ring-2 ring-blue-500/30' : 
                        'bg-green-600 text-green-100 ring-2 ring-green-500/30'
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
          <div className="text-center mt-12 py-8 border-t border-gray-700">
            <p className="text-gray-400 mb-2">
              <span className="font-bold">TimeTracer v1.0</span> - Proyecto devCAMP BOTTEGA 2025
            </p>
            <p className="text-gray-500 text-sm">
              Modo oscuro completamente funcional con Tailwind CSS 🌙
            </p>
          </div>

        </div>
      </div>
    </div>
  );
}

export default App;