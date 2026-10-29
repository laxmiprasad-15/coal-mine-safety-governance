import React, { useState, useEffect } from 'react';
import {
  Wrench, AlertTriangle, CheckCircle2, Activity,
  Clock, Gauge, Plus, RefreshCw, ArrowUpRight
} from 'lucide-react';
import { getEquipmentApi, postEquipmentReadingApi } from '../services/api';
import Modal from '../components/Modal';

const Equipment = () => {
  const [equipmentList, setEquipmentList] = useState([]);
  const [loading, setLoading] = useState(true);

  // Ingest reading modal
  const [readingModalOpen, setReadingModalOpen] = useState(false);
  const [selectedEquip, setSelectedEquip] = useState(null);
  const [telemetryForm, setTelemetryForm] = useState({
    vibration: '2.5',
    temperature: '50.0',
    oil_pressure: '4.2',
    current_draw: '42.0',
    rpm: '1450'
  });

  const loadEquipment = async () => {
    try {
      setLoading(true);
      const res = await getEquipmentApi();
      setEquipmentList(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadEquipment();
  }, []);

  const handleOpenTelemetryModal = (eq) => {
    setSelectedEquip(eq);
    setTelemetryForm({
      vibration: eq.last_vibration ? String(eq.last_vibration) : '3.0',
      temperature: eq.last_temp ? String(eq.last_temp) : '52.0',
      oil_pressure: '4.2',
      current_draw: '45.0',
      rpm: '1450'
    });
    setReadingModalOpen(true);
  };

  const handleTelemetrySubmit = async (e) => {
    e.preventDefault();
    if (!selectedEquip) return;

    try {
      await postEquipmentReadingApi({
        equipment_id: selectedEquip.id,
        vibration: Number(telemetryForm.vibration),
        temperature: Number(telemetryForm.temperature),
        oil_pressure: Number(telemetryForm.oil_pressure),
        current_draw: Number(telemetryForm.current_draw),
        rpm: Number(telemetryForm.rpm)
      });
      setReadingModalOpen(false);
      await loadEquipment();
    } catch (err) {
      alert("Error submitting telemetry: " + err.message);
    }
  };

  const warningCount = equipmentList.filter(e => e.status !== 'Operational').length;

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-xl font-semibold text-gray-900 tracking-tight">Machinery Health & Predictive Maintenance</h2>
          <p className="text-xs text-gray-500 mt-1">
            Predictive continuous condition monitoring of shearers, continuous miners, haulage belts, and exhaust ventilation fans with Remaining Useful Life (RUL) estimation.
          </p>
        </div>
        <div className="mt-3 md:mt-0 flex items-center space-x-2">
          {warningCount > 0 && (
            <span className="text-xs px-2.5 py-1 rounded bg-amber-100 text-amber-800 font-semibold border border-amber-200 flex items-center">
              <AlertTriangle size={13} className="mr-1 text-amber-600" />
              {warningCount} Machine(s) Require Maintenance Attention
            </span>
          )}
        </div>
      </div>

      {/* Equipment Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {equipmentList.map((eq) => {
          const isWarning = eq.status !== 'Operational';
          return (
            <div
              key={eq.id}
              className={`bg-white rounded-lg border p-5 transition-all ${
                isWarning ? 'border-amber-300 bg-amber-50/15' : 'border-gray-200'
              }`}
            >
              <div className="flex items-start justify-between">
                <div>
                  <span className="text-[10px] font-mono text-gray-400">{eq.equipment_code}</span>
                  <h3 className="text-sm font-semibold text-gray-900">{eq.name}</h3>
                  <span className="text-[11px] text-gray-500">{eq.type} • {eq.zone_name}</span>
                </div>
                <span className={`px-2 py-0.5 rounded text-[11px] font-medium ${
                  eq.status === 'Operational' ? 'bg-green-100 text-green-800' :
                  eq.status === 'Warning' ? 'bg-amber-100 text-amber-800' : 'bg-red-100 text-red-800'
                }`}>
                  {eq.status}
                </span>
              </div>

              {/* Health Score and RUL */}
              <div className="mt-4 pt-3 border-t border-gray-100 space-y-2">
                <div>
                  <div className="flex items-center justify-between text-xs mb-1">
                    <span className="text-gray-500">Condition Index:</span>
                    <span className="font-semibold text-gray-900">{Math.round(eq.health_score)}%</span>
                  </div>
                  <div className="w-full bg-gray-100 rounded-full h-2 overflow-hidden">
                    <div
                      className={`h-2 rounded-full ${
                        eq.health_score > 70 ? 'bg-emerald-600' :
                        eq.health_score > 45 ? 'bg-amber-500' : 'bg-red-600'
                      }`}
                      style={{ width: `${eq.health_score}%` }}
                    />
                  </div>
                </div>

                <div className="flex items-center justify-between text-xs pt-1">
                  <span className="text-gray-500">Remaining Useful Life (RUL):</span>
                  <span className="font-mono font-semibold text-gray-800">{eq.rul_days} Days</span>
                </div>
              </div>

              {/* Telemetry Metrics Strip */}
              <div className="mt-3 grid grid-cols-2 gap-2 text-xs bg-gray-50 p-2.5 rounded border border-gray-100">
                <div>
                  <span className="text-[10px] text-gray-400 block uppercase">Vibration</span>
                  <span className={`font-semibold font-mono ${
                    (eq.last_vibration || 0) >= 7.5 ? 'text-red-600 font-bold' : 'text-gray-800'
                  }`}>
                    {eq.last_vibration !== null ? `${eq.last_vibration} mm/s` : 'N/A'}
                  </span>
                </div>
                <div>
                  <span className="text-[10px] text-gray-400 block uppercase">Temperature</span>
                  <span className={`font-semibold font-mono ${
                    (eq.last_temp || 0) >= 65 ? 'text-red-600 font-bold' : 'text-gray-800'
                  }`}>
                    {eq.last_temp !== null ? `${eq.last_temp}°C` : 'N/A'}
                  </span>
                </div>
              </div>

              <div className="mt-4 flex justify-end">
                <button
                  onClick={() => handleOpenTelemetryModal(eq)}
                  className="px-3 py-1.5 rounded bg-gray-100 hover:bg-gray-200 text-gray-800 font-medium text-xs"
                >
                  Log Telemetry Pulse
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Machinery Telemetry Input Modal */}
      <Modal
        isOpen={readingModalOpen}
        onClose={() => setReadingModalOpen(false)}
        title={selectedEquip ? `Machinery Telemetry: ${selectedEquip.name}` : 'Log Telemetry'}
      >
        <form onSubmit={handleTelemetrySubmit} className="space-y-4 text-xs">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-medium text-gray-700 mb-1">Vibration (mm/s RMS)</label>
              <input
                type="number"
                step="0.1"
                required
                value={telemetryForm.vibration}
                onChange={(e) => setTelemetryForm({ ...telemetryForm, vibration: e.target.value })}
                className="w-full text-xs rounded border border-gray-300 p-2"
              />
              <span className="text-[10px] text-gray-400">Limit: 7.5 mm/s</span>
            </div>
            <div>
              <label className="block font-medium text-gray-700 mb-1">Bearing Temp (°C)</label>
              <input
                type="number"
                step="0.5"
                required
                value={telemetryForm.temperature}
                onChange={(e) => setTelemetryForm({ ...telemetryForm, temperature: e.target.value })}
                className="w-full text-xs rounded border border-gray-300 p-2"
              />
              <span className="text-[10px] text-gray-400">Limit: 65.0°C</span>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="block font-medium text-gray-700 mb-1">Oil Pressure (bar)</label>
              <input
                type="number"
                step="0.1"
                value={telemetryForm.oil_pressure}
                onChange={(e) => setTelemetryForm({ ...telemetryForm, oil_pressure: e.target.value })}
                className="w-full text-xs rounded border border-gray-300 p-2"
              />
            </div>
            <div>
              <label className="block font-medium text-gray-700 mb-1">Motor Current (Amps)</label>
              <input
                type="number"
                step="1"
                value={telemetryForm.current_draw}
                onChange={(e) => setTelemetryForm({ ...telemetryForm, current_draw: e.target.value })}
                className="w-full text-xs rounded border border-gray-300 p-2"
              />
            </div>
            <div>
              <label className="block font-medium text-gray-700 mb-1">Shaft RPM</label>
              <input
                type="number"
                step="10"
                value={telemetryForm.rpm}
                onChange={(e) => setTelemetryForm({ ...telemetryForm, rpm: e.target.value })}
                className="w-full text-xs rounded border border-gray-300 p-2"
              />
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
              Evaluate Machine Condition
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default Equipment;

