import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { timeEntriesAPI } from '../services/api';
import {
	formatLocalDateTime,
	calculateDuration,
	getCurrentLocalDateTime,
	calculateTotalHours
} from '../utils/timeUtils';

function WorkerDashboard() {
	const { user, logout } = useAuth();
	const [timeEntries, setTimeEntries] = useState([]);
	const [loading, setLoading] = useState(true);
	const [hasOpenEntry, setHasOpenEntry] = useState(false);
	const [openEntry, setOpenEntry] = useState(null);

	useEffect(() => {
		loadData();
	}, []);

	const loadData = async () => {
		setLoading(true);
		try {
			const entriesRes = await timeEntriesAPI.getAll();
			const myEntries = entriesRes.data.time_entries.filter(e => e.user_id === user.id);
			setTimeEntries(myEntries);

			// Verificar si hay un registro abierto
			const open = myEntries.find(e => e.check_out === null);
			setHasOpenEntry(!!open);
			setOpenEntry(open || null);
		} catch (error) {
			console.error('Error cargando datos:', error);
		}
		setLoading(false);
	};

	const handleCheckIn = async () => {
		if (hasOpenEntry) {
			alert('Ya tienes un registro abierto');
			return;
		}

		try {
			const now = getCurrentLocalDateTime();

			const newEntry = {
				user_id: user.id,
				date: now.split('T')[0],
				check_in: now,
				check_out: null,
				total_hours: null,
				notes: 'Registro de entrada'
			};

			await timeEntriesAPI.create(newEntry);
			await loadData();
		} catch (error) {
			console.error('Error en check-in:', error);
			alert('Error al registrar entrada');
		}
	};

	const handleCheckOut = async () => {
		if (!hasOpenEntry || !openEntry) {
			alert('No tienes un registro abierto');
			return;
		}

		try {
			const now = getCurrentLocalDateTime();
			const totalHours = parseFloat(calculateTotalHours(openEntry.check_in, now));

			const updatedEntry = {
				user_id: user.id,
				date: openEntry.date,
				check_in: openEntry.check_in,
				check_out: now,
				total_hours: totalHours,
				notes: openEntry.notes || 'Registro completado'
			};

			await timeEntriesAPI.create(updatedEntry);
			await loadData();
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
								disabled={hasOpenEntry}
								className={`px-8 py-4 rounded-xl font-bold text-lg transition-all transform ${hasOpenEntry
										? 'bg-gray-600 cursor-not-allowed opacity-50'
										: 'bg-green-600 hover:bg-green-700 hover:scale-105 shadow-lg'
									}`}
							>
								✅ Marcar Entrada
							</button>

							<button
								onClick={handleCheckOut}
								disabled={!hasOpenEntry}
								className={`px-8 py-4 rounded-xl font-bold text-lg transition-all transform ${!hasOpenEntry
										? 'bg-gray-600 cursor-not-allowed opacity-50'
										: 'bg-red-600 hover:bg-red-700 hover:scale-105 shadow-lg'
									}`}
							>
								🚪 Marcar Salida
							</button>
						</div>

						{hasOpenEntry && openEntry && (
							<div className="mt-6 text-center">
								<div className="bg-green-900/50 border border-green-600 rounded-lg p-4 inline-block">
									<p className="text-green-300 mb-2">
										✅ Tienes una jornada activa
									</p>
									<p className="text-green-200 text-sm">
										Entrada: {formatLocalDateTime(openEntry.check_in)}
									</p>
									<p className="text-green-200 text-sm font-bold mt-2">
										Tiempo transcurrido: {calculateDuration(openEntry.check_in, null)}
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
									{timeEntries.filter(e => e.check_out !== null).length}
								</div>
								<div className="text-gray-300">Días Completados</div>
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
							<div className="overflow-x-auto">
								<table className="w-full">
									<thead>
										<tr className="border-b-2 border-gray-700">
											<th className="text-left py-3 px-4 text-gray-400 font-semibold">Fecha</th>
											<th className="text-left py-3 px-4 text-gray-400 font-semibold">Entrada</th>
											<th className="text-left py-3 px-4 text-gray-400 font-semibold">Salida</th>
											<th className="text-left py-3 px-4 text-gray-400 font-semibold">Duración</th>
										</tr>
									</thead>
									<tbody>
										{timeEntries.map((entry) => (
											<tr key={entry.id} className="border-b border-gray-700 hover:bg-gray-700/30">
												<td className="py-3 px-4">{entry.date}</td>
												<td className="py-3 px-4">{formatLocalDateTime(entry.check_in)}</td>
												<td className="py-3 px-4">
													{entry.check_out ? (
														formatLocalDateTime(entry.check_out)
													) : (
														<span className="text-green-400 font-semibold">En curso</span>
													)}
												</td>
												<td className="py-3 px-4 font-bold text-green-400">
													{calculateDuration(entry.check_in, entry.check_out)}
												</td>
											</tr>
										))}
									</tbody>
								</table>
							</div>
						)}
					</div>
				</div>
			</div>
		</div>
	);
}

export default WorkerDashboard;