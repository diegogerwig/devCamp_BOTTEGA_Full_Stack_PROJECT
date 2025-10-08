import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';

function Login() {
	const [email, setEmail] = useState('');
	const [password, setPassword] = useState('');
	const [error, setError] = useState('');
	const [loading, setLoading] = useState(false);
	const { login } = useAuth();

	// Función para validar formato de email
	const isValidEmail = (email) => {
		const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
		const atCount = (email.match(/@/g) || []).length;
		return emailRegex.test(email) && atCount === 1;
	};

	const handleSubmit = async (e) => {
		e.preventDefault();
		setError('');

		// Validar formato de email
		if (!isValidEmail(email)) {
			setError('Por favor, introduce un email válido (ejemplo@dominio.com)');
			return;
		}

		setLoading(true);

		console.log('🔐 Intentando login con:', email);
		console.log('📍 Estado antes del login:', {
			isAuthenticated: 'pendiente',
			token: localStorage.getItem('token') ? 'existe' : 'no existe',
			user: localStorage.getItem('user') ? 'existe' : 'no existe'
		});

		const result = await login(email, password);

		console.log('📥 Resultado del login:', result);
		console.log('📍 Estado después del login:', {
			success: result.success,
			token: localStorage.getItem('token') ? 'existe' : 'no existe',
			user: localStorage.getItem('user') ? 'existe' : 'no existe'
		});

		if (!result.success) {
			setError(result.message);
			console.error('❌ Login fallido:', result.message);
		} else {
			console.log('✅ Login exitoso, usuario:', result.user);
			console.log('⏳ Esperando actualización del estado...');

			setTimeout(() => {
				console.log('🔄 Estado debería estar actualizado ahora');
			}, 100);
		}

		setLoading(false);
	};

	// 🔑 Credenciales de prueba desde variables de entorno
	const demoCredentials = [
		{ 
			role: 'Admin', 
			email: import.meta.env.VITE_DEMO_ADMIN_EMAIL || 'admin@timetracer.com',
			password: import.meta.env.VITE_DEMO_ADMIN_PASSWORD || '' 
		},
		{ 
			role: 'Manager', 
			email: import.meta.env.VITE_DEMO_MANAGER_EMAIL || 'juan@company.com',
			password: import.meta.env.VITE_DEMO_MANAGER_PASSWORD || '' 
		},
		{ 
			role: 'Worker', 
			email: import.meta.env.VITE_DEMO_WORKER_EMAIL || 'maria@company.com',
			password: import.meta.env.VITE_DEMO_WORKER_PASSWORD || '' 
		}
	];

	const fillCredentials = (demoEmail, demoPassword) => {
		setEmail(demoEmail);
		setPassword(demoPassword);
		setError('');
	};

	return (
		<div className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
			<div className="max-w-md w-full">
				{/* Header */}
				<div className="text-center mb-8">
					<h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
						TimeTracer
					</h1>
					<p className="text-gray-400 text-lg">Sistema de Gestión de Jornada Laboral</p>
				</div>

				{/* Login Form */}
				<div className="bg-gray-800 border border-gray-700 rounded-xl p-8 shadow-2xl">
					<h2 className="text-2xl font-bold text-white mb-6 text-center">Iniciar Sesión</h2>

					{error && (
						<div className="bg-red-900/50 border border-red-600 rounded-lg p-4 mb-6">
							<p className="text-red-200 text-sm">{error}</p>
						</div>
					)}

					<form onSubmit={handleSubmit} className="space-y-6">
						<div>
							<label className="block text-gray-300 text-sm font-medium mb-2">
								Email
							</label>
							<input
								type="email"
								value={email}
								onChange={(e) => {
									setEmail(e.target.value);
									setError('');
								}}
								className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
								placeholder="tu@email.com"
								required
							/>
						</div>

						<div>
							<label className="block text-gray-300 text-sm font-medium mb-2">
								Contraseña
							</label>
							<input
								type="password"
								value={password}
								onChange={(e) => {
									setPassword(e.target.value);
									setError('');
								}}
								className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
								placeholder="••••••••"
								required
							/>
						</div>

						<button
							type="submit"
							disabled={loading}
							className={`w-full py-3 px-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-lg shadow-lg transition-all duration-200 ${loading
									? 'opacity-50 cursor-not-allowed'
									: 'hover:from-blue-700 hover:to-purple-700 hover:shadow-xl transform hover:scale-105'
								}`}
						>
							{loading ? (
								<span className="flex items-center justify-center">
									<svg className="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
										<circle
											className="opacity-25"
											cx="12"
											cy="12"
											r="10"
											stroke="currentColor"
											strokeWidth="4"
											fill="none"
										/>
										<path
											className="opacity-75"
											fill="currentColor"
											d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
										/>
									</svg>
									Iniciando sesión...
								</span>
							) : (
								'Iniciar Sesión'
							)}
						</button>
					</form>
				</div>

				{/* Demo Credentials */}
				<div className="mt-8 bg-gray-800 border border-gray-700 rounded-xl p-6">
					<h3 className="text-lg font-semibold text-white mb-4 text-center">
						🎭 Credenciales de Prueba
					</h3>
					<div className="space-y-3">
						{demoCredentials.map((demo, index) => (
							<button
								key={index}
								onClick={() => fillCredentials(demo.email, demo.password)}
								disabled={!demo.password}
								className={`w-full p-3 rounded-lg text-left transition-colors ${
									demo.password 
										? 'bg-gray-700 hover:bg-gray-600 cursor-pointer' 
										: 'bg-gray-700/50 cursor-not-allowed opacity-50'
								}`}
							>
								<div className="flex justify-between items-center">
									<div>
										<div className="text-white font-medium">{demo.role}</div>
										<div className="text-gray-400 text-sm">{demo.email}</div>
										{!demo.password && (
											<div className="text-yellow-400 text-xs mt-1">
												⚠️ Configura .env para usar esta cuenta
											</div>
										)}
									</div>
									{demo.password && (
										<span className="text-blue-400 text-sm">Usar →</span>
									)}
								</div>
							</button>
						))}
					</div>
					<p className="text-gray-500 text-xs mt-4 text-center">
						Click para autocompletar las credenciales
					</p>
				</div>

				{/* Footer */}
				<div className="text-center mt-8">
					<p className="text-gray-500 text-sm">
						TimeTracer v0.0 - Proyecto devCAMP BOTTEGA 2025
					</p>
				</div>
			</div>
		</div>
	);
}

export default Login;