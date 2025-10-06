import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { timeEntriesAPI } from '../services/api';

function WorkerDashboard() {
	const { user, logout } = useAuth();
	const [timeEntries, setTimeEntries] = useState([]);
	const [loading, setLoading] = useState(true);
	const [checkInTime, setCheckInTime] = useState(null);

	useEffect(() => {
		loadData();
	}, []);

	const loadData = async () => {
		setLoading(true);
		try {
			const entriesRes = await timeEntriesAPI.getAll();
			setTimeEntries(entriesRes.data.time_entries);
		} catch (error) {
			console.error('Error cargando datos:', error);
		}
		setLoading(false);
	};

	const handleCheckIn = async () => {
		try {
			const now = new Date();
			setCheckInTime(now);

			const newEntry = {
				user_id: user.id,
				date: now.toISOString().split('T')[0],
				check_in: now.toISOString(),
				notes: 'Check-in automático'
			};

			await timeEntriesAPI.create(newEntry);
			loadData();
		} catch (error) {
			console.error('Error en check-in:', error);
			alert('Error al registrar entrada');
		}
	};

	const handleCheckOut = async () => {
		try {
			const now = new Date();
			const checkIn = checkInTime || new Date(now.getTime() - 8 * 60 * 60 * 1000);
			const hours = ((now - checkIn) / (1000 * 60 * 60)).toFixed(2);

			const newEntry = {
				user_id: user.id,
				date: now.toISOString().split('T')[0],
				check_in: checkIn.toISOString(),
				check_out: now.toISOString(),
				total_hours: parseFloat(hours),
				notes: 'Check-out automático'
			};

			await timeEntriesAPI.create(newEntry);
			setCheckInTime(null);
			loadData();
		} catch (error) {
			console.error('Error en check-out:', error);
			alert('Error al registrar salida');
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

	const totalHours = timeEntries.reduce((sum, entry) => sum + (entry.total_hours || 0), 0);
	const thisWeekEntries = timeEntries.filter(entry => {
		const entryDate = new Date(entry.date);
		const now = new Date();
		const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
		return entryDate >= weekAgo;
	});

	return (
		<div className="min-h-screen bg-gray-900 text-white">
			<div className="p-4 md:p-8">
				<div className="max-w-7xl mx-auto">
					{/* Header */}
					<div className="flex justify-between items-center mb-8">
						<div>
							<h1 className="text-4xl font-bold bg-gradient-to-r from-green-400 to-emerald-500 bg-clip-text text-transparent">
								Mi Panel de Trabajo
							</h1>
							<p className="text-gray-400 mt-2">
								{user.name} - {user.department}
							</p>
						</div>
						<button
							onClick={logout}
							className="bg-red-600 hover:bg-red-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
						>
							🚪 Cerrar Sesión
						</button>
					</div>

					{/* Check In/Out Section */}
					<div className="bg-gradient-to-br from-blue-900 to-purple-900 border border-blue-700 rounded-2xl p-8 mb-8 shadow-2xl">
						<h2 className="text-2xl font-bold mb-6 text-center">Registro de Jornada</h2>

						<div className="flex flex-col md:flex-row gap-4 justify-center items-center">
							<button
								onClick={handleCheckIn}
								disabled={checkInTime !== null}
								className={`px-8 py-4 rounded-xl font-bold text-lg transition-all transform ${checkInTime
										? 'bg-gray-600 cursor-not-allowed'
										: 'bg-green-600 hover:bg-green-700 hover:scale-105 shadow-lg'
									}`}
							>
								✅ Marcar Entrada
							</button>

							<button
								onClick={handleCheckOut}
								className="px-8 py-4 bg-red-600 hover:bg-red-700 rounded-xl font-bold text-lg transition-all transform hover:scale-105 shadow-lg"
							>
								🚪 Marcar Salida
							</button>
						</div>

						{checkInTime && (
							<div className="mt-6 text-center">
								<div className="bg-green-900/50 border border-green-600 rounded-lg p-4 inline-block">
									<p className="text-green-300">
										✅ Entrada registrada: {checkInTime.toLocaleTimeString()}
									</p>
								</div>
							</div>
						)}
					</div>

					{/* Statistics */}
					<div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
						<div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
							<div className="text-center">
								<div className="text-4xl font-bold text-green-400 mb-2">
									{totalHours.toFixed(1)}h
								</div>
								<div className="text-gray-300">Horas Totales</div>
							</div>
						</div>
						<div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
							<div className="text-center">
								<div className="text-4xl font-bold text-blue-400 mb-2">
									{thisWeekEntries.length}
								</div>
								<div className="text-gray-300">Días Esta Semana</div>
							</div>
						</div>
						<div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
							<div className="text-center">
								<div className="text-4xl font-bold text-purple-400 mb-2">
									{timeEntries.length}
								</div>
								<div className="text-gray-300">Registros Totales</div>
							</div>
						</div>
					</div>

					{/* My Time Entries */}
					<div className="bg-gray-800 border border-gray-700 rounded-xl p-8">
						<h2 className="text-2xl font-bold mb-8 text-center text-white">
							Mi Historial de Tiempo
						</h2>

						{timeEntries.length === 0 ? (
							<div className="text-center py-12">
								<div className="text-6xl mb-4">⏰</div>
								<h3 className="text-xl font-semibold text-gray-300 mb-2">
									Aún no tienes registros
								</h3>
								<p className="text-gray-500">
									Usa los botones de arriba para marcar tu entrada y salida
								</p>
							</div>
						) : (
							<div className="space-y-4">
								{timeEntries.slice(0, 10).map((entry) => (
									<div
										key={entry.id}
										className="bg-gray-700/50 border border-gray-600 rounded-lg p-6 hover:bg-gray-700 transition-colors"
									>
										<div className="flex justify-between items-start">
											<div>
												<h3 className="font-semibold text-white text-lg mb-2">
													📅 {entry.date}
												</h3>
												<div className="text-gray-400 text-sm space-y-1">
													{entry.check_in && (
														<div>✅ Entrada: {new Date(entry.check_in).toLocaleTimeString()}</div>
													)}
													{entry.check_out && (
														<div>🚪 Salida: {new Date(entry.check_out).toLocaleTimeString()}</div>
													)}
												</div>
											</div>
											<div className="text-right">
												<div className="text-3xl font-bold text-green-400">
													{entry.total_hours ? `${entry.total_hours}h` : '⏳'}
												</div>
											</div>
										</div>
										{entry.notes && (
											<div className="mt-4 p-3 bg-gray-800/50 rounded-lg">
												<p className="text-gray-300 text-sm">📝 {entry.notes}</p>
											</div>
										)}
									</div>
								))}
							</div>
						)}
					</div>
				</div>
			</div>
		</div>
	);
}

export default WorkerDashboard;