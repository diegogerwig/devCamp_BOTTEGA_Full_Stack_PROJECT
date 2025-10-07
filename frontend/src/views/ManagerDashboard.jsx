import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { usersAPI, timeEntriesAPI } from '../services/api';
import {
	formatLocalDateTime,
	calculateDuration,
	getCurrentLocalDateTime,
	getCurrentLocalDate,
	calculateTotalHours,
	formatForDateTimeInput,
	dateTimeInputToISO
} from '../utils/timeUtils';

function ManagerDashboard() {
	const { user, logout } = useAuth();
	const [users, setUsers] = useState([]);
	const [timeEntries, setTimeEntries] = useState([]);
	const [activeTab, setActiveTab] = useState('my-time');
	const [loading, setLoading] = useState(true);
	const [hasOpenEntry, setHasOpenEntry] = useState(false);
	const [openEntry, setOpenEntry] = useState(null);

	// Estados para edición
	const [editingEntry, setEditingEntry] = useState(null);
	const [editCheckIn, setEditCheckIn] = useState('');
	const [editCheckOut, setEditCheckOut] = useState('');

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

			// Verificar si el manager tiene UN registro abierto (de cualquier fecha)
			const myEntries = entriesRes.data.time_entries.filter(e => e.user_id === user.id);
			const open = myEntries.find(e => e.check_out === null);
			setHasOpenEntry(!!open);
			setOpenEntry(open || null);
			
			if (open) {
				console.log('📌 Registro abierto encontrado:', {
					id: open.id,
					date: open.date,
					check_in: open.check_in
				});
			} else {
				console.log('✅ No hay registros abiertos');
			}
		} catch (error) {
			console.error('Error cargando datos:', error);
		}
		setLoading(false);
	};

	const handleCheckIn = async () => {
		if (hasOpenEntry) {
			alert(`Ya tienes un registro abierto desde el ${openEntry.date} a las ${formatLocalDateTime(openEntry.check_in)}. Debes cerrarlo antes de abrir uno nuevo.`);
			return;
		}

		try {
			const now = getCurrentLocalDateTime();
			const today = getCurrentLocalDate();
			
			const response = await timeEntriesAPI.create({
				user_id: user.id,
				date: today,
				check_in: now,
				check_out: null,
				notes: 'Manager check-in'
			});
			console.log('✅ Check-in exitoso:', response.data);
			await loadData();
		} catch (error) {
			console.error('❌ Error en check-in:', error);
			console.error('📄 Error response:', error.response?.data);
			alert(error.response?.data?.message || 'Error al registrar entrada');
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

			const response = await timeEntriesAPI.create({
				user_id: user.id,
				date: openEntry.date,
				check_in: openEntry.check_in,
				check_out: now,
				total_hours: totalHours,
				notes: openEntry.notes
			});
			console.log('✅ Check-out exitoso:', response.data);
			await loadData();
		} catch (error) {
			console.error('❌ Error en check-out:', error);
			console.error('📄 Error response:', error.response?.data);
			alert(error.response?.data?.message || 'Error al registrar salida');
		}
	};

	const startEdit = (entry) => {
		if (entry.user_id === user.id) {
			alert('No puedes editar tus propios registros');
			return;
		}
		setEditingEntry(entry.id);
		setEditCheckIn(formatForDateTimeInput(entry.check_in));
		setEditCheckOut(entry.check_out ? formatForDateTimeInput(entry.check_out) : '');
	};

	const saveEdit = async () => {
		try {
			const checkInISO = dateTimeInputToISO(editCheckIn);
			const checkOutISO = editCheckOut ? dateTimeInputToISO(editCheckOut) : null;
			const totalHours = checkOutISO ? parseFloat(calculateTotalHours(checkInISO, checkOutISO)) : null;

			await timeEntriesAPI.update(editingEntry, {
				check_in: checkInISO,
				check_out: checkOutISO,
				total_hours: totalHours
			});

			setEditingEntry(null);
			await loadData();
		} catch (error) {
			console.error('Error guardando cambios:', error);
			alert(error.response?.data?.message || 'Error al guardar cambios');
		}
	};

	const cancelEdit = () => {
		setEditingEntry(null);
		setEditCheckIn('');
		setEditCheckOut('');
	};

	const handleDeleteEntry = async (entryId, entryUserId) => {
		if (entryUserId === user.id) {
			alert('No puedes eliminar tus propios registros');
			return;
		}

		if (confirm('¿Estás seguro de eliminar este registro?')) {
			try {
				await timeEntriesAPI.delete(entryId);
				await loadData();
			} catch (error) {
				console.error('Error eliminando registro:', error);
				alert(error.response?.data?.message || 'Error al eliminar registro');
			}
		}
	};

	if (loading) {
		return (
			<div className="min-h-screen bg-gray-900 flex items-center justify-center">
				<div className="animate-spin w-16 h-16 border-4 border-gray-600 border-t-blue-500 rounded-full"></div>
			</div>
		);
	}

	// Manager ve todos los usuarios de su departamento (incluyendo él mismo)
	const departmentUsers = users.filter(u => u.department === user.department);
	const departmentWorkers = users.filter(u => u.department === user.department && u.role === 'worker');
	
	// Mostrar todos los registros del departamento (incluyendo los del manager)
	const allDepartmentEntries = timeEntries.filter(e => 
		departmentUsers.some(u => u.id === e.user_id)
	).sort((a, b) => new Date(b.check_in) - new Date(a.check_in));
	
	const myEntries = timeEntries
		.filter(e => e.user_id === user.id)
		.sort((a, b) => new Date(b.check_in) - new Date(a.check_in));

	return (
		<div className="min-h-screen bg-gray-900 text-white p-4 md:p-8">
			<div className="max-w-7xl mx-auto">
				{/* Header */}
				<div className="flex justify-between items-center mb-8">
					<div>
						<h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-cyan-500 bg-clip-text text-transparent">
							Panel de Manager
						</h1>
						<p className="text-gray-400 mt-2">{user.name} - {user.department}</p>
					</div>
					<button onClick={logout} className="bg-red-600 hover:bg-red-700 px-6 py-3 rounded-lg font-medium">
						🚪 Cerrar Sesión
					</button>
				</div>

				{/* Tabs */}
				<div className="flex justify-center mb-8">
					<div className="bg-gray-800 border border-gray-700 rounded-xl p-2 flex space-x-2">
						{['my-time', 'team', 'records'].map((tab) => (
							<button
								key={tab}
								onClick={() => setActiveTab(tab)}
								className={`px-6 py-2 rounded-lg font-medium ${activeTab === tab ? 'bg-blue-600 text-white' : 'text-gray-300 hover:bg-gray-700'
									}`}
							>
								{tab === 'my-time' && '⏰ Mi Jornada'}
								{tab === 'team' && '👥 Mi Equipo'}
								{tab === 'records' && '📊 Registros'}
							</button>
						))}
					</div>
				</div>

				{/* My Time Tab */}
				{activeTab === 'my-time' && (
					<div>
						<div className="bg-gradient-to-br from-blue-900 to-purple-900 border border-blue-700 rounded-2xl p-8 mb-8">
							<h2 className="text-2xl font-bold mb-6 text-center">Mi Registro de Jornada</h2>
							<div className="flex gap-4 justify-center">
								<button
									onClick={handleCheckIn}
									disabled={hasOpenEntry}
									className={`px-8 py-4 rounded-xl font-bold text-lg ${hasOpenEntry ? 'bg-gray-600 cursor-not-allowed opacity-50' : 'bg-green-600 hover:bg-green-700'
										}`}
								>
									✅ Marcar Entrada
								</button>
								<button
									onClick={handleCheckOut}
									disabled={!hasOpenEntry}
									className={`px-8 py-4 rounded-xl font-bold text-lg ${!hasOpenEntry ? 'bg-gray-600 cursor-not-allowed opacity-50' : 'bg-red-600 hover:bg-red-700'
										}`}
								>
									🚪 Marcar Salida
								</button>
							</div>
							{hasOpenEntry && openEntry && (
								<div className="mt-6 text-center">
									<div className="bg-green-900/50 border border-green-600 rounded-lg p-4 inline-block">
										<p className="text-green-300 mb-2">✅ Tienes una jornada activa</p>
										<p className="text-green-200 text-sm">Fecha: {openEntry.date}</p>
										<p className="text-green-200 text-sm">Entrada: {formatLocalDateTime(openEntry.check_in)}</p>
										<p className="text-green-200 text-sm font-bold mt-2">
											Tiempo transcurrido: {calculateDuration(openEntry.check_in, null)}
										</p>
									</div>
								</div>
							)}
						</div>

						<div className="bg-gray-800 border border-gray-700 rounded-xl p-8">
							<h3 className="text-xl font-bold mb-4">Mis Registros</h3>
							<div className="overflow-x-auto">
								<table className="w-full">
									<thead>
										<tr className="border-b-2 border-gray-700">
											<th className="text-left py-3 px-4 text-gray-400">Fecha</th>
											<th className="text-left py-3 px-4 text-gray-400">Entrada</th>
											<th className="text-left py-3 px-4 text-gray-400">Salida</th>
											<th className="text-left py-3 px-4 text-gray-400">Duración</th>
											<th className="text-left py-3 px-4 text-gray-400">Estado</th>
										</tr>
									</thead>
									<tbody>
										{myEntries.map((entry) => (
											<tr key={entry.id} className={`border-b border-gray-700 ${entry.check_out === null ? 'bg-green-900/20' : ''}`}>
												<td className="py-3 px-4">{entry.date}</td>
												<td className="py-3 px-4">{formatLocalDateTime(entry.check_in)}</td>
												<td className="py-3 px-4">
													{entry.check_out ? formatLocalDateTime(entry.check_out) : <span className="text-green-400">En curso</span>}
												</td>
												<td className="py-3 px-4 font-bold">{calculateDuration(entry.check_in, entry.check_out)}</td>
												<td className="py-3 px-4">
													{entry.check_out === null ? (
														<span className="px-3 py-1 bg-green-600 text-green-100 rounded-full text-xs font-bold">
															ACTIVO
														</span>
													) : (
														<span className="px-3 py-1 bg-gray-600 text-gray-200 rounded-full text-xs font-bold">
															CERRADO
														</span>
													)}
												</td>
											</tr>
										))}
									</tbody>
								</table>
							</div>
						</div>
					</div>
				)}

				{/* Team Tab - SOLO MUESTRA WORKERS */}
				{activeTab === 'team' && (
					<div className="bg-gray-800 border border-gray-700 rounded-xl p-8">
						<div className="flex justify-between items-center mb-6">
							<h2 className="text-2xl font-bold">Mi Equipo - Workers</h2>
							<div className="bg-yellow-900/30 border border-yellow-700 rounded-lg px-4 py-2">
								<p className="text-yellow-300 text-sm">
									ℹ️ Solo el Admin puede crear usuarios
								</p>
							</div>
						</div>

						{departmentWorkers.length === 0 ? (
							<div className="text-center py-12">
								<div className="text-6xl mb-4">👥</div>
								<h3 className="text-xl font-semibold text-gray-300 mb-2">
									No hay workers en tu equipo
								</h3>
								<p className="text-gray-500">
									Contacta al administrador para añadir workers a tu departamento
								</p>
							</div>
						) : (
							<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
								{departmentWorkers.map((worker) => (
									<div key={worker.id} className="bg-gray-700/50 border border-gray-600 rounded-xl p-6 text-center">
										<div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-cyan-600 rounded-full flex items-center justify-center mx-auto mb-4">
											<span className="text-white font-bold text-2xl">{worker.name.charAt(0)}</span>
										</div>
										<h3 className="font-bold text-lg mb-1">{worker.name}</h3>
										<p className="text-gray-400 text-sm mb-2">{worker.email}</p>
										<span className="inline-block px-4 py-2 text-xs font-bold rounded-full bg-green-600 text-green-100">
											WORKER
										</span>
									</div>
								))}
							</div>
						)}
					</div>
				)}

				{/* Records Tab - MUESTRA TODOS LOS REGISTROS DEL DEPARTAMENTO */}
				{activeTab === 'records' && (
					<div className="bg-gray-800 border border-gray-700 rounded-xl p-8">
						<h2 className="text-2xl font-bold mb-6">Registros del Departamento</h2>
						<p className="text-gray-400 mb-4">
							Mostrando registros de todos los miembros del departamento {user.department}
						</p>
						<div className="overflow-x-auto">
							<table className="w-full">
								<thead>
									<tr className="border-b-2 border-gray-700">
										<th className="text-left py-3 px-4 text-gray-400">Usuario</th>
										<th className="text-left py-3 px-4 text-gray-400">Rol</th>
										<th className="text-left py-3 px-4 text-gray-400">Fecha</th>
										<th className="text-left py-3 px-4 text-gray-400">Entrada</th>
										<th className="text-left py-3 px-4 text-gray-400">Salida</th>
										<th className="text-left py-3 px-4 text-gray-400">Duración</th>
										<th className="text-left py-3 px-4 text-gray-400">Estado</th>
										<th className="text-left py-3 px-4 text-gray-400">Acciones</th>
									</tr>
								</thead>
								<tbody>
									{allDepartmentEntries.map((entry) => {
										const entryUser = users.find(u => u.id === entry.user_id);
										const isEditing = editingEntry === entry.id;
										const isOwnRecord = entry.user_id === user.id;

										return (
											<tr key={entry.id} className={`border-b border-gray-700 hover:bg-gray-700/30 ${entry.check_out === null ? 'bg-green-900/20' : ''}`}>
												<td className="py-3 px-4">
													<span className="font-semibold">{entryUser?.name || 'Desconocido'}</span>
													{isOwnRecord && (
														<span className="ml-2 text-xs text-blue-400">(Tú)</span>
													)}
												</td>
												<td className="py-3 px-4">
													<span className={`px-2 py-1 rounded-full text-xs font-bold ${
														entryUser?.role === 'manager' ? 'bg-blue-600 text-blue-100' : 'bg-green-600 text-green-100'
													}`}>
														{entryUser?.role?.toUpperCase() || 'N/A'}
													</span>
												</td>
												<td className="py-3 px-4">{entry.date}</td>
												<td className="py-3 px-4">
													{isEditing ? (
														<input
															type="datetime-local"
															value={editCheckIn}
															onChange={(e) => setEditCheckIn(e.target.value)}
															className="px-2 py-1 bg-gray-700 border border-gray-600 rounded text-white text-sm"
														/>
													) : (
														formatLocalDateTime(entry.check_in)
													)}
												</td>
												<td className="py-3 px-4">
													{isEditing ? (
														<input
															type="datetime-local"
															value={editCheckOut}
															onChange={(e) => setEditCheckOut(e.target.value)}
															className="px-2 py-1 bg-gray-700 border border-gray-600 rounded text-white text-sm"
														/>
													) : entry.check_out ? (
														formatLocalDateTime(entry.check_out)
													) : (
														<span className="text-green-400 font-semibold">En curso</span>
													)}
												</td>
												<td className="py-3 px-4 font-bold text-green-400">
													{calculateDuration(entry.check_in, entry.check_out)}
												</td>
												<td className="py-3 px-4">
													{entry.check_out === null ? (
														<span className="px-3 py-1 bg-green-600 text-green-100 rounded-full text-xs font-bold">
															ACTIVO
														</span>
													) : (
														<span className="px-3 py-1 bg-gray-600 text-gray-200 rounded-full text-xs font-bold">
															CERRADO
														</span>
													)}
												</td>
												<td className="py-3 px-4">
													{isOwnRecord ? (
														<span className="text-gray-500 text-sm">No editable</span>
													) : isEditing ? (
														<div className="flex gap-2">
															<button onClick={saveEdit} className="p-2 text-green-400 hover:bg-green-900/30 rounded">
																✓
															</button>
															<button onClick={cancelEdit} className="p-2 text-gray-400 hover:bg-gray-700 rounded">
																✕
															</button>
														</div>
													) : (
														<div className="flex gap-2">
															<button onClick={() => startEdit(entry)} className="p-2 text-blue-400 hover:bg-blue-900/30 rounded">
																✏️
															</button>
															<button onClick={() => handleDeleteEntry(entry.id, entry.user_id)} className="p-2 text-red-400 hover:bg-red-900/30 rounded">
																🗑️
															</button>
														</div>
													)}
												</td>
											</tr>
										);
									})}
								</tbody>
							</table>
						</div>
					</div>
				)}
			</div>
		</div>
	);
}

export default ManagerDashboard;