import React, { createContext, useState, useContext, useEffect } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext();

export const useAuth = () => {
	const context = useContext(AuthContext);
	if (!context) {
		throw new Error('useAuth debe ser usado dentro de un AuthProvider');
	}
	return context;
};

export const AuthProvider = ({ children }) => {
	const [user, setUser] = useState(null);
	const [loading, setLoading] = useState(true);
	const [isAuthenticated, setIsAuthenticated] = useState(false);

	useEffect(() => {
		checkAuth();
	}, []);

	const checkAuth = async () => {
		const token = localStorage.getItem('token');
		const savedUser = localStorage.getItem('user');

		if (token && savedUser) {
			try {
				const response = await authAPI.getCurrentUser();
				setUser(response.data.user);
				setIsAuthenticated(true);
			} catch (error) {
				console.error('Error verificando autenticación:', error);
				logout();
			}
		}
		setLoading(false);
	};

	const login = async (email, password) => {
		try {
			const response = await authAPI.login(email, password);
			const { access_token, user } = response.data;

			localStorage.setItem('token', access_token);
			localStorage.setItem('user', JSON.stringify(user));

			setUser(user);
			setIsAuthenticated(true);

			return { success: true, user };
		} catch (error) {
			console.error('Error en login:', error);
			return {
				success: false,
				message: error.response?.data?.message || 'Error al iniciar sesión'
			};
		}
	};

	const logout = () => {
		localStorage.removeItem('token');
		localStorage.removeItem('user');
		setUser(null);
		setIsAuthenticated(false);
	};

	const value = {
		user,
		loading,
		isAuthenticated,
		login,
		logout
	};

	return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};