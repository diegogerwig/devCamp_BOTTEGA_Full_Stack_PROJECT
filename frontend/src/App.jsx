import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'https://time-tracer-bottega-back.onrender.com';

function App() {
  const [status, setStatus] = useState({
    backend: '🔄 Connecting...',
    loading: true
  });
  const [users, setUsers] = useState([]);
  const [timeEntries, setTimeEntries] = useState([]);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [debugInfo, setDebugInfo] = useState(null);

  useEffect(() => {
    document.documentElement.classList.add('dark');
    checkBackend();
  }, []);

  const checkBackend = async () => {
    setDebugInfo(`🔍 Intentando conectar con: ${API_URL}`);
    setStatus(prev => ({ ...prev, loading: true }));

    try {
      console.log('Connecting to:', API_URL);

      const axiosConfig = {
        timeout: 60000, // 60 segundos para dar tiempo a que "despierte" el servicio
        headers: {
          'Content-Type': 'application/json'
        }
      };

      setDebugInfo(`⏳ Despertando el servidor... (puede tomar hasta 60 segundos)`);

      // Primero probar la ruta raíz
      const homeResponse = await axios.get(`${API_URL}/`, axiosConfig);
      console.log('Home response:', homeResponse.data);
      setDebugInfo(`✅ Servidor despierto, obteniendo datos...`);

      const statusResponse = await axios.get(`${API_URL}/api/status`, axiosConfig);
      console.log('Status response:', statusResponse.data);

      const usersResponse = await axios.get(`${API_URL}/api/users`, axiosConfig);
      console.log('Users response:', usersResponse.data);

      const entriesResponse = await axios.get(`${API_URL}/api/time-entries`, axiosConfig);
      console.log('Entries response:', entriesResponse.data);

      setStatus({
        ...statusResponse.data,
        loading: false
      });
      setUsers(usersResponse.data.users);
      setTimeEntries(entriesResponse.data.time_entries);
      setDebugInfo('✅ Conexión exitosa - Base de datos SQLite funcionando');

    } catch (error) {
      console.error('Connection error:', error);

      let errorMessage = 'Unknown error';
      if (error.code === 'ECONNABORTED') {
        errorMessage = 'Timeout - El servidor en Render tardó demasiado en despertar. Inténtalo de nuevo.';
      } else if (error.response) {
        if (error.response.status === 500) {
          errorMessage = `Error interno del servidor (500). El servidor puede estar iniciándose.`;
        } else {
          errorMessage = `HTTP ${error.response.status}: ${error.response.statusText}`;
        }
      } else if (error.request) {
        errorMessage = 'No se pudo conectar con el servidor. Puede estar durmiendo en Render.';
      } else {
        errorMessage = error.message;
      }

      setStatus({
        backend: '❌ Backend not connected',
        database: '⚠️ Waiting for backend',
        deploy: '🚧 Check backend deployment',
        loading: false,
        error: `Connection failed: ${errorMessage}`
      });
      setDebugInfo(`❌ Error: ${errorMessage}`);
    }
  };

  const createSampleUser = async () => {
    try {
      setDebugInfo('🔄 Creando usuario...');
      const newUser = {
        name: 'Test User',
        email: `test${Date.now()}@example.com`,
        role: 'worker',
        department: 'Testing'
      };

      await axios.post(`${API_URL}/api/users`, newUser, { timeout: 30000 });
      setDebugInfo('✅ Usuario creado exitosamente');
      checkBackend(); // Refresh data
    } catch (error) {
      console.error('Error creating user:', error);
      setDebugInfo(`❌ Error creando usuario: ${error.message}`);
    }
  };

  const createSampleTimeEntry = async (userId) => {
    try {
      setDebugInfo('🔄 Creando registro de tiempo...');
      const now = new Date();
      const checkIn = new Date(now.getTime() - 8 * 60 * 60 * 1000); // 8 hours ago

      const newEntry = {
        user_id: userId,
        date: now.toISOString().split('T')[0],
        check_in: checkIn.toISOString(),
        check_out: now.toISOString(),
        total_hours: 8.0,
        notes: 'Sample work day'
      };

      await axios.post(`${API_URL}/api/time-entries`, newEntry, { timeout: 30000 });
      setDebugInfo('✅ Registro de tiempo creado exitosamente');
      checkBackend(); // Refresh data
    } catch (error) {
      console.error('Error creating time entry:', error);
      setDebugInfo(`❌ Error creando registro: ${error.message}`);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <div className="p-4 md:p-8">
        <div className="max-w-7xl mx-auto">

          {/* Header */}
          <div className="text-center mb-12">
            <h1 className="text-5xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
              ⏰ TimeTracer v2.0
            </h1>
            <p className="text-xl md:text-2xl text-gray-300 mb-6">
              Sistema de Gestión con PostgreSQL Persistente
            </p>
            <div className="inline-flex items-center space-x-2 bg-gradient-to-r from-green-600 to-emerald-600 text-white px-6 py-3 rounded-full font-medium shadow-lg">
              <span>🐘</span>
              <span>PostgreSQL Ready</span>
            </div>
          </div>

          {/* Navigation */}
          <div className="flex justify-center mb-8">
            <div className="bg-gray-800 border border-gray-700 rounded-xl p-2 flex space-x-2">
              {['dashboard', 'users', 'time-entries'].map(tab => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`px-6 py-2 rounded-lg font-medium transition-all ${activeTab === tab
                      ? 'bg-blue-600 text-white shadow-lg'
                      : 'text-gray-300 hover:text-white hover:bg-gray-700'
                    }`}
                >
                  {tab === 'dashboard' && '📊 Dashboard'}
                  {tab === 'users' && '👥 Users'}
                  {tab === 'time-entries' && '⏰ Time Entries'}
                </button>
              ))}
            </div>
          </div>

          {/* Debug Info */}
          {debugInfo && (
            <div className="bg-blue-900/50 border border-blue-600 rounded-xl p-4 mb-8">
              <div className="flex items-center space-x-3 mb-2">
                <span className="text-blue-400 text-lg">🔍</span>
                <h3 className="text-lg font-semibold text-blue-300">Debug Info</h3>
              </div>
              <p className="text-blue-200 text-sm">{debugInfo}</p>
              <p className="text-blue-300 text-xs mt-2">
                Backend URL: <code className="bg-blue-800/70 px-2 py-1 rounded font-mono">{API_URL}</code>
              </p>
              <button
                onClick={checkBackend}
                className="mt-3 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm transition-colors"
              >
                🔄 Reintentar Conexión
              </button>
            </div>
          )}

          {/* Error Alert */}
          {status.error && (
            <div className="bg-red-900/70 border border-red-600 rounded-xl p-6 mb-8">
              <div className="flex items-center space-x-3 mb-3">
                <span className="text-red-400 text-xl">⚠️</span>
                <h3 className="text-lg font-semibold text-red-300">Connection Error</h3>
              </div>
              <p className="text-red-200 mb-2">{status.error}</p>
              <div className="bg-red-800/50 rounded-lg p-3 mt-3">
                <p className="text-red-200 text-sm">
                  Backend URL: <code className="bg-red-800/70 px-2 py-1 rounded font-mono">{API_URL}</code>
                </p>
              </div>
            </div>
          )}

          {/* Loading State */}
          {status.loading && (
            <div className="bg-gray-800 border border-gray-700 rounded-xl p-8 mb-12">
              <div className="text-center py-12">
                <div className="relative inline-block">
                  <div className="animate-spin w-16 h-16 border-4 border-gray-600 border-t-blue-500 rounded-full mx-auto mb-6"></div>
                  <div className="absolute inset-0 animate-ping w-16 h-16 border-4 border-gray-700 border-t-purple-500 rounded-full opacity-30"></div>
                </div>
                <p className="text-xl text-gray-300">Conectando con PostgreSQL...</p>
                <p className="text-gray-500 text-sm mt-2">Puede tomar unos segundos si el servidor está inactivo</p>
              </div>
            </div>
          )}

          {/* Dashboard Tab */}
          {activeTab === 'dashboard' && !status.loading && (
            <div>
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
                      <span className="text-white text-xl">🐘</span>
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

              {/* Statistics */}
              {status.statistics && (
                <div className="bg-gray-800 border border-gray-700 rounded-xl p-8 mb-12">
                  <h2 className="text-3xl font-bold mb-8 text-center bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
                    📊 Estadísticas en Tiempo Real
                  </h2>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="text-center p-6 bg-gray-700/50 rounded-xl">
                      <div className="text-4xl font-bold text-blue-400 mb-2">{status.statistics.users}</div>
                      <div className="text-gray-300">Usuarios Registrados</div>
                    </div>
                    <div className="text-center p-6 bg-gray-700/50 rounded-xl">
                      <div className="text-4xl font-bold text-green-400 mb-2">{status.statistics.time_entries}</div>
                      <div className="text-gray-300">Registros de Tiempo</div>
                    </div>
                    <div className="text-center p-6 bg-gray-700/50 rounded-xl">
                      <div className="text-4xl font-bold text-purple-400 mb-2">{status.statistics.absences}</div>
                      <div className="text-gray-300">Ausencias</div>
                    </div>
                  </div>
                </div>
              )}

              {/* Features */}
              {status.features && (
                <div className="bg-gray-800 border border-gray-700 rounded-xl p-8">
                  <h2 className="text-3xl font-bold mb-8 text-center bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
                    ✨ Características del Sistema
                  </h2>

                  <div className="grid md:grid-cols-2 gap-4">
                    {status.features.map((feature, index) => (
                      <div key={index} className="flex items-center space-x-3 p-4 bg-gray-700/50 rounded-lg hover:bg-gray-700 transition-colors">
                        <span className="text-green-400 text-lg flex-shrink-0">✅</span>
                        <span className="text-gray-200">{feature}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Users Tab */}
          {activeTab === 'users' && !status.loading && (
            <div className="bg-gray-800 border border-gray-700 rounded-xl p-8">
              <div className="flex justify-between items-center mb-8">
                <h2 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
                  👥 Gestión de Usuarios
                </h2>
                <button
                  onClick={createSampleUser}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors shadow-lg"
                >
                  ➕ Crear Usuario de Prueba
                </button>
              </div>

              {users.length === 0 ? (
                <div className="text-center py-12">
                  <div className="text-6xl mb-4">👥</div>
                  <h3 className="text-xl font-semibold text-gray-300 mb-2">No hay usuarios registrados</h3>
                  <p className="text-gray-500 mb-6">Crea tu primer usuario para comenzar</p>
                  <button
                    onClick={createSampleUser}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
                  >
                    Crear Primer Usuario
                  </button>
                </div>
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                  {users.map(user => (
                    <div key={user.id} className="bg-gray-700/70 border border-gray-600 rounded-xl p-6 hover:bg-gray-700 hover:scale-105 transition-all duration-200 hover:shadow-xl">
                      <div className="text-center">
                        <div className="relative mb-4">
                          <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto shadow-lg ring-4 ring-gray-600">
                            <span className="text-white font-bold text-2xl">{user.name.charAt(0)}</span>
                          </div>
                          <div className={`absolute -bottom-1 -right-1 w-6 h-6 rounded-full border-2 border-gray-700 shadow-md ${user.status === 'active' ? 'bg-green-500' : 'bg-red-500'
                            }`}></div>
                        </div>

                        <h3 className="font-bold text-lg mb-1 text-white">{user.name}</h3>
                        <p className="text-gray-400 text-sm mb-2">{user.email}</p>
                        <p className="text-gray-500 text-xs mb-4">{user.department}</p>

                        <span className={`inline-block px-4 py-2 text-xs font-bold rounded-full shadow-md ${user.role === 'admin' ? 'bg-red-600 text-red-100 ring-2 ring-red-500/30' :
                            user.role === 'manager' ? 'bg-blue-600 text-blue-100 ring-2 ring-blue-500/30' :
                              'bg-green-600 text-green-100 ring-2 ring-green-500/30'
                          }`}>
                          {user.role.toUpperCase()}
                        </span>

                        <div className="mt-4">
                          <button
                            onClick={() => createSampleTimeEntry(user.id)}
                            className="text-xs bg-gray-600 hover:bg-gray-500 text-white px-3 py-2 rounded-lg transition-colors"
                          >
                            ⏰ Crear Registro
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Time Entries Tab */}
          {activeTab === 'time-entries' && !status.loading && (
            <div className="bg-gray-800 border border-gray-700 rounded-xl p-8">
              <h2 className="text-3xl font-bold mb-8 text-center bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
                ⏰ Registros de Tiempo
              </h2>

              {timeEntries.length === 0 ? (
                <div className="text-center py-12">
                  <div className="text-6xl mb-4">⏰</div>
                  <h3 className="text-xl font-semibold text-gray-300 mb-2">No hay registros de tiempo</h3>
                  <p className="text-gray-500">Los registros aparecerán aquí cuando los usuarios marquen entrada/salida</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {timeEntries.slice(0, 10).map(entry => {
                    const user = users.find(u => u.id === entry.user_id);
                    return (
                      <div key={entry.id} className="bg-gray-700/50 border border-gray-600 rounded-lg p-6 hover:bg-gray-700 transition-colors">
                        <div className="flex justify-between items-start">
                          <div className="flex items-center space-x-4">
                            <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-blue-600 rounded-full flex items-center justify-center shadow-lg">
                              <span className="text-white font-bold text-lg">
                                {user ? user.name.charAt(0) : '?'}
                              </span>
                            </div>
                            <div>
                              <h3 className="font-semibold text-white">{user ? user.name : 'Usuario desconocido'}</h3>
                              <p className="text-gray-400 text-sm">{entry.date}</p>
                            </div>
                          </div>

                          <div className="text-right">
                            <div className="text-2xl font-bold text-green-400">
                              {entry.total_hours ? `${entry.total_hours}h` : 'En curso'}
                            </div>
                            <div className="text-gray-400 text-sm space-y-1">
                              {entry.check_in && (
                                <div>Entrada: {new Date(entry.check_in).toLocaleTimeString()}</div>
                              )}
                              {entry.check_out && (
                                <div>Salida: {new Date(entry.check_out).toLocaleTimeString()}</div>
                              )}
                            </div>
                          </div>
                        </div>

                        {entry.notes && (
                          <div className="mt-4 p-3 bg-gray-800/50 rounded-lg">
                            <p className="text-gray-300 text-sm">{entry.notes}</p>
                          </div>
                        )}
                      </div>
                    );
                  })}

                  {timeEntries.length > 10 && (
                    <div className="text-center pt-4">
                      <p className="text-gray-400">Mostrando los 10 registros más recientes de {timeEntries.length} total</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Footer */}
          <div className="text-center mt-12 py-8 border-t border-gray-700">
            <p className="text-gray-400 mb-2">
              <span className="font-bold">TimeTracer v2.0</span> - Sistema con PostgreSQL Persistente
            </p>
            <p className="text-gray-500 text-sm">
              🐘 Base de datos PostgreSQL en Render | Proyecto devCAMP BOTTEGA 2025
            </p>
            {status.database_type && (
              <p className="text-gray-600 text-xs mt-2">
                Database: {status.database_type} | Environment: {status.environment}
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;