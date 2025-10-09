import React, { createContext, useState, useContext, useEffect } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext();

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
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

        console.log('🔍 checkAuth - Token:', token ? 'Exists' : 'Does not exist');
        console.log('🔍 checkAuth - User:', savedUser ? 'Exists' : 'Does not exist');

        if (token && savedUser) {
            try {
                // First, set the user from localStorage
                const parsedUser = JSON.parse(savedUser);
                setUser(parsedUser);
                setIsAuthenticated(true);
                console.log('✅ User loaded from localStorage:', parsedUser);

                // Then verify with backend (non-blocking UI)
                try {
                    const response = await authAPI.getCurrentUser();
                    console.log('✅ User verified with backend:', response.data.user);
                    setUser(response.data.user);
                } catch (verifyError) {
                    console.warn('⚠️ Could not verify with backend, but token exists');
                    // Do not logout here, allow user to use the app
                }
            } catch (error) {
                console.error('❌ Error parsing user from localStorage:', error);
                logout();
            }
        } else {
            console.log('❌ No token or saved user found');
        }

        setLoading(false);
    };

    const login = async (email, password) => {
        try {
            console.log('🔄 Calling login API...');
            const response = await authAPI.login(email, password);
            console.log('📦 Full server response:', response);
            console.log('📦 response.data:', response.data);

            const { access_token, user } = response.data;

            if (!access_token || !user) {
                console.error('❌ Incomplete response:', { access_token, user });
                throw new Error('Incomplete server response');
            }

            console.log('💾 Saving token to localStorage');
            localStorage.setItem('token', access_token);

            console.log('💾 Saving user to localStorage');
            localStorage.setItem('user', JSON.stringify(user));

            console.log('✅ Verifying saved data:');
            console.log('   - Token saved:', localStorage.getItem('token') ? 'YES' : 'NO');
            console.log('   - User saved:', localStorage.getItem('user') ? 'YES' : 'NO');

            console.log('🔄 Updating React state');
            setUser(user);
            setIsAuthenticated(true);

            console.log('🎉 Login completed successfully');
            console.log('👤 Current user:', user);

            return { success: true, user };
        } catch (error) {
            console.error('❌ Login error:', error);
            console.error('📄 Error details:', error.response?.data);
            console.error('📄 Status code:', error.response?.status);
            return {
                success: false,
                message: error.response?.data?.message || error.message || 'Login failed'
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