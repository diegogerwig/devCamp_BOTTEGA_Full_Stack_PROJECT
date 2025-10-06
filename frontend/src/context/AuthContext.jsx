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

		console.log('🔍 checkAuth - Token:', token ? 'Existe' : 'No existe');
		console.log('🔍 checkAuth - User:', savedUser ? 'Existe' : 'No existe');

		if (token && savedUser) {
			try {
				// Primero establecer el usuario del localStorage
				const parsedUser = JSON.parse(savedUser);
				setUser(parsedUser);
				setIsAuthenticated(true);
				console.log('✅ Usuario cargado desde localStorage:', parsedUser);

				// Luego verificar con el backend (sin bloquear la UI)
				try {
					const response = await authAPI.getCurrentUser();
					console.log('✅ Usuario verificado con backend:', response.data.user);
					setUser(response.data.user);
				} catch (verifyError) {
					console.warn('⚠️ No se pudo verificar con backend, pero token existe');
					// No hacer logout aquí, dejar que el usuario use la app
				}
			} catch (error) {
				console.error('❌ Error parseando usuario de localStorage:', error);
				logout();
			}
		} else {
			console.log('❌ No hay token o usuario guardado');
		}

		setLoading(false);
	};

	const login = async (email, password) => {
		try {
			console.log('🔄 Llamando a API de login...');
			const response = await authAPI.login(email, password);
			console.log('📦 Respuesta completa del servidor:', response);
			console.log('📦 response.data:', response.data);

			const { access_token, user } = response.data;

			if (!access_token || !user) {
				console.error('❌ Respuesta incompleta:', { access_token, user });
				throw new Error('Respuesta del servidor incompleta');
			}

			console.log('💾 Guardando token en localStorage');
			localStorage.setItem('token', access_token);

			console.log('💾 Guardando usuario en localStorage');
			localStorage.setItem('user', JSON.stringify(user));

			console.log('✅ Verificando que se guardó:');
			console.log('   - Token guardado:', localStorage.getItem('token') ? 'SÍ' : 'NO');
			console.log('   - User guardado:', localStorage.getItem('user') ? 'SÍ' : 'NO');

			console.log('🔄 Actualizando estado de React');
			setUser(user);
			setIsAuthenticated(true);

			console.log('🎉 Login completado exitosamente');
			console.log('👤 Usuario actual:', user);

			return { success: true, user };
		} catch (error) {
			console.error('❌ Error en login:', error);
			console.error('📄 Detalles del error:', error.response?.data);
			console.error('📄 Status code:', error.response?.status);
			return {
				success: false,
				message: error.response?.data?.message || error.message || 'Error al iniciar sesión'
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