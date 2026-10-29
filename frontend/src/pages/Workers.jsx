import React, { useState, useEffect } from 'react';
import {
  Users, HeartPulse, Thermometer, Clock, AlertTriangle,
  CheckCircle2, Plus, RefreshCw, UserCheck
} from 'lucide-react';
import { getWorkersApi, postHealthReadingApi, getZonesApi } from '../services/api';
import Modal from '../components/Modal';

const Workers = () => {
  const [workers, setWorkers] = useState([]);
  const [zones, setZones] = useState([]);
  const [loading, setLoading] = useState(true);

  // Health modal
  const [readingModalOpen, setReadingModalOpen] = useState(false);
  const [selectedWorker, setSelectedWorker] = useState(null);
  const [healthForm, setHealthForm] = useState({
    heart_rate: '78',
    body_temp: '36.8',
    spo2: '98',
    fatigue_score: '20',
    shift_hours: '4.5',
    activity_status: 'Active'
  });

  const loadWorkers = async () => {
    try {
      setLoading(true);
      const [wRes, zRes] = await Promise.all([
        getWorkersApi(),
        getZonesApi()
      ]);
      setWorkers(wRes.data);
      setZones(zRes.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadWorkers();
  }, []);

  const handleOpenReadingModal = (w) => {
    setSelectedWorker(w);
    setHealthForm({
      heart_rate: w.last_heart_rate ? String(Math.round(w.last_heart_rate)) : '80',
      body_temp: w.last_body_temp ? String(w.last_body_temp) : '36.8',
      spo2: '98',
      fatigue_score: w.fatigue_score ? String(Math.round(w.fatigue_score)) : '25',
      shift_hours: '4.5',
      activity_status: 'Active'
    });
    setReadingModalOpen(true);
  };

  const handleReadingSubmit = async (e) => {
    e.preventDefault();
    if (!selectedWorker) return;

    try {
      await postHealthReadingApi({
        worker_id: selectedWorker.id,
        heart_rate: Number(healthForm.heart_rate),
        body_temp: Number(healthForm.body_temp),
        spo2: Number(healthForm.spo2),
        fatigue_score: Number(healthForm.fatigue_score),
        shift_hours: Number(healthForm.shift_hours),
        activity_status: healthForm.activity_status
      });
      setReadingModalOpen(false);
      await loadWorkers();
    } catch (err) {
      alert("Error submitting wearable reading: " + err.message);
    }
  };

  const alertWorkersCount = workers.filter(w => w.is_alert).length;

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-xl font-semibold text-gray-900 tracking-tight">Worker Health & Crew Fatigue Surveillance</h2>
          <p className="text-xs text-gray-500 mt-1">
            Real-time wearable biometric monitoring of heart rate, SpO2, core temperature, and shift exhaustion fatigue indices.
          </p>
        </div>
        <div className="mt-3 md:mt-0 flex items-center space-x-2">
          {alertWorkersCount > 0 && (
            <span className="text-xs px-2.5 py-1 rounded bg-red-100 text-red-800 font-semibold border border-red-200 flex items-center">
              <AlertTriangle size={13} className="mr-1 text-red-600" />
              {alertWorkersCount} Crew Member(s) in Medical Alert
            </span>
          )}
        </div>
      </div>

      {/* Workers Roster Table */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-gray-50 text-gray-500 border-b border-gray-200 font-semibold">
              <tr>
                <th className="py-3 px-4">Worker ID & Name</th>
                <th className="py-3 px-4">Role Title</th>
                <th className="py-3 px-4">Stationed Sector</th>
                <th className="py-3 px-4">Heart Rate</th>
                <th className="py-3 px-4">Body Temp</th>
                <th className="py-3 px-4">Fatigue Index</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Wearable Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 text-gray-700">
              {workers.map((w) => (
                <tr key={w.id} className={`hover:bg-gray-50/70 ${w.is_alert ? 'bg-red-50/30' : ''}`}>
                  <td className="py-3 px-4">
                    <span className="font-semibold text-gray-900 block">{w.full_name}</span>
                    <span className="text-[11px] font-mono text-gray-400">{w.worker_code} • {w.blood_group}</span>
                  </td>
                  <td className="py-3 px-4 text-gray-600">{w.role_title}</td>
                  <td className="py-3 px-4 text-gray-700 font-medium">{w.zone_name}</td>
                  <td className="py-3 px-4 font-mono font-medium">
                    <span className={w.last_heart_rate > 115 ? 'text-red-600 font-bold' : 'text-gray-900'}>
                      {w.last_heart_rate ? `${Math.round(w.last_heart_rate)} bpm` : 'N/A'}
                    </span>
                  </td>
                  <td className="py-3 px-4 font-mono font-medium">
                    <span className={w.last_body_temp >= 38.0 ? 'text-red-600 font-bold' : 'text-gray-900'}>
                      {w.last_body_temp ? `${w.last_body_temp}°C` : 'N/A'}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <div className="flex items-center space-x-2">
                      <span className="font-mono text-[11px]">{w.fatigue_score ? Math.round(w.fatigue_score) : 0}/100</span>
                      <div className="w-16 bg-gray-100 rounded-full h-1.5 overflow-hidden">
                        <div
                          className={`h-1.5 rounded-full ${
                            (w.fatigue_score || 0) > 70 ? 'bg-red-500' : 'bg-blue-600'
                          }`}
                          style={{ width: `${Math.min(100, w.fatigue_score || 0)}%` }}
                        />
                      </div>
                    </div>
                  </td>
                  <td className="py-3 px-4">
                    <span className={`inline-block px-2 py-0.5 rounded text-[11px] font-medium ${
                      w.status === 'Medical Alert' ? 'bg-red-100 text-red-800' :
                      w.status === 'Break' ? 'bg-amber-100 text-amber-800' : 'bg-green-100 text-green-800'
                    }`}>
                      {w.status}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right">
                    <button
                      onClick={() => handleOpenReadingModal(w)}
                      className="px-2.5 py-1 rounded bg-gray-100 hover:bg-gray-200 text-gray-800 text-[11px] font-medium"
                    >
                      Log Vitals
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Wearable Biometric Ingestion Modal */}
      <Modal
        isOpen={readingModalOpen}
        onClose={() => setReadingModalOpen(false)}
        title={selectedWorker ? `Wearable Device Reading: ${selectedWorker.full_name}` : 'Log Vitals'}
      >
        <form onSubmit={handleReadingSubmit} className="space-y-4 text-xs">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-medium text-gray-700 mb-1">Heart Rate (BPM)</label>
              <input
                type="number"
                step="1"
                required
                value={healthForm.heart_rate}
                onChange={(e) => setHealthForm({ ...healthForm, heart_rate: e.target.value })}
                className="w-full text-xs rounded border border-gray-300 p-2"
              />
              <span className="text-[10px] text-gray-400">Normal: 60 - 100 bpm</span>
            </div>
            <div>
              <label className="block font-medium text-gray-700 mb-1">Core Body Temp (°C)</label>
              <input
                type="number"
                step="0.1"
                required
                value={healthForm.body_temp}
                onChange={(e) => setHealthForm({ ...healthForm, body_temp: e.target.value })}
                className="w-full text-xs rounded border border-gray-300 p-2"
              />
              <span className="text-[10px] text-gray-400">Heat Stress: &ge; 38.0°C</span>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-medium text-gray-700 mb-1">Blood Oxygen SpO2 (%)</label>
              <input
                type="number"
                step="0.5"
                required
                value={healthForm.spo2}
                onChange={(e) => setHealthForm({ ...healthForm, spo2: e.target.value })}
                className="w-full text-xs rounded border border-gray-300 p-2"
              />
            </div>
            <div>
              <label className="block font-medium text-gray-700 mb-1">Fatigue Score (0-100)</label>
              <input
                type="number"
                step="1"
                min="0"
                max="100"
                required
                value={healthForm.fatigue_score}
                onChange={(e) => setHealthForm({ ...healthForm, fatigue_score: e.target.value })}
                className="w-full text-xs rounded border border-gray-300 p-2"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-medium text-gray-700 mb-1">Shift Duration (Hours)</label>
              <input
                type="number"
                step="0.5"
                value={healthForm.shift_hours}
                onChange={(e) => setHealthForm({ ...healthForm, shift_hours: e.target.value })}
                className="w-full text-xs rounded border border-gray-300 p-2"
              />
            </div>
            <div>
              <label className="block font-medium text-gray-700 mb-1">Activity State</label>
              <select
                value={healthForm.activity_status}
                onChange={(e) => setHealthForm({ ...healthForm, activity_status: e.target.value })}
                className="w-full text-xs rounded border border-gray-300 p-2"
              >
                <option value="Active">Active Drilling / Operating</option>
                <option value="High Exertion">High Physical Exertion</option>
                <option value="Resting">Resting / Break</option>
              </select>
            </div>
          </div>

          <div className="flex justify-end space-x-2 pt-3 border-t border-gray-200">
            <button
              type="button"
              onClick={() => setReadingModalOpen(false)}
              className="px-3 py-1.5 rounded border border-gray-300 text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-3.5 py-1.5 rounded bg-blue-600 text-white hover:bg-blue-700 font-medium"
            >
              Update Wearable Telemetry
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default Workers;

