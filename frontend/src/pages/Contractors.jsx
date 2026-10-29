import React, { useState, useEffect } from 'react';
import {
  Users, ShieldCheck, AlertTriangle, FileText, CheckCircle2,
  XCircle, Filter, Search, Building2, Briefcase, Award
} from 'lucide-react';
import axios from 'axios';

const SUBSIDIARIES = [
  { code: 'ALL', name: 'All Coal India Subsidiaries' },
  { code: 'BCCL', name: 'BCCL - Bharat Coking Coal (Dhanbad)' },
  { code: 'ECL', name: 'ECL - Eastern Coalfields (Sanctoria)' },
  { code: 'CCL', name: 'CCL - Central Coalfields (Ranchi)' },
  { code: 'WCL', name: 'WCL - Western Coalfields (Nagpur)' },
  { code: 'SECL', name: 'SECL - South Eastern Coalfields (Bilaspur)' },
  { code: 'MCL', name: 'MCL - Mahanadi Coalfields (Sambalpur)' },
  { code: 'NCL', name: 'NCL - Northern Coalfields (Singrauli)' },
];

export default function Contractors() {
  const [contractors, setContractors] = useState([]);
  const [summary, setSummary] = useState(null);
  const [selectedSub, setSelectedSub] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      setLoading(true);
      const [cRes, sRes] = await Promise.all([
        axios.get(`/api/v1/contractors/?subsidiary=${selectedSub}`),
        axios.get('/api/v1/contractors/summary')
      ]);
      setContractors(cRes.data);
      setSummary(sRes.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [selectedSub]);

  const filtered = contractors.filter(c =>
    c.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    c.code.toLowerCase().includes(searchQuery.toLowerCase()) ||
    c.work_order_no.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-xl font-semibold text-gray-900 tracking-tight">Contractor Governance & Statutory Labour Compliance</h2>
          <p className="text-xs text-gray-500 mt-1">
            Centralized oversight of outsourced mining contractors across CIL subsidiaries. Tracking Form B registers, PME Form O medical examinations, and VTC induction.
          </p>
        </div>
      </div>

      {/* KPI Cards */}
      {summary && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3.5">
          <div className="bg-white p-4 rounded-lg border border-gray-200">
            <span className="text-xs text-gray-500">Active Mining Contractors</span>
            <div className="flex items-baseline justify-between mt-1.5">
              <span className="text-2xl font-bold text-gray-900">{summary.total_contractors}</span>
              <Building2 size={16} className="text-blue-600" />
            </div>
            <span className="text-[11px] text-gray-400 mt-1 block">Deploying {summary.total_contract_workers} contract miners</span>
          </div>

          <div className="bg-white p-4 rounded-lg border border-gray-200">
            <span className="text-xs text-gray-500">Avg Compliance Rating</span>
            <div className="flex items-baseline justify-between mt-1.5">
              <span className="text-2xl font-bold text-emerald-600">{summary.avg_compliance_score}%</span>
              <Award size={16} className="text-emerald-600" />
            </div>
            <span className="text-[11px] text-emerald-600 mt-1 block">DGMS benchmark: &gt; 80%</span>
          </div>

          <div className="bg-white p-4 rounded-lg border border-gray-200">
            <span className="text-xs text-gray-500">PME Medical Clearance (Form O)</span>
            <div className="flex items-baseline justify-between mt-1.5">
              <span className="text-2xl font-bold text-blue-600">{summary.pme_compliant_rate}%</span>
              <ShieldCheck size={16} className="text-blue-600" />
            </div>
            <span className="text-[11px] text-gray-400 mt-1 block">Statutory CMR rule compliance</span>
          </div>

          <div className="bg-white p-4 rounded-lg border border-gray-200">
            <span className="text-xs text-gray-500">At-Risk Contractors</span>
            <div className="flex items-baseline justify-between mt-1.5">
              <span className="text-2xl font-bold text-amber-600">{summary.at_risk_contractors}</span>
              <AlertTriangle size={16} className="text-amber-600" />
            </div>
            <span className="text-[11px] text-amber-600 mt-1 block">Score &lt; 80% (Audit warning)</span>
          </div>
        </div>
      )}

      {/* Filter Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 bg-white p-3 rounded-lg border border-gray-200">
        <div className="flex items-center space-x-2">
          <Filter size={14} className="text-gray-400" />
          <span className="text-xs font-medium text-gray-700">Subsidiary:</span>
          <select
            value={selectedSub}
            onChange={(e) => setSelectedSub(e.target.value)}
            className="text-xs rounded border border-gray-300 py-1.5 px-3 bg-white text-gray-800 focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            {SUBSIDIARIES.map((sub) => (
              <option key={sub.code} value={sub.code}>{sub.name}</option>
            ))}
          </select>
        </div>

        <div className="relative">
          <Search size={14} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder="Search contractor or work order..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-8 pr-3 py-1.5 text-xs rounded border border-gray-300 bg-white placeholder-gray-400 w-64 focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>
      </div>

      {/* Contractors Table */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-gray-600">
            <thead className="bg-gray-50 text-[11px] text-gray-500 uppercase border-b border-gray-200">
              <tr>
                <th className="px-4 py-3">Contractor / Agency</th>
                <th className="px-4 py-3">Subsidiary</th>
                <th className="px-4 py-3">Work Order</th>
                <th className="px-4 py-3">Category</th>
                <th className="px-4 py-3">Workers</th>
                <th className="px-4 py-3">Form O (PME)</th>
                <th className="px-4 py-3">VTC Trained</th>
                <th className="px-4 py-3">Compliance Score</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filtered.map((c) => (
                <tr key={c.id} className="hover:bg-gray-50/80 transition-colors">
                  <td className="px-4 py-3">
                    <span className="font-semibold text-gray-900 block">{c.name}</span>
                    <span className="text-[10px] text-gray-400 font-mono">{c.code}</span>
                  </td>
                  <td className="px-4 py-3">
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-50 text-blue-700 border border-blue-200">
                      {c.subsidiary}
                    </span>
                  </td>
                  <td className="px-4 py-3 font-mono text-[11px] text-gray-700">
                    {c.work_order_no}
                  </td>
                  <td className="px-4 py-3 text-gray-700">
                    {c.category}
                  </td>
                  <td className="px-4 py-3 font-semibold text-gray-800">
                    {c.active_workers}
                  </td>
                  <td className="px-4 py-3">
                    {c.pme_valid ? (
                      <span className="inline-flex items-center text-emerald-700 text-[11px] font-medium">
                        <CheckCircle2 size={13} className="mr-1 text-emerald-600" /> Valid
                      </span>
                    ) : (
                      <span className="inline-flex items-center text-red-700 text-[11px] font-medium">
                        <XCircle size={13} className="mr-1 text-red-600" /> 3 Due
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    {c.vtc_trained ? (
                      <span className="inline-flex items-center text-emerald-700 text-[11px] font-medium">
                        <CheckCircle2 size={13} className="mr-1 text-emerald-600" /> 100%
                      </span>
                    ) : (
                      <span className="inline-flex items-center text-amber-700 text-[11px] font-medium">
                        <AlertTriangle size={13} className="mr-1 text-amber-600" /> Refresh Due
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center space-x-2">
                      <div className="w-16 bg-gray-200 rounded-full h-1.5 overflow-hidden">
                        <div
                          className={`h-full rounded-full ${
                            c.compliance_score >= 90 ? 'bg-emerald-500' :
                            c.compliance_score >= 80 ? 'bg-blue-500' : 'bg-amber-500'
                          }`}
                          style={{ width: `${c.compliance_score}%` }}
                        ></div>
                      </div>
                      <span className="font-bold text-gray-900">{c.compliance_score}%</span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
