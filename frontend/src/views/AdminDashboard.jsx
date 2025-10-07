import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { usersAPI, timeEntriesAPI, statusAPI } from '../services/api';
import {
	formatLocalDateTime,
	calculateDuration,
	formatForDateTimeInput,
	dateTimeInputToISO,
	calculateTotalHours
} from '../utils/timeUtils';

function AdminDashboard() {
	const { user, logout } = useAuth();
	const [users, setUsers] = useState([]);
	const [timeEntries, setTimeEntries] = useState([]);
	const [status, setStatus] = useState(null);
	const [activeTab, setActiveTab] = useState('dashboard');
	const [loading, setLoading] = useState(true);

	// Estados para edición de registros
	const [editingEntry, setEditingEntry] = useState(null);
	const [editCheckIn, setEditCheckIn] = useState('');
	const [editCheckOut, setEditCheckOut] = useState('');

	// Estados para crear usuario
	const [showCreateUser, setShowCreateUser] = useState(false);
	const [newUserName, setNewUserName] = useState('');
	const [newUserEmail, setNewUserEmail] = useState('');
	const [newUserPassword, setNewUserPassword] = useState('');
	const [newUserRole, setNewUserRole] = useState('worker');
	const [newUserDepartment, setNewUserDepartment] = useState('');

	// Estados para editar usuario
	const [editingUser, setEditingUser] = useState(null);
	const [editUserName, setEditUserName] = useState('');
	const [editUserEmail, setEditUserEmail] = useState('');
	const [editUserPassword, setEditUserPassword] = useState('');
	const [editUserRole, setEditUserRole] = useState('worker');
	const [editUserDepartment, setEditUserDepartment] = useState('');

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
			
			// Ordenar registros por fecha de entrada (más reciente primero)
			const sortedEntries = entriesRes.data.time_entries.sort((a, b) => {
				return new Date(b.check_in) - new Date(a.check_in);
			});
			setTimeEntries(sortedEntries);
			
			setStatus(statusRes.data);
		} catch (error) {
			console.error('Error cargando datos:', error);
		}
		setLoading(false);
	};

	// Funciones para edición de registros de tiempo
	const startEditEntry = (entry) => {
		setEditingEntry(entry.id);
		setEditCheckIn(formatForDateTimeInput(entry.check_in));
		setEditCheckOut(entry.check_out ? formatForDateTimeInput(entry.check_out) : '');
	};

	const saveEditEntry = async () => {
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

	const cancelEditEntry = () => {
		setEditingEntry(null);
		setEditCheckIn('');
		setEditCheckOut('');
	};

	const handleDeleteEntry = async (entryId) => {
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

	// Funciones para usuarios
	const handleCreateUser = async () => {
		if (!newUserName || !newUserEmail || !newUserPassword || !newUserDepartment) {
			alert('Completa todos los campos');
			return;
		}

		try {
			await usersAPI.create({
				name: newUserName,
				email: newUserEmail,
				password: newUserPassword,
				role: newUserRole,
				department: newUserDepartment
			});

			setNewUserName('');
			setNewUserEmail('');
			setNewUserPassword('');
			setNewUserRole('worker');
			setNewUserDepartment('');
			setShowCreateUser(false);
			await loadData();
			alert('Usuario creado exitosamente');
		} catch (error) {
			console.error('Error creando usuario:', error);
			alert(error.response?.data?.message || 'Error al crear usuario');
		}
	};

	const startEditUser = (u) => {
		setEditingUser(u.id);
		setEditUserName(u.name);
		setEditUserEmail(u.email);
		setEditUserPassword('');
		setEditUserRole(u.role);
		setEditUserDepartment(u.department);
	};

	const saveEditUser = async () => {
		try {
			const updateData = {
				name: editUserName,
				email: editUserEmail,
				role: editUserRole,
				department: editUserDepartment
			};

			if (editUserPassword) {
				updateData.password = editUserPassword;
			}

			await usersAPI.update(editingUser, updateData);

			setEditingUser(null);
			setEditUserPassword('');
			await loadData();
			alert('Usuario actualizado exitosamente');
		} catch (error) {
			console.error('Error actualizando usuario:', error);
			alert(error.response?.data?.message || 'Error al actualizar usuario');
		}
	};

	const cancelEditUser = () => {
		setEditingUser(null);
		setEditUserName('');
		setEditUserEmail('');
		setEditUserPassword('');
		setEditUserRole('worker');
		setEditUserDepartment('');
	};

	const handleDeleteUser = async (userId) => {
		if (confirm('¿Estás seguro de eliminar este usuario? Se eliminarán todos sus registros.')) {
			try {
				await usersAPI.delete(userId);
				await loadData();
				alert('Usuario eliminado exitosamente');
			} catch (error) {
				console.error('Error eliminando usuario:', error);
				alert(error.response?.data?.message || 'Error al eliminar usuario');
			}
		}
	};

	if (loading) {
		return (
			<div className="min-h-screen bg-gray-900 flex items-center justify-center">
				<div className="animate-spin w-16 h-16 border-4 border-gray-600 border-t-red-500 rounded-full"></div>
			</div>
		);
	}

	const getRoleBadgeColor = (role) => {
		switch (role) {
			case 'admin': return 'bg-red-600 text-red-100';
			case 'manager': return 'bg-blue-600 text-blue-100';
			case 'worker': return 'bg-green-600 text-green-100';
			default: return 'bg-gray-600 text-gray-100';
		}
	};

	return (
		<div className="min-h-screen bg-gray-900 text-white p-4 md:p-8">
			<div className="max-w-7xl mx-auto">
				{/* Header */}
				<div className="flex justify-between items-center mb-8">
					<div>
						<h1 className="text-4xl font-bold bg-gradient-to-r from-red-400 to-pink-500 bg-clip-text text-transparent">
							Panel de Administrador
						</h1>
						<p className="text-gray-400 mt-2">Bienvenido, {user.name}</p>
					</div>
					<button onClick={logout} className="bg-red-600 hover:bg-red-700 px-6 py-3 rounded-lg font-medium">
						🚪 Cerrar Sesión
					</button>
				</div>

				{/* Tabs */}
				<div className="flex justify-center mb-8">
					<div className="bg-gray-800 border border-gray-700 rounded-xl p-2 flex space-x-2">
						{['dashboard', 'users', 'records'].map((tab) => (
							<button
								key={tab}
								onClick={() => setActiveTab(tab)}
								className={`px-6 py-2 rounded-lg font-medium ${activeTab === tab ? 'bg-red-600 text-white' : 'text-gray-300 hover:bg-gray-700'
									}`}
							>
								{tab === 'dashboard' && '📊 Dashboard'}
								{tab === 'users' && '👥 Usuarios'}
								{tab === 'records' && '⏰ Registros'}
							</button>
						))}
					</div>
				</div>

				{/* Dashboard Tab */}
				{activeTab === 'dashboard' && status && (
					<div>
						<div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
							<div className="bg-gray-800 border border-gray-700 rounded-xl p-6 text-center">
								<div className="text-4xl font-bold text-red-400 mb-2">{status.statistics.users}</div>
								<div className="text-gray-300">Usuarios Totales</div>
							</div>
							<div className="bg-gray-800 border border-gray-700 rounded-xl p-6 text-center">
								<div className="text-4xl font-bold text-green-400 mb-2">{status.statistics.time_entries}</div>
								<div className="text-gray-300">Registros de Tiempo</div>
							</div>
						</div>

						<div className="bg-gray-800 border border-gray-700 rounded-xl p-8">
							<h2 className="text-2xl font-bold mb-6 text-center">Características del Sistema</h2>
							<div className="grid md:grid-cols-2 gap-4">
								{status.features?.map((feature, index) => (
									<div key={index} className="flex items-center space-x-3 p-4 bg-gray-700/50 rounded-lg">
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
						<div className="flex justify-between items-center mb-6">
							<h2 className="text-2xl font-bold">Gestión de Usuarios</h2>
							<button
								onClick={() => setShowCreateUser(!showCreateUser)}
								className="bg-red-600 hover:bg-red-700 px-6 py-3 rounded-lg font-medium"
							>
								➕ Crear Usuario
							</button>
						</div>

						{/* Formulario de crear usuario */}
						{showCreateUser && (
							<div className="bg-red-900/30 border border-red-700 rounded-xl p-6 mb-6">
								<h3 className="text-lg font-bold mb-4">Nuevo Usuario</h3>
								<div className="grid grid-cols-2 gap-4 mb-4">
									<input
										type="text"
										placeholder="Nombre"
										value={newUserName}
										onChange={(e) => setNewUserName(e.target.value)}
										className="px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
									/>
									<input
										type="email"
										placeholder="Email"
										value={newUserEmail}
										onChange={(e) => setNewUserEmail(e.target.value)}
										className="px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
									/>
									<input
										type="password"
										placeholder="Contraseña"
										value={newUserPassword}
										onChange={(e) => setNewUserPassword(e.target.value)}
										className="px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
									/>
									<input
										type="text"
										placeholder="Departamento"
										value={newUserDepartment}
										onChange={(e) => setNewUserDepartment(e.target.value)}
										className="px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
									/>
									<select
										value={newUserRole}
										onChange={(e) => setNewUserRole(e.target.value)}
										className="px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white col-span-2"
									>
										<option value="worker">Worker</option>
										<option value="manager">Manager</option>
										<option value="admin">Admin</option>
									</select>
								</div>
								<div className="flex gap-2">
									<button onClick={handleCreateUser} className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded-lg">
										Crear
									</button>
									<button onClick={() => setShowCreateUser(false)} className="bg-gray-600 hover:bg-gray-700 px-4 py-2 rounded-lg">
										Cancelar
									</button>
								</div>
							</div>
						)}

						{/* Tabla de usuarios */}
						<div className="overflow-x-auto">
							<table className="w-full">
								<thead>
									<tr className="border-b-2 border-gray-700">
										<th className="text-left py-3 px-4 text-gray-400">Nombre</th>
										<th className="text-left py-3 px-4 text-gray-400">Email</th>
										<th className="text-left py-3 px-4 text-gray-400">Departamento</th>
										<th className="text-left py-3 px-4 text-gray-400">Rol</th>
										<th className="text-left py-3 px-4 text-gray-400">Acciones</th>
									</tr>
								</thead>
								<tbody>
									{users.filter(u => u.id !== user.id).map((u) => {
										const isEditing = editingUser === u.id;

										return (
											<tr key={u.id} className="border-b border-gray-700 hover:bg-gray-700/30">
												<td className="py-3 px-4">
													{isEditing ? (
														<input
															type="text"
															value={editUserName}
															onChange={(e) => setEditUserName(e.target.value)}
															className="px-2 py-1 bg-gray-700 border border-gray-600 rounded text-white w-full"
														/>
													) : (
														<span className="font-semibold">{u.name}</span>
													)}
												</td>
												<td className="py-3 px-4">
													{isEditing ? (
														<input
															type="email"
															value={editUserEmail}
															onChange={(e) => setEditUserEmail(e.target.value)}
															className="px-2 py-1 bg-gray-700 border border-gray-600 rounded text-white w-full"
														/>
													) : (
														<span className="text-gray-300">{u.email}</span>
													)}
												</td>
												<td className="py-3 px-4">
													{isEditing ? (
														<input
															type="text"
															value={editUserDepartment}
															onChange={(e) => setEditUserDepartment(e.target.value)}
															className="px-2 py-1 bg-gray-700 border border-gray-600 rounded text-white w-full"
														/>
													) : (
														<span className="text-gray-300">{u.department}</span>
													)}
												</td>
												<td className="py-3 px-4">
													{isEditing ? (
														<select
															value={editUserRole}
															onChange={(e) => setEditUserRole(e.target.value)}
															className="px-2 py-1 bg-gray-700 border border-gray-600 rounded text-white"
														>
															<option value="worker">Worker</option>
															<option value="manager">Manager</option>
															<option value="admin">Admin</option>
														</select>
													) : (
														<span className={`px-3 py-1 rounded-full text-xs font-bold ${getRoleBadgeColor(u.role)}`}>
															{u.role.toUpperCase()}
														</span>
													)}
												</td>
												<td className="py-3 px-4">
													{isEditing ? (
														<div className="flex flex-col gap-2">
															<input
																type="password"
																value={editUserPassword}
																onChange={(e) => setEditUserPassword(e.target.value)}
																placeholder="Nueva contraseña (opcional)"
																className="px-2 py-1 bg-gray-700 border border-gray-600 rounded text-white text-sm"
															/>
															<div className="flex gap-2">
																<button onClick={saveEditUser} className="p-2 text-green-400 hover:bg-green-900/30 rounded" title="Guardar">
																	✓
																</button>
																<button onClick={cancelEditUser} className="p-2 text-gray-400 hover:bg-gray-700 rounded" title="Cancelar">
																	✕
																</button>
															</div>
														</div>
													) : (
														<div className="flex gap-2">
															<button onClick={() => startEditUser(u)} className="p-2 text-blue-400 hover:bg-blue-900/30 rounded" title="Editar">
																✏️
															</button>
															<button onClick={() => handleDeleteUser(u.id)} className="p-2 text-red-400 hover:bg-red-900/30 rounded" title="Eliminar">
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

				{/* Records Tab */}
				{activeTab === 'records' && (
					<div className="bg-gray-800 border border-gray-700 rounded-xl p-8">
						<h2 className="text-2xl font-bold mb-6">Todos los Registros</h2>
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
									{timeEntries.map((entry) => {
										const entryUser = users.find(u => u.id === entry.user_id);
										const isEditing = editingEntry === entry.id;

										return (
											<tr key={entry.id} className={`border-b border-gray-700 hover:bg-gray-700/30 ${entry.check_out === null ? 'bg-green-900/20' : ''}`}>
												<td className="py-3 px-4 font-semibold">{entryUser?.name || 'Desconocido'}</td>
												<td className="py-3 px-4">
													<span className={`px-2 py-1 rounded-full text-xs font-bold ${getRoleBadgeColor(entryUser?.role)}`}>
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
													{isEditing ? (
														<div className="flex gap-2">
															<button onClick={saveEditEntry} className="p-2 text-green-400 hover:bg-green-900/30 rounded">
																✓
															</button>
															<button onClick={cancelEditEntry} className="p-2 text-gray-400 hover:bg-gray-700 rounded">
																✕
															</button>
														</div>
													) : (
														<div className="flex gap-2">
															<button onClick={() => startEditEntry(entry)} className="p-2 text-blue-400 hover:bg-blue-900/30 rounded">
																✏️
															</button>
															<button onClick={() => handleDeleteEntry(entry.id)} className="p-2 text-red-400 hover:bg-red-900/30 rounded">
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

export default AdminDashboard;