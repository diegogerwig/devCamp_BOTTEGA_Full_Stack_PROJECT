import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { usersAPI, timeEntriesAPI } from '../services/api';

function ManagerDashboard() {
	const { user, logout } = useAuth();
	const [users, setUsers] = useState([]);
	const [timeEntries, setTimeEntries] = useState([]);
	const [activeTab, setActiveTab] = useState('team');
	const [loading, setLoading] = useState(true);

	useEffect(() => {
		loadData();
	}, []);

	const loadData = async () => {
		setLoading(true);
		try {
			const [usersRes, entriesRes] = await Promise.all([
				usersAPI.getAll(),
				timeEntriesAPI.getAll()
			]);

			setUsers(usersRes.data.users);
			setTimeEntries(entriesRes.data.time_entries);
		} catch (error) {
			console.error('Error cargando datos:', error);
		}
		setLoading(false);
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

	const departmentUsers = users.filter(u => u.department === user.department);
	const departmentEntries = timeEntries.filter(e =>
		departmentUsers.some(u => u.id === e.user_id)
	);

	return (
		<div className="min-h-screen bg-gray-900 text-white">
			<div className="p-4 md:p-8">
				<div className="max-w-7xl mx-auto">
					{/* Header */}
					<div className="flex justify-between items-center mb-8">
						<div>
							<h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-cyan-500 bg-clip-text text-transparent">
								Panel de Manager
							</h1>
							<p className="text-gray-400 mt-2">
								{user.name} - Departamento: {user.department}
							</p>
						</div>
						<button
							onClick={logout}
							className="bg-red-600 hover:bg-red-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
						>
							🚪 Cerrar Sesión
						</button>
					</div>

					{/* Statistics */}
					<div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
						<div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
							<div className="text-center">
								<div className="text-4xl font-bold text-blue-400 mb-2">
									{departmentUsers.length}
								</div>
								<div className="text-gray-300">Miembros del Equipo</div>
							</div>
						</div>
						<div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
							<div className="text-center">
								<div className="text-4xl font-bold text-green-400 mb-2">
									{departmentEntries.length}
								</div>
								<div className="text-gray-300">Registros del Departamento</div>
							</div>
						</div>
						<div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
							<div className="text-center">
								<div className="text-4xl font-bold text-purple-400 mb-2">
									{user.department}
								</div>
								<div className="text-gray-300">Tu Departamento</div>
							</div>
						</div>
					</div>

					{/* Navigation */}
					<div className="flex justify-center mb-8">
						<div className="bg-gray-800 border border-gray-700 rounded-xl p-2 flex space-x-2">
							{['team', 'time-entries'].map((tab) => (
								<button
									key={tab}
									onClick={() => setActiveTab(tab)}
									className={`px-6 py-2 rounded-lg font-medium transition-all ${activeTab === tab
											? 'bg-blue-600 text-white shadow-lg'
											: 'text-gray-300 hover:text-white hover:bg-gray-700'
										}`}
								>
									{tab === 'team' && '👥 Mi Equipo'}
									{tab === 'time-entries' && '⏰ Registros del Equipo'}
								</button>
							))}
						</div>
					</div>

					{/* Team Tab */}
					{activeTab === 'team' && (
						<div className="bg-gray-800 border border-gray-700 rounded-xl p-8">
							<h2 className="text-2xl font-bold mb-8 text-center text-white">
								Equipo de {user.department}
							</h2>

							{departmentUsers.length === 0 ? (
								<div className="text-center py-12">
									<div className="text-6xl mb-4">👥</div>
									<h3 className="text-xl font-semibold text-gray-300">
										No hay miembros en tu departamento
									</h3>
								</div>
							) : (
								<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
									{departmentUsers.map((u) => (
										<div
											key={u.id}
											className="bg-gray-700/70 border border-gray-600 rounded-xl p-6 hover:bg-gray-700 transition-all"
										>
											<div className="text-center">
												<div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-cyan-600 rounded-full flex items-center justify-center mx-auto mb-4">
													<span className="text-white font-bold text-2xl">
														{u.name.charAt(0)}
													</span>
												</div>
												<h3 className="font-bold text-lg mb-1">{u.name}</h3>
												<p className="text-gray-400 text-sm mb-2">{u.email}</p>
												<span
													className={`inline-block px-4 py-2 text-xs font-bold rounded-full ${u.role === 'manager'
															? 'bg-blue-600 text-blue-100'
															: 'bg-green-600 text-green-100'
														}`}
												>
													{u.role.toUpperCase()}
												</span>
											</div>
										</div>
									))}
								</div>
							)}
						</div>
					)}

					{/* Time Entries Tab */}
					{activeTab === 'time-entries' && (
						<div className="bg-gray-800 border border-gray-700 rounded-xl p-8">
							<h2 className="text-2xl font-bold mb-8 text-center text-white">
								Registros de Tiempo del Equipo
							</h2>

							{departmentEntries.length === 0 ? (
								<div className="text-center py-12">
									<div className="text-6xl mb-4">⏰</div>
									<h3 className="text-xl font-semibold text-gray-300">
										No hay registros de tiempo del equipo
									</h3>
								</div>
							) : (
								<div className="space-y-4">
									{departmentEntries.slice(0, 10).map((entry) => {
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
								</div>
							)}
						</div>
					)}
				</div>
			</div>
		</div>
	);
}

export default ManagerDashboard;