import React, { useState, useEffect } from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard, Map, HardHat, Activity, TrendingUp,
  FileCheck2, CheckSquare, Users, Wrench, FileText,
  ShieldAlert, Settings, Bell, LogOut, RefreshCw, UserCheck, CheckCircle2, AlertTriangle, AlertCircle
} from 'lucide-react';
import { useAuth, DEMO_ACCOUNTS } from '../context/AuthContext';
import { getNotificationsApi, markNotificationReadApi, markAllNotificationsReadApi, triggerSimulatorPulseApi } from '../services/api';

const navItems = [
  { name: 'Dashboard', path: '/', icon: LayoutDashboard },
  { name: 'Digital Twin', path: '/digital-twin', icon: Map },
  { name: 'PPE Detection', path: '/ppe-detection', icon: HardHat },
  { name: 'Sensor Monitoring', path: '/sensors', icon: Activity },
  { name: 'Risk Forecast', path: '/risk-forecast', icon: TrendingUp },
  { name: 'Compliance Cases', path: '/compliance-cases', icon: FileCheck2 },
  { name: 'Corrective Actions', path: '/actions', icon: CheckSquare },
  { name: 'Workers', path: '/workers', icon: Users },
  { name: 'Equipment', path: '/equipment', icon: Wrench },
  { name: 'Reports', path: '/reports', icon: FileText },
  { name: 'Audit Trail', path: '/audit-trail', icon: ShieldAlert },
  { name: 'Settings', path: '/settings', icon: Settings },
];

