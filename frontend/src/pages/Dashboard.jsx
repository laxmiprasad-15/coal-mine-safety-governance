import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  FileCheck, AlertTriangle, HardHat, ShieldAlert,
  Clock, Wrench, HeartPulse, CheckCircle2, ArrowRight,
  TrendingUp, Activity, Map, ExternalLink
} from 'lucide-react';
import StatCard from '../components/StatCard';
import RiskBadge from '../components/RiskBadge';
import { getDashboardSummaryApi } from '../services/api';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const Dashboard = () => {
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      const res = await getDashboardSummaryApi();
      setData(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 10000);
    return () => clearInterval(interval);
  }, []);

  if (loading || !data) {
    return (
      <div className="flex items-center justify-center h-64 text-sm text-gray-500">
        Loading Coal Mine Safety Governance intelligence...
      </div>
    );
  }

  const { kpis, recent_detections, recent_anomalies, zones_mini } = data;

  const chartData = zones_mini.map(z => ({
    name: z.name.split(' ')[0] + ' ' + (z.name.split(' ')[1] || ''),
    score: z.risk_score,
    level: z.risk_level
  }));

  const getBarColor = (level) => {
    if (level === 'Critical') return '#DC2626';
    if (level === 'High') return '#EA580C';
    if (level === 'Medium') return '#EAB308';
    return '#16A34A';
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-xl font-semibold text-gray-900 tracking-tight">Safety & Compliance Governance Dashboard</h2>
          <p className="text-xs text-gray-500 mt-1">
            Real-time AI computer vision PPE tracking, IoT multi-gas telemetry, and traceable compliance remediation.
          </p>
        </div>
        <div className="mt-3 md:mt-0 flex space-x-2">
          <button
            onClick={() => navigate('/digital-twin')}
            className="inline-flex items-center text-xs font-medium px-3 py-1.5 rounded-md bg-blue-600 text-white hover:bg-blue-700 transition-colors"
          >
            <Map size={14} className="mr-1.5" />
            Launch 2D Digital Twin
          </button>
          <button
            onClick={() => navigate('/reports')}
            className="inline-flex items-center text-xs font-medium px-3 py-1.5 rounded-md bg-white border border-gray-200 text-gray-700 hover:bg-gray-50 transition-colors"
          >
            Generate Audit Report
          </button>
        </div>
      </div>

      {/* 8 Primary KPI Stat Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          title="Open Compliance Cases"
          value={kpis.open_cases}
          subtext={`${kpis.total_cases} total logged`}
          icon={FileCheck}
          onClick={() => navigate('/compliance-cases')}
        />
        <StatCard
          title="Critical Alerts Today"
          value={kpis.critical_alerts_today}
          subtext="Immediate response required"
          icon={AlertTriangle}
          alert={kpis.critical_alerts_today > 0}
          onClick={() => navigate('/sensors')}
        />
        <StatCard
          title="PPE Violations (24h)"
          value={kpis.ppe_violations_today}
          subtext="Detected via YOLOv8 feeds"
          icon={HardHat}
          onClick={() => navigate('/ppe-detection')}
        />
        <StatCard
          title="High-Risk Sectors"
          value={kpis.high_risk_zones}
          subtext="Under heightened surveillance"
          icon={ShieldAlert}
          alert={kpis.high_risk_zones > 0}
          onClick={() => navigate('/risk-forecast')}
        />
        <StatCard
          title="Overdue Actions"
          value={kpis.overdue_actions}
          subtext="Exceeded statutory deadline"
          icon={Clock}
          alert={kpis.overdue_actions > 0}
          onClick={() => navigate('/actions')}
        />
        <StatCard
          title="Machinery Alerts"
          value={kpis.equipment_alerts}
          subtext="Abnormal vibration / heat"
          icon={Wrench}
          onClick={() => navigate('/equipment')}
        />
        <StatCard
          title="Crew Vitals Alerts"
          value={kpis.worker_health_alerts}
          subtext="Fatigue / heat exhaustion"
          icon={HeartPulse}
          onClick={() => navigate('/workers')}
        />
        <StatCard
          title="Compliance Resolution"
          value={`${kpis.completion_rate}%`}
          subtext="Closed & verified cases"
          icon={CheckCircle2}
          onClick={() => navigate('/compliance-cases')}
        />
      </div>

      {/* Mini Risk Forecast Chart & Quick Navigation Bar */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white p-5 rounded-lg border border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-gray-900">Sector-wise Predictive Risk Distribution</h3>
              <p className="text-xs text-gray-500">Continuous AI risk index (0-100) calculated from multi-sensor and PPE feeds</p>
            </div>
            <button
              onClick={() => navigate('/risk-forecast')}
              className="text-xs text-blue-600 hover:underline inline-flex items-center"
            >
              Next Shift Forecast <ArrowRight size={12} className="ml-1" />
            </button>
          </div>
          <div className="h-48 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <XAxis dataKey="name" tick={{ fontSize: 10, fill: '#6B7280' }} interval={0} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 10, fill: '#6B7280' }} />
                <Tooltip
                  formatter={(val, name, item) => [`${val}/100 (${item.payload.level} Risk)`, 'Risk Index']}
                  contentStyle={{ backgroundColor: '#FFF', borderColor: '#E5E7EB', fontSize: 11, borderRadius: 6 }}
                />
                <Bar dataKey="score" radius={[4, 4, 0, 0]}>
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={getBarColor(entry.level)} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Quick Action Pillars */}
        <div className="bg-white p-5 rounded-lg border border-gray-200 flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-semibold text-gray-900 mb-1">Operational Governance Modules</h3>
            <p className="text-xs text-gray-500 mb-4">Statutory coal mine compliance workflows</p>
            <div className="space-y-2.5">
              <div
                onClick={() => navigate('/ppe-detection')}
                className="p-3 rounded-md border border-gray-200 hover:border-blue-400 hover:bg-blue-50/20 cursor-pointer transition-colors flex items-center justify-between"
              >
                <div className="flex items-center space-x-2.5">
                  <HardHat size={16} className="text-blue-600" />
                  <div>
                    <p className="text-xs font-medium text-gray-900">PPE Safety Verification</p>
                    <p className="text-[11px] text-gray-500">Review YOLOv8 detections</p>
                  </div>
                </div>
                <ArrowRight size={14} className="text-gray-400" />
              </div>

              <div
                onClick={() => navigate('/sensors')}
                className="p-3 rounded-md border border-gray-200 hover:border-blue-400 hover:bg-blue-50/20 cursor-pointer transition-colors flex items-center justify-between"
              >
                <div className="flex items-center space-x-2.5">
                  <Activity size={16} className="text-emerald-600" />
                  <div>
                    <p className="text-xs font-medium text-gray-900">Atmospheric Gas Matrix</p>
                    <p className="text-[11px] text-gray-500">CH4, CO, O2, Airflow telemetry</p>
                  </div>
                </div>
                <ArrowRight size={14} className="text-gray-400" />
              </div>

              <div
                onClick={() => navigate('/compliance-cases')}
                className="p-3 rounded-md border border-gray-200 hover:border-blue-400 hover:bg-blue-50/20 cursor-pointer transition-colors flex items-center justify-between"
              >
                <div className="flex items-center space-x-2.5">
                  <FileCheck size={16} className="text-indigo-600" />
                  <div>
                    <p className="text-xs font-medium text-gray-900">Compliance Case Ledger</p>
                    <p className="text-[11px] text-gray-500">Traceable audit workflow</p>
                  </div>
                </div>
                <ArrowRight size={14} className="text-gray-400" />
              </div>
            </div>
          </div>
          <div className="mt-4 pt-3 border-t border-gray-100 flex items-center justify-between text-[11px] text-gray-500">
            <span>DGMS Regulatory Compliance</span>
            <span className="text-emerald-600 font-medium">Active Monitoring</span>
          </div>
        </div>
      </div>

      {/* Recent AI Detections & Sensor Outliers */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent AI PPE Detections */}
        <div className="bg-white rounded-lg border border-gray-200 p-5">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-gray-900">Recent AI PPE Detections</h3>
              <p className="text-xs text-gray-500">Automated optical safety equipment inspection</p>
            </div>
            <button
              onClick={() => navigate('/ppe-detection')}
              className="text-xs text-blue-600 hover:underline"
            >
              View all
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-gray-50 text-gray-500 border-y border-gray-200">
                <tr>
                  <th className="py-2 px-3">Violation Type</th>
                  <th className="py-2 px-3">Zone</th>
                  <th className="py-2 px-3">Confidence</th>
                  <th className="py-2 px-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 text-gray-700">
                {recent_detections.map((d) => (
                  <tr key={d.id} className="hover:bg-gray-50/60">
                    <td className="py-2.5 px-3 font-medium text-gray-900">{d.violation}</td>
                    <td className="py-2.5 px-3 text-gray-500">{d.zone}</td>
                    <td className="py-2.5 px-3">{Math.round(d.confidence * 100)}%</td>
                    <td className="py-2.5 px-3">
                      <span className={`inline-block px-2 py-0.5 rounded text-[11px] font-medium ${
                        d.status === 'Confirmed' ? 'bg-amber-100 text-amber-800' :
                        d.status === 'Case Created' ? 'bg-blue-100 text-blue-800' :
                        d.status === 'Compliant' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                      }`}>
                        {d.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Recent Sensor Telemetry Anomalies */}
        <div className="bg-white rounded-lg border border-gray-200 p-5">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-gray-900">Atmospheric & Machinery Anomalies</h3>
              <p className="text-xs text-gray-500">Flagged by Isolation Forest and DGMS safety limits</p>
            </div>
            <button
              onClick={() => navigate('/sensors')}
              className="text-xs text-blue-600 hover:underline"
            >
              View all
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-gray-50 text-gray-500 border-y border-gray-200">
                <tr>
                  <th className="py-2 px-3">Metric / Sensor</th>
                  <th className="py-2 px-3">Reading</th>
                  <th className="py-2 px-3">Zone</th>
                  <th className="py-2 px-3">Anomaly Score</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 text-gray-700">
                {recent_anomalies.map((a) => (
                  <tr key={a.id} className="hover:bg-gray-50/60">
                    <td className="py-2.5 px-3 font-medium text-gray-900">{a.sensor}</td>
                    <td className="py-2.5 px-3 font-semibold text-red-600">
                      {a.value} {a.unit}
                    </td>
                    <td className="py-2.5 px-3 text-gray-500">{a.zone}</td>
                    <td className="py-2.5 px-3">{a.score}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

