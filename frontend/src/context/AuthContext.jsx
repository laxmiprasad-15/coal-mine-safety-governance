import React, { createContext, useContext, useState, useEffect } from 'react';
import { loginApi, getMeApi } from '../services/api';

const AuthContext = createContext(null);

export const DEMO_ACCOUNTS = [
  { role: 'Admin', email: 'admin@coalmine.gov', password: 'Admin@123', name: 'Dr. Rajesh Sharma (Director)' },
  { role: 'Safety Officer', email: 'safety@coalmine.gov', password: 'Safety@123', name: 'Vikram Rathore (Safety Officer)' },
  { role: 'Mine Supervisor', email: 'supervisor@coalmine.gov', password: 'Super@123', name: 'Arun Mukherjee (Shift Supervisor)' },
  { role: 'Worker', email: 'worker@coalmine.gov', password: 'Worker@123', name: 'Ramesh Yadav (Drill Operator)' },
  { role: 'Auditor', email: 'auditor@coalmine.gov', password: 'Auditor@123', name: 'Sanjay Deshmukh (DGMS Inspector)' }
];

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('coal_mine_token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUser = async () => {
      const storedToken = localStorage.getItem('coal_mine_token');
      const storedUser = localStorage.getItem('coal_mine_user');
      if (storedToken && storedUser) {
        setUser(JSON.parse(storedUser));
        setToken(storedToken);
      } else {
        // Default to Safety Officer for quick evaluation if not logged in
        await switchDemoRole('Safety Officer');
      }
      setLoading(false);
    };
    fetchUser();
  }, []);

  const login = async (email, password) => {
    try {
      const res = await loginApi(email, password);
      const { access_token, user: userData } = res.data;
      localStorage.setItem('coal_mine_token', access_token);
      localStorage.setItem('coal_mine_user', JSON.stringify(userData));
      setToken(access_token);
      setUser(userData);
      return userData;
    } catch (err) {
      console.error("Login failed:", err);
      throw err;
    }
  };

  const logout = () => {
    localStorage.removeItem('coal_mine_token');
    localStorage.removeItem('coal_mine_user');
    setUser(null);
    setToken(null);
  };

  const switchDemoRole = async (roleName) => {
    const demo = DEMO_ACCOUNTS.find(a => a.role === roleName) || DEMO_ACCOUNTS[1];
    return await login(demo.email, demo.password);
  };

  const hasPermission = (moduleName) => {
    if (!user) return false;
    if (user.role === 'Admin') return true;
    if (user.permissions && user.permissions.includes('all')) return true;
    return true; // Permit view, restrict state mutations based on role
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, login, logout, switchDemoRole, hasPermission }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);