const DashboardLayout = () => {
  const { user, logout, switchDemoRole } = useAuth();
  const navigate = useNavigate();
  const [notifications, setNotifications] = useState([]);
  const [showNotifs, setShowNotifs] = useState(false);
  const [pulsing, setPulsing] = useState(false);

  const fetchNotifs = async () => {
    try {
      const res = await getNotificationsApi();
      setNotifications(res.data);
    } catch (e) {
      console.error("Error fetching notifications:", e);
    }
  };

  useEffect(() => {
    fetchNotifs();
    const interval = setInterval(fetchNotifs, 15000);
    return () => clearInterval(interval);
  }, []);

  const unreadCount = notifications.filter(n => !n.is_read).length;

  const handleSimulatePulse = async () => {
    try {
      setPulsing(true);
      await triggerSimulatorPulseApi();
      await fetchNotifs();
      setTimeout(() => setPulsing(false), 800);
    } catch (e) {
      console.error(e);
      setPulsing(false);
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await markAllNotificationsReadApi();
      fetchNotifs();
    } catch (e) {
      console.error(e);
    }
  };

  const handleNotificationClick = async (notif) => {
    if (!notif.is_read) {
      await markNotificationReadApi(notif.id);
      fetchNotifs();
    }
    if (notif.link_url) {
      setShowNotifs(false);
      navigate(notif.link_url);
    }
  };

  return (
    <div className="flex h-screen bg-[#F7F8FA] overflow-hidden">
      {/* Fixed Left Sidebar */}
      <aside className="w-64 bg-[#111827] text-gray-300 flex flex-col flex-shrink-0 z-20">
        <div className="p-4 border-b border-gray-800 flex items-center space-x-3">
          <div className="w-8 h-8 rounded bg-blue-600 flex items-center justify-center text-white font-bold text-sm">
            DT
          </div>
          <div>
            <h1 className="font-semibold text-sm text-white leading-tight">Coal Mine Safety</h1>
            <p className="text-[11px] text-gray-400">Digital Twin & Governance</p>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="flex-1 overflow-y-auto px-2 py-4 space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === '/'}
              className={({ isActive }) =>
                `flex items-center px-3 py-2 text-xs font-medium rounded-md transition-colors ${
                  isActive
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                }`
              }
            >
              <item.icon className="mr-3 h-4 w-4 flex-shrink-0" />
              {item.name}
            </NavLink>
          ))}
        </nav>

        {/* Current Active Mine & Role Footer */}
        <div className="p-3 border-t border-gray-800 text-[11px] text-gray-400">
          <div className="flex items-center justify-between mb-1">
            <span className="font-medium text-gray-200">BCCL Colliery No. 7</span>
            <span className="inline-block w-2 h-2 rounded-full bg-emerald-500" title="System Operational" />
          </div>
          <p className="truncate text-gray-400">DGMS Standard UG-2024</p>
        </div>
      </aside>

      {/* Main Body */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top Header */}
        <header className="h-14 bg-white border-b border-gray-200 flex items-center justify-between px-6 z-10">
          <div className="flex items-center space-x-4">
            <span className="text-xs font-semibold px-2.5 py-1 rounded bg-gray-100 text-gray-700 border border-gray-200">
              Underground Block 4 | Seam III
            </span>
          </div>

          <div className="flex items-center space-x-3">
            {/* Live Simulator Pulse */}
            <button
              onClick={handleSimulatePulse}
              title="Trigger simulated live IoT sensor pulse"
              className="inline-flex items-center text-xs font-medium px-2.5 py-1.5 rounded border border-gray-200 bg-white hover:bg-gray-50 text-gray-700 transition-colors"
            >
              <RefreshCw className={`w-3.5 h-3.5 mr-1.5 text-gray-500 ${pulsing ? 'animate-spin' : ''}`} />
              Pulse Telemetry
            </button>

            {/* Role Switcher for B.Tech Demo Testing */}
            <div className="flex items-center space-x-1.5 bg-gray-50 border border-gray-200 rounded px-2 py-1">
              <UserCheck size={14} className="text-gray-500" />
              <span className="text-xs text-gray-500">Role:</span>
              <select
                value={user?.role || 'Safety Officer'}
                onChange={(e) => switchDemoRole(e.target.value)}
                className="text-xs font-medium bg-transparent border-0 text-gray-900 focus:ring-0 cursor-pointer p-0 pr-1"
              >
                {DEMO_ACCOUNTS.map((a) => (
                  <option key={a.role} value={a.role}>
                    {a.role}
                  </option>
                ))}
              </select>
            </div>

            {/* Notification Dropdown Bell */}
            <div className="relative">
              <button
                onClick={() => setShowNotifs(!showNotifs)}
                className="relative p-1.5 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
              >
                <Bell size={18} />
                {unreadCount > 0 && (
                  <span className="absolute top-1 right-1 w-2 h-2 bg-red-600 rounded-full" />
                )}
              </button>

              {showNotifs && (
                <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg border border-gray-200 shadow-lg py-2 z-50">
                  <div className="flex items-center justify-between px-4 py-2 border-b border-gray-100">
                    <span className="text-xs font-semibold text-gray-800">Safety Alerts ({unreadCount})</span>
                    {unreadCount > 0 && (
                      <button
                        onClick={handleMarkAllRead}
                        className="text-[11px] text-blue-600 hover:underline"
                      >
                        Mark all read
                      </button>
                    )}
                  </div>
                  <div className="max-h-72 overflow-y-auto divide-y divide-gray-100">
                    {notifications.length === 0 ? (
                      <p className="p-4 text-xs text-center text-gray-500">No active alerts</p>
                    ) : (
                      notifications.slice(0, 8).map((n) => (
                        <div
                          key={n.id}
                          onClick={() => handleNotificationClick(n)}
                          className={`p-3 text-xs cursor-pointer hover:bg-gray-50 ${
                            !n.is_read ? 'bg-blue-50/40' : ''
                          }`}
                        >
                          <div className="flex items-start space-x-2">
                            {n.type === 'critical' ? (
                              <AlertCircle size={14} className="text-red-500 flex-shrink-0 mt-0.5" />
                            ) : n.type === 'warning' ? (
                              <AlertTriangle size={14} className="text-amber-500 flex-shrink-0 mt-0.5" />
                            ) : (
                              <CheckCircle2 size={14} className="text-green-500 flex-shrink-0 mt-0.5" />
                            )}
                            <div className="flex-1 min-w-0">
                              <p className="font-medium text-gray-900 truncate">{n.title}</p>
                              <p className="text-gray-500 text-[11px] line-clamp-2 mt-0.5">{n.message}</p>
                            </div>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Logout button */}
            <button
              onClick={logout}
              title="Logout session"
              className="p-1.5 text-gray-400 hover:text-gray-600 rounded-md hover:bg-gray-100 transition-colors"
            >
              <LogOut size={16} />
            </button>
          </div>
        </header>

        {/* Content Outlet */}
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default DashboardLayout;

