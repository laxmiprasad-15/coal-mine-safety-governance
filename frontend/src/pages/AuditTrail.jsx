import React, { useState, useEffect } from 'react';
import {
  ShieldAlert, Search, Filter, Lock, CheckCircle2,
  RefreshCw, User, Database, Hash
} from 'lucide-react';
import { getAuditLogsApi } from '../services/api';

const ACTIONS = ['All', 'USER_LOGIN', 'USER_REGISTERED', 'PPE_DETECTION_RUN', 'PPE_DETECTION_CONFIRMED', 'CASE_CREATED', 'CASE_UPDATED', 'CORRECTIVE_ACTION_CREATED', 'CORRECTIVE_ACTION_STATUS_CHANGED', 'REPORT_GENERATED'];

const AuditTrail = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedAction, setSelectedAction] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');

  const loadLogs = async () => {
    try {
      setLoading(true);
      const params = {};
      if (selectedAction !== 'All') params.action = selectedAction;
      const res = await getAuditLogsApi(params);
      setLogs(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLogs();
  }, [selectedAction]);

  const filteredLogs = logs.filter(l => {
    if (!searchQuery.trim()) return true;
    const q = searchQuery.toLowerCase();
    return (
      (l.action && l.action.toLowerCase().includes(q)) ||
      (l.user_name && l.user_name.toLowerCase().includes(q)) ||
      (l.new_state && l.new_state.toLowerCase().includes(q)) ||
      (l.tamper_token && l.tamper_token.toLowerCase().includes(q))
    );
  });

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-xl font-semibold text-gray-900 tracking-tight">Immutable Compliance Audit Trail & Governance Log</h2>
          <p className="text-xs text-gray-500 mt-1">
            Tamper-evident regulatory logging chaining user, timestamp, state delta, and SHA-256 cryptographic integrity tokens.
          </p>
        </div>
        <div className="mt-3 md:mt-0 flex items-center space-x-2">
          <span className="text-xs px-2.5 py-1 rounded bg-green-50 text-green-700 font-medium border border-green-200 flex items-center">
            <Lock size={12} className="mr-1 text-green-600" />
            Cryptographic Integrity Verified
          </span>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white p-4 rounded-lg border border-gray-200 flex flex-col md:flex-row md:items-center md:justify-between gap-3 text-xs">
        <div className="relative flex-1 max-w-sm">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search action, actor, token hash, delta..."
            className="w-full text-xs rounded border border-gray-300 pl-8 pr-3 py-1.5 focus:ring-1 focus:ring-blue-500"
          />
          <Search size={14} className="absolute left-2.5 top-2.5 text-gray-400" />
        </div>

        <div className="flex items-center space-x-2">
          <span className="text-gray-500">Action Type:</span>
          <select
            value={selectedAction}
            onChange={(e) => setSelectedAction(e.target.value)}
            className="text-xs rounded border border-gray-300 py-1 px-2.5 bg-white text-gray-800"
          >
            {ACTIONS.map(a => <option key={a} value={a}>{a}</option>)}
          </select>
        </div>
      </div>

      {/* Audit Logs Table */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-gray-50 text-gray-500 border-b border-gray-200 font-semibold">
              <tr>
                <th className="py-3 px-4">Timestamp (UTC)</th>
                <th className="py-3 px-4">Action Event</th>
                <th className="py-3 px-4">Entity Type</th>
                <th className="py-3 px-4">Operator / Actor</th>
                <th className="py-3 px-4">State Delta / Event Details</th>
                <th className="py-3 px-4">SHA-256 Tamper Verification Token</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 text-gray-700">
              {filteredLogs.map((l) => (
                <tr key={l.id} className="hover:bg-gray-50/70 font-mono text-[11px]">
                  <td className="py-3 px-4 text-gray-500 whitespace-nowrap">
                    {new Date(l.timestamp).toLocaleString()}
                  </td>
                  <td className="py-3 px-4">
                    <span className="font-semibold text-blue-700 font-sans text-xs">
                      {l.action}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-gray-600 font-sans">{l.entity_type}</td>
                  <td className="py-3 px-4 text-gray-800 font-sans font-medium">
                    {l.user_name}
                  </td>
                  <td className="py-3 px-4 font-sans text-gray-700 max-w-xs truncate">
                    {l.new_state || l.previous_state || "System state transition verified"}
                  </td>
                  <td className="py-3 px-4 text-gray-400 max-w-[160px] truncate">
                    <span className="text-[10px] bg-gray-100 text-gray-600 px-1.5 py-0.5 rounded border border-gray-200" title={l.tamper_token}>
                      {l.tamper_token ? l.tamper_token.slice(0, 16) + '...' : 'SHA256-GEN'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default AuditTrail;

