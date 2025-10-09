import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { timeEntriesAPI } from '../services/api';
import {
	formatLocalDateTime,
	calculateDuration,
	getCurrentLocalDateTime,
	getCurrentLocalDate,
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
			
			// Sort by check-in date and time (most recent first)
			myEntries.sort((a, b) => {
				const dateCompare = new Date(b.check_in) - new Date(a.check_in);
				return dateCompare;
			});
			
			setTimeEntries(myEntries);

			// Check if there is ONE OPEN RECORD (without check_out) from ANY date
			const open = myEntries.find(e => e.check_out === null);
			setHasOpenEntry(!!open);
			setOpenEntry(open || null);
			
			if (open) {
				console.log('📌 Open record found:', {
					id: open.id,
					date: open.date,
					check_in: open.check_in
				});
			} else {
				console.log('✅ No open records');
			}
		} catch (error) {
			console.error('Error loading data:', error);
			alert(error.response?.data?.message || 'Error loading data');
		}
		setLoading(false);
	};

	const handleCheckIn = async () => {
		if (hasOpenEntry) {
			alert(`You already have an open record from ${openEntry.date} at ${formatLocalDateTime(openEntry.check_in)}. You must close it before opening a new one.`);
			return;
		}

		try {
			const now = getCurrentLocalDateTime();
			const today = getCurrentLocalDate();

			const newEntry = {
				user_id: user.id,
				date: today,
				check_in: now,
				check_out: null,
				total_hours: null,
				notes: 'Check-in record'
			};

			console.log('✅ Creating new record:', newEntry);
			const response = await timeEntriesAPI.create(newEntry);
			console.log('✅ Successful check-in:', response.data);
			await loadData();
		} catch (error) {
			console.error('❌ Check-in error:', error);
			console.error('📄 Error response:', error.response?.data);
			alert(error.response?.data?.message || 'Error registering check-in');
		}
	};

	const handleCheckOut = async () => {
		if (!hasOpenEntry || !openEntry) {
			alert('You do not have an open record');
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
				notes: openEntry.notes || 'Record completed'
			};

			console.log('✅ Closing record:', updatedEntry);
			const response = await timeEntriesAPI.create(updatedEntry);
			console.log('✅ Successful check-out:', response.data);
			await loadData();
		} catch (error) {
			console.error('❌ Check-out error:', error);
			console.error('📄 Error response:', error.response?.data);
			alert(error.response?.data?.message || 'Error registering check-out');
		}
	};

	if (loading) {
		return (
			<div className="min-h-screen bg-gray-900 flex items-center justify-center">
				<div className="text-center">
					<div className="animate-spin w-16 h-16 border-4 border-gray-600 border-t-blue-500 rounded-full mx-auto mb-4"></div>
					<p className="text-gray-300 text-xl">Loading Dashboard...</p>
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
								My Work Dashboard
							</h1>
							<p className="text-gray-400 mt-2">
								{user.name} - {user.department}
							</p>
						</div>
						<button
							onClick={logout}
							className="bg-red-600 hover:bg-red-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
						>
							🚪 Log Out
						</button>
					</div>

					{/* Check In/Out Section */}
					<div className="bg-gradient-to-br from-blue-900 to-purple-900 border border-blue-700 rounded-2xl p-8 mb-8 shadow-2xl">
						<h2 className="text-2xl font-bold mb-6 text-center">Shift Record</h2>

						<div className="flex flex-col md:flex-row gap-4 justify-center items-center">
							<button
								onClick={handleCheckIn}
								disabled={hasOpenEntry}
								className={`px-8 py-4 rounded-xl font-bold text-lg transition-all transform ${hasOpenEntry
									? 'bg-gray-600 cursor-not-allowed opacity-50'
									: 'bg-green-600 hover:bg-green-700 hover:scale-105 shadow-lg'
									}`}
							>
								✅ Check In
							</button>

							<button
								onClick={handleCheckOut}
								disabled={!hasOpenEntry}
								className={`px-8 py-4 rounded-xl font-bold text-lg transition-all transform ${!hasOpenEntry
									? 'bg-gray-600 cursor-not-allowed opacity-50'
									: 'bg-red-600 hover:bg-red-700 hover:scale-105 shadow-lg'
									}`}
							>
								🚪 Check Out
							</button>
						</div>

						{hasOpenEntry && openEntry && (
							<div className="mt-6 text-center">
								<div className="bg-green-900/50 border border-green-600 rounded-lg p-4 inline-block">
									<p className="text-green-300 mb-2">
										✅ You have an active shift
									</p>
									<p className="text-green-200 text-sm">
										Date: {openEntry.date}
									</p>
									<p className="text-green-200 text-sm">
										Check In: {formatLocalDateTime(openEntry.check_in)}
									</p>
									<p className="text-green-200 text-sm font-bold mt-2">
										Elapsed Time: {calculateDuration(openEntry.check_in, null)}
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
								<div className="text-gray-300">Total Hours</div>
							</div>
						</div>
						<div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
							<div className="text-center">
								<div className="text-4xl font-bold text-blue-400 mb-2">
									{timeEntries.filter(e => e.check_out !== null).length}
								</div>
								<div className="text-gray-300">Completed Records</div>
							</div>
						</div>
						<div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
							<div className="text-center">
								<div className="text-4xl font-bold text-purple-400 mb-2">
									{timeEntries.length}
								</div>
								<div className="text-gray-300">Total Records</div>
							</div>
						</div>
					</div>

					{/* My Time Entries */}
					<div className="bg-gray-800 border border-gray-700 rounded-xl p-8">
						<h2 className="text-2xl font-bold mb-8 text-center text-white">
							My Time History
						</h2>

						{timeEntries.length === 0 ? (
							<div className="text-center py-12">
								<div className="text-6xl mb-4">⏰</div>
								<h3 className="text-xl font-semibold text-gray-300 mb-2">
									You don't have records yet
								</h3>
								<p className="text-gray-500">
									Use the buttons above to mark your check-in and check-out
								</p>
							</div>
						) : (
							<div className="overflow-x-auto">
								<table className="w-full">
									<thead>
										<tr className="border-b-2 border-gray-700">
											<th className="text-left py-3 px-4 text-gray-400 font-semibold">Date</th>
											<th className="text-left py-3 px-4 text-gray-400 font-semibold">Check In</th>
											<th className="text-left py-3 px-4 text-gray-400 font-semibold">Check Out</th>
											<th className="text-left py-3 px-4 text-gray-400 font-semibold">Duration</th>
											<th className="text-left py-3 px-4 text-gray-400 font-semibold">Status</th>
										</tr>
									</thead>
									<tbody>
										{timeEntries.map((entry) => (
											<tr key={entry.id} className={`border-b border-gray-700 hover:bg-gray-700/30 ${entry.check_out === null ? 'bg-green-900/20' : ''}`}>
												<td className="py-3 px-4">{entry.date}</td>
												<td className="py-3 px-4">{formatLocalDateTime(entry.check_in)}</td>
												<td className="py-3 px-4">
													{entry.check_out ? (
														formatLocalDateTime(entry.check_out)
													) : (
														<span className="text-green-400 font-semibold">In Progress</span>
													)}
												</td>
												<td className="py-3 px-4 font-bold text-green-400">
													{calculateDuration(entry.check_in, entry.check_out)}
												</td>
												<td className="py-3 px-4">
													{entry.check_out === null ? (
														<span className="px-3 py-1 bg-green-600 text-green-100 rounded-full text-xs font-bold">
															ACTIVE
														</span>
													) : (
														<span className="px-3 py-1 bg-gray-600 text-gray-200 rounded-full text-xs font-bold">
															CLOSED
														</span>
													)}
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