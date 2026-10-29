import React, { useState } from 'react';
import { Settings as SettingsIcon, Shield, Key, Bell, Database, Check } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

const SettingsPage = () => {
  const { user } = useAuth();
  const [currPassword, setCurrPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [msg, setMsg] = useState('');

  const handlePasswordChange = async (e) => {
    e.preventDefault();
    try {
      await api.post('/auth/change-password', {
        current_password: currPassword,
        new_password: newPassword
      });
      setMsg('Password updated successfully');
      setCurrPassword('');
      setNewPassword('');
    } catch (e) {
      alert("Error updating password: " + (e.response?.data?.detail || e.message));
    }
  };

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Page Header */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 tracking-tight">System Configuration & Governance Settings</h2>
        <p className="text-xs text-gray-500 mt-1">
          Review statutory thresholds, active user credentials, and platform security settings.
        </p>
      </div>

      {/* Profile Card */}
      <div className="bg-white p-5 rounded-lg border border-gray-200 space-y-4">
        <h3 className="text-sm font-semibold text-gray-900">Current User Identity</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
          <div>
            <span className="text-gray-400 block uppercase text-[10px]">Full Name</span>
            <span className="font-semibold text-gray-800">{user?.full_name || 'Safety Officer'}</span>
          </div>
          <div>
            <span className="text-gray-400 block uppercase text-[10px]">Email</span>
            <span className="font-mono text-gray-800">{user?.email || 'safety@coalmine.gov'}</span>
          </div>
          <div>
            <span className="text-gray-400 block uppercase text-[10px]">Assigned Role</span>
            <span className="font-medium text-blue-600">{user?.role || 'Safety Officer'}</span>
          </div>
          <div>
            <span className="text-gray-400 block uppercase text-[10px]">Department</span>
            <span className="text-gray-800">{user?.department || 'DGMS Safety Directorate'}</span>
          </div>
        </div>
      </div>

      {/* DGMS Statutory Thresholds Reference */}
      <div className="bg-white p-5 rounded-lg border border-gray-200 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-gray-900">DGMS Mining Safety Standard Thresholds (Circular 2024-26)</h3>
          <span className="text-[10px] bg-green-50 text-green-700 px-2 py-0.5 rounded border border-green-200">Enforced</span>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-xs">
          <div className="p-3 bg-gray-50 rounded border border-gray-100">
            <span className="text-gray-500 block text-[11px]">Methane (CH4) Advisory Limit</span>
            <span className="font-semibold text-gray-900 text-sm">0.75%</span>
            <span className="text-[10px] text-red-600 block mt-0.5">Evacuation: &ge; 1.25%</span>
          </div>
          <div className="p-3 bg-gray-50 rounded border border-gray-100">
            <span className="text-gray-500 block text-[11px]">Carbon Monoxide (CO) Safe Limit</span>
            <span className="font-semibold text-gray-900 text-sm">25.0 PPM</span>
            <span className="text-[10px] text-red-600 block mt-0.5">Danger: &ge; 50.0 PPM</span>
          </div>
          <div className="p-3 bg-gray-50 rounded border border-gray-100">
            <span className="text-gray-500 block text-[11px]">Minimum Oxygen (O2)</span>
            <span className="font-semibold text-gray-900 text-sm">19.5%</span>
            <span className="text-[10px] text-gray-400 block mt-0.5">Standard air: 20.9%</span>
          </div>
          <div className="p-3 bg-gray-50 rounded border border-gray-100">
            <span className="text-gray-500 block text-[11px]">Minimum Ventilation Airflow</span>
            <span className="font-semibold text-gray-900 text-sm">0.5 m/s</span>
            <span className="text-[10px] text-red-600 block mt-0.5">Critical: &lt; 0.3 m/s</span>
          </div>
          <div className="p-3 bg-gray-50 rounded border border-gray-100">
            <span className="text-gray-500 block text-[11px]">Maximum Ambient Temp</span>
            <span className="font-semibold text-gray-900 text-sm">33.0°C</span>
            <span className="text-[10px] text-red-600 block mt-0.5">Heat Stress: &ge; 38.0°C</span>
          </div>
          <div className="p-3 bg-gray-50 rounded border border-gray-100">
            <span className="text-gray-500 block text-[11px]">Machinery Vibration Limit</span>
            <span className="font-semibold text-gray-900 text-sm">7.5 mm/s</span>
            <span className="text-[10px] text-red-600 block mt-0.5">Fault: &ge; 12.0 mm/s</span>
          </div>
        </div>
      </div>

      {/* Password Change Form */}
      <div className="bg-white p-5 rounded-lg border border-gray-200">
        <h3 className="text-sm font-semibold text-gray-900 mb-3">Security & Password Management</h3>
        {msg && <p className="text-xs text-green-600 font-medium mb-3">{msg}</p>}
        <form onSubmit={handlePasswordChange} className="space-y-3 max-w-sm text-xs">
          <div>
            <label className="block text-gray-700 mb-1">Current Password</label>
            <input
              type="password"
              required
              value={currPassword}
              onChange={(e) => setCurrPassword(e.target.value)}
              className="w-full text-xs rounded border border-gray-300 p-2"
            />
          </div>
          <div>
            <label className="block text-gray-700 mb-1">New Secure Password</label>
            <input
              type="password"
              required
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              className="w-full text-xs rounded border border-gray-300 p-2"
            />
          </div>
          <button
            type="submit"
            className="px-3.5 py-1.5 rounded bg-blue-600 text-white hover:bg-blue-700 font-medium"
          >
            Update Password
          </button>
        </form>
      </div>
    </div>
  );
};

export default SettingsPage;

