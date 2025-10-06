import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { usersAPI, timeEntriesAPI, statusAPI } from '../services/api';

function AdminDashboard() {
	const { user, logout } = useAuth();
	const [users, setUsers] = useState([]);
	const [timeEntries, setTimeEntries] = useState([]);
	const [status, setStatus] = useState(null);
	const [activeTab, setActiveTab] = useState('dashboard');
	const [loading, setLoading] = useState(true);

	useEffect(() => {
		loadData();
	}, []);

	const loadData = async () => {
		setLoading(true);
		try {
			const [usersRes, entriesRes, statusRes] = await Promise.all([
				usersAPI.getAll(),
				timeEntriesAPI.getAll(),
				statusAPI.get()
			]);

			setUsers(usersRes.data.users);
			setTimeEntries(entriesRes.data.time_entries);
			setStatus(statusRes.data);
		} catch (error) {
			console.error('Error cargando datos:', error);
		}
		setLoading(false);
	};

	const createSampleUser = async () => {
		try {
			const newUser = {
				name: 'Test User',
				email: `test${Date.now()}@example.com`,
				password: 'test123',
				role: 'worker',
				department: 'Testing'
			};

			await usersAPI.create(newUser);
			loadData();
		} catch (error) {
			console.error('Error creando usuario:', error);
		}
	};

	const createSampleTimeEntry = async (userId) => {
		try {
			const now = new Date();
			const checkIn = new Date(now.getTime() - 8 * 60 * 60 * 1000);

			const newEntry = {
				user_id: userId,
				date: now.toISOString().split('T')[0],
				check_in: checkIn.toISOString(),
				check_out: now.toISOString(),
				total_hours: 8.0,
				notes: 'Sample work day'
			};

			await timeEntriesAPI.create(newEntry);
			loadData();
		} catch (error) {
			console.error('Error creando registro:', error);
		}
	};

	if (loading) {
		return (
			<div className="min-h-screen bg-gray-900 flex items-center justify-center">
				<div className="text-center">
					<div className="animate-spin w-16 h-16 border-4 border-gray-600 border-t-blue-500 rounded-full mx-auto mb-4"></div>
					<p className="text-gray-300 text-xl">Cargando Dashboard...</p>
				</div>
			</div>
		);
	}

	return (
		<div className="min-h-screen bg-gray-900 text-white">
			<div className="p-4 md:p-8">
				<div className="max-w-7xl mx-auto">
					{/* Header */}
					<div className="flex justify-between items-center mb-8">
						<div>
							<h1 className="text-4xl font-bold bg-gradient-to-r from-red-400 to-pink-500 bg-clip-text text-transparent">
								Panel de Administrador
							</h1>
							<p className="text-gray-400 mt-2">Bienvenido, {user.name}</p>
						</div>
						<button
							onClick={logout}
							className="bg-red-600 hover:bg-red-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
						>
							🚪 Cerrar Sesión
						</button>
					</div>

					{/* Navigation */}
					<div className="flex justify-center mb-8">
						<div className="bg-gray-800 border border-gray-700 rounded-xl p-2 flex space-x-2">
							{['dashboard', 'users', 'time-entries'].map((tab) => (
								<button
									key={tab}
									onClick={() => setActiveTab(tab)}
									className={`px-6 py-2 rounded-lg font-medium transition-all ${activeTab === tab
											? 'bg-red-600 text-white shadow-lg'
											: 'text-gray-300 hover:text-white hover:bg-gray-700'
										}`}
								>
									{tab === 'dashboard' && '📊 Dashboard'}
									{tab === 'users' && '👥 Usuarios'}
									{tab === 'time-entries' && '⏰ Registros'}
								</button>
							))}
						</div>
					</div>

					{/* Dashboard Tab */}
					{activeTab === 'dashboard' && status && (
						<div>
							{/* Statistics */}
							<div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
								<div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
									<div className="text-center">
										<div className="text-4xl font-bold text-red-400 mb-2">
											{status.statistics.users}
										</div>
										<div className="text-gray-300">Usuarios Totales</div>
									</div>
								</div>
								<div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
									<div className="text-center">
										<div className="text-4xl font-bold text-green-400 mb-2">
											{status.statistics.time_entries}
										</div>
										<div className="text-gray-300">Registros de Tiempo</div>
									</div>
								</div>
								<div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
									<div className="text-center">
										<div className="text-4xl font-bold text-purple-400 mb-2">
											{status.statistics.absences}
										</div>
										<div className="text-gray-300">Ausencias</div>
									</div>
								</div>
							</div>

							{/* Features */}
							<div className="bg-gray-800 border border-gray-700 rounded-xl p-8">
								<h2 className="text-2xl font-bold mb-6 text-center bg-gradient-to-r from-red-400 to-pink-500 bg-clip-text text-transparent">
									Características del Sistema
								</h2>
								<div className="grid md:grid-cols-2 gap-4">
									{status.features?.map((feature, index) => (
										<div
											key={index}
											className="flex items-center space-x-3 p-4 bg-gray-700/50 rounded-lg"
										>
											<span className="text-green-400">✅</span>
											<span className="text-gray-200">{feature}</span>
										</div>
									))}
								</div>
							</div>
						</div>
					)}

					{/* Users Tab */}
					{activeTab === 'users' && (
						<div className="bg-gray-800 border border-gray-700 rounded-xl p-8">
							<div className="flex justify-between items-center mb-8">
								<h2 className="text-2xl font-bold text-white">Gestión de Usuarios</h2>
								<button
									onClick={createSampleUser}
									className="bg-red-600 hover:bg-red-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
								>
									➕ Crear Usuario
								</button>
							</div>

							<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
								{users.map((u) => (
									<div
										key={u.id}
										className="bg-gray-700/70 border border-gray-600 rounded-xl p-6 hover:bg-gray-700 transition-all"
									>
										<div className="text-center">
											<div className="w-16 h-16 bg-gradient-to-br from-red-500 to-pink-600 rounded-full flex items-center justify-center mx-auto mb-4">
												<span className="text-white font-bold text-2xl">
													{u.name.charAt(0)}
												</span>
											</div>
											<h3 className="font-bold text-lg mb-1">{u.name}</h3>
											<p className="text-gray-400 text-sm mb-2">{u.email}</p>
											<p className="text-gray-500 text-xs mb-4">{u.department}</p>
											<span
												className={`inline-block px-4 py-2 text-xs font-bold rounded-full ${u.role === 'admin'
														? 'bg-red-600 text-red-100'
														: u.role === 'manager'
															? 'bg-blue-600 text-blue-100'
															: 'bg-green-600 text-green-100'
													}`}
											>
												{u.role.toUpperCase()}
											</span>
											<div className="mt-4">
												<button
													onClick={() => createSampleTimeEntry(u.id)}
													className="text-xs bg-gray-600 hover:bg-gray-500 text-white px-3 py-2 rounded-lg"
												>
													⏰ Crear Registro
												</button>
											</div>
										</div>
									</div>
								))}
							</div>
						</div>
					)}

					{/* Time Entries Tab */}
					{activeTab === 'time-entries' && (
						<div className="bg-gray-800 border border-gray-700 rounded-xl p-8">
							<h2 className="text-2xl font-bold mb-8 text-center text-white">
								Registros de Tiempo
							</h2>

							<div className="space-y-4">
								{timeEntries.slice(0, 10).map((entry) => {
									const entryUser = users.find((u) => u.id === entry.user_id);
									return (
										<div
											key={entry.id}
											className="bg-gray-700/50 border border-gray-600 rounded-lg p-6"
										>
											<div className="flex justify-between items-start">
												<div className="flex items-center space-x-4">
													<div className="w-12 h-12 bg-gradient-to-br from-green-500 to-blue-600 rounded-full flex items-center justify-center">
														<span className="text-white font-bold">
															{entryUser ? entryUser.name.charAt(0) : '?'}
														</span>
													</div>
													<div>
														<h3 className="font-semibold text-white">
															{entryUser ? entryUser.name : 'Usuario desconocido'}
														</h3>
														<p className="text-gray-400 text-sm">{entry.date}</p>
													</div>
												</div>
												<div className="text-right">
													<div className="text-2xl font-bold text-green-400">
														{entry.total_hours ? `${entry.total_hours}h` : 'En curso'}
													</div>
												</div>
											</div>
										</div>
									);
								})}
							</div>
						</div>
					)}
				</div>
			</div>
		</div>
	);
}

export default AdminDashboard;