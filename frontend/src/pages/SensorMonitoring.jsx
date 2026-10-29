import React, { useState, useEffect, useRef } from 'react';
import {
  Activity, Wind, Thermometer, Flame, Gauge,
  Upload, Plus, RefreshCw, AlertTriangle, CheckCircle2, ChevronRight
} from 'lucide-react';
import {
  getSensorsApi, getSensorHistoryApi, postSensorReadingApi,
  uploadSensorCsvApi, triggerSimulatorPulseApi, getZonesApi,
  toggleStreamerApi, getStreamerStatusApi
} from '../services/api';
import Modal from '../components/Modal';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

const SensorMonitoring = () => {
  const [sensors, setSensors] = useState([]);
  const [zones, setZones] = useState([]);
  const [selectedZone, setSelectedZone] = useState('all');
  const [selectedSensor, setSelectedSensor] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);

  useEffect(() => {
    getStreamerStatusApi().then(res => setIsStreaming(res.data.is_running)).catch(() => {});
  }, []);

  useEffect(() => {
    let interval = null;
    if (isStreaming) {
      interval = setInterval(async () => {
        await loadSensors();
        if (selectedSensor) {
          getSensorHistoryApi(selectedSensor.id).then(res => {
            const chartPoints = res.data.map(r => ({
              time: new Date(r.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
              value: r.value,
              is_anomaly: r.is_anomaly
            }));
            setHistory(chartPoints);
          }).catch(() => {});
        }
      }, 3500);
    }
    return () => { if (interval) clearInterval(interval); };
  }, [isStreaming, selectedSensor?.id]);

  const handleToggleStream = async () => {
    try {
      const nextState = !isStreaming;
      const res = await toggleStreamerApi(nextState, 3.5);
      setIsStreaming(res.data.is_running);
    } catch (e) {
      console.error(e);
    }
  };

  // Manual entry modal
  const [manualModalOpen, setManualModalOpen] = useState(false);
  const [manualForm, setManualForm] = useState({ sensor_id: '', value: '' });

  // CSV upload ref
  const csvInputRef = useRef(null);

  const loadSensors = async () => {
    try {
      const zoneParam = selectedZone === 'all' ? null : Number(selectedZone);
      const [sRes, zRes] = await Promise.all([
        getSensorsApi(zoneParam),
        getZonesApi()
      ]);
      setSensors(sRes.data);
      setZones(zRes.data);

      // Select first sensor by default if none selected
      if (!selectedSensor && sRes.data.length > 0) {
        handleSelectSensor(sRes.data[0]);
      } else if (selectedSensor) {
        const updated = sRes.data.find(s => s.id === selectedSensor.id);
        if (updated) setSelectedSensor(updated);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectSensor = async (s) => {
    setSelectedSensor(s);
    try {
      setHistoryLoading(true);
      const res = await getSensorHistoryApi(s.id);
      const chartPoints = res.data.map(r => ({
        time: new Date(r.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        value: r.value,
        is_anomaly: r.is_anomaly
      }));
      setHistory(chartPoints);
    } catch (e) {
      console.error(e);
    } finally {
      setHistoryLoading(false);
    }
  };

  useEffect(() => {
    loadSensors();
  }, [selectedZone]);

  const handleManualSubmit = async (e) => {
    e.preventDefault();
    if (!manualForm.sensor_id || manualForm.value === '') return;

    try {
      const s = sensors.find(item => item.id === Number(manualForm.sensor_id));
      await postSensorReadingApi({
        sensor_id: Number(manualForm.sensor_id),
        zone_id: s?.zone_id || 1,
        value: Number(manualForm.value)
      });
      setManualModalOpen(false);
      setManualForm({ sensor_id: '', value: '' });
      await loadSensors();
      if (selectedSensor?.id === Number(manualForm.sensor_id)) {
        handleSelectSensor(selectedSensor);
      }
    } catch (err) {
      alert("Error submitting reading: " + err.message);
    }
  };

  const handleCsvUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    try {
      const formData = new FormData();
      formData.append('file', file);
      const res = await uploadSensorCsvApi(formData);
      alert(res.data.message);
      await loadSensors();
    } catch (err) {
      alert("Error uploading CSV: " + err.message);
    }
  };

  const handlePulse = async () => {
    try {
      await triggerSimulatorPulseApi();
      await loadSensors();
      if (selectedSensor) handleSelectSensor(selectedSensor);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-xl font-semibold text-gray-900 tracking-tight">Environmental & IoT Telemetry Surveillance</h2>
          <p className="text-xs text-gray-500 mt-1">
            Real-time multi-gas monitoring (CH4, CO, O2), temperature, airflow velocity, and machinery vibration with dynamic DGMS safety thresholds.
          </p>
        </div>
        <div className="mt-3 md:mt-0 flex items-center space-x-2">
          <input
            type="file"
            ref={csvInputRef}
            onChange={handleCsvUpload}
            accept=".csv"
            className="hidden"
          />
          <button
            onClick={() => csvInputRef.current?.click()}
            className="inline-flex items-center text-xs font-medium px-3 py-1.5 rounded border border-gray-200 bg-white text-gray-700 hover:bg-gray-50"
          >
            <Upload size={14} className="mr-1.5 text-gray-500" />
            Upload Sensor CSV
          </button>
          <button
            onClick={() => setManualModalOpen(true)}
            className="inline-flex items-center text-xs font-medium px-3 py-1.5 rounded bg-blue-600 text-white hover:bg-blue-700"
          >
            <Plus size={14} className="mr-1.5" />
            Manual Reading Entry
          </button>
        </div>
      </div>

      {/* Zone Selector and Pulse Action */}
      <div className="flex items-center justify-between bg-white p-3.5 rounded-lg border border-gray-200">
        <div className="flex items-center space-x-3">
          <span className="text-xs font-medium text-gray-700">Filter by Sector:</span>
          <select
            value={selectedZone}
            onChange={(e) => setSelectedZone(e.target.value)}
            className="text-xs rounded border border-gray-300 py-1 px-2.5 bg-white text-gray-800"
          >
            <option value="all">All Mine Sectors ({zones.length})</option>
            {zones.map((z) => (
              <option key={z.id} value={z.id}>{z.code}: {z.name}</option>
            ))}
          </select>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={handleToggleStream}
            className={`inline-flex items-center text-xs font-medium px-3 py-1.5 rounded-full border transition-all ${
              isStreaming
                ? 'bg-emerald-50 border-emerald-300 text-emerald-700'
                : 'bg-gray-50 border-gray-200 text-gray-600 hover:bg-gray-100'
            }`}
          >
            <span className={`w-2 h-2 rounded-full mr-2 ${isStreaming ? 'bg-emerald-500 animate-pulse' : 'bg-gray-400'}`}></span>
            {isStreaming ? 'Live Stream Active (Streaming 3.5s)' : 'Start Real-Time Live Stream'}
          </button>

          <button
            onClick={handlePulse}
            className="text-xs text-blue-600 hover:text-blue-800 font-medium inline-flex items-center"
          >
            <RefreshCw size={13} className="mr-1.5" /> Single Pulse
          </button>
        </div>
      </div>

      {/* Main Grid: Sensor Cards on Left, Selected Sensor Trend on Right */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Sensor Grid (2 Columns on large screens) */}
        <div className="lg:col-span-2 grid grid-cols-1 md:grid-cols-2 gap-3.5 max-h-[580px] overflow-y-auto pr-1">
          {sensors.map((s) => {
            const isSelected = selectedSensor?.id === s.id;
            return (
              <div
                key={s.id}
                onClick={() => handleSelectSensor(s)}
                className={`p-4 rounded-lg border cursor-pointer transition-all ${
                  isSelected
                    ? 'border-blue-600 ring-1 ring-blue-600 bg-blue-50/20'
                    : s.is_alert
                    ? 'border-red-300 bg-red-50/30 hover:border-red-400'
                    : 'border-gray-200 bg-white hover:border-gray-300'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <span className="text-[10px] font-mono text-gray-400">{s.sensor_code}</span>
                    <h4 className="text-xs font-semibold text-gray-900 leading-tight">{s.name}</h4>
                    <span className="text-[11px] text-gray-500">{s.zone_name}</span>
                  </div>
                  <span className={`text-[11px] px-2 py-0.5 rounded font-medium ${
                    s.is_alert ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'
                  }`}>
                    {s.is_alert ? 'ANOMALY' : 'NORMAL'}
                  </span>
                </div>

                <div className="mt-3 flex items-baseline justify-between pt-2 border-t border-gray-100">
                  <span className="text-2xl font-bold text-gray-900">
                    {s.last_reading !== null ? `${s.last_reading} ${s.unit}` : 'N/A'}
                  </span>
                  <span className="text-[11px] text-gray-500">
                    Limit: {s.warning_threshold} {s.unit}
                  </span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Selected Sensor Deep-Dive & Time Series Chart */}
        <div className="bg-white p-5 rounded-lg border border-gray-200 flex flex-col justify-between">
          {selectedSensor ? (
            <div>
              <div className="border-b border-gray-100 pb-3 mb-4">
                <span className="text-[10px] font-mono text-gray-400">{selectedSensor.sensor_code}</span>
                <h3 className="text-sm font-semibold text-gray-900">{selectedSensor.name}</h3>
                <p className="text-xs text-gray-500 mt-0.5">{selectedSensor.zone_name}</p>
              </div>

              {/* DGMS Threshold Specs */}
              <div className="grid grid-cols-2 gap-2 mb-4 text-xs">
                <div className="p-2.5 bg-gray-50 rounded border border-gray-100">
                  <span className="text-[10px] text-gray-500 uppercase block">Advisory Warning</span>
                  <span className="font-semibold text-amber-700">{selectedSensor.warning_threshold} {selectedSensor.unit}</span>
                </div>
                <div className="p-2.5 bg-gray-50 rounded border border-gray-100">
                  <span className="text-[10px] text-gray-500 uppercase block">Critical Evacuation</span>
                  <span className="font-semibold text-red-700">{selectedSensor.danger_threshold} {selectedSensor.unit}</span>
                </div>
              </div>

              {/* Chart */}
              <div>
                <h4 className="text-xs font-semibold text-gray-800 mb-2">Historical Reading Trend (Chronological)</h4>
                {historyLoading ? (
                  <div className="h-44 flex items-center justify-center text-xs text-gray-400">Loading trend...</div>
                ) : (
                  <div className="h-44 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={history} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
                        <defs>
                          <linearGradient id="sensorGrad" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor={selectedSensor.is_alert ? '#EF4444' : '#2563EB'} stopOpacity={0.3}/>
                            <stop offset="95%" stopColor={selectedSensor.is_alert ? '#EF4444' : '#2563EB'} stopOpacity={0}/>
                          </linearGradient>
                        </defs>
                        <XAxis dataKey="time" tick={{ fontSize: 9, fill: '#6B7280' }} />
                        <YAxis tick={{ fontSize: 9, fill: '#6B7280' }} />
                        <Tooltip
                          formatter={(v) => [`${v} ${selectedSensor.unit}`, 'Value']}
                          contentStyle={{ backgroundColor: '#FFF', borderColor: '#E5E7EB', fontSize: 11, borderRadius: 6 }}
                        />
                        <Area
                          type="monotone"
                          dataKey="value"
                          stroke={selectedSensor.is_alert ? '#DC2626' : '#2563EB'}
                          fill="url(#sensorGrad)"
                          strokeWidth={2}
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                )}
              </div>

              <div className="mt-4 pt-3 border-t border-gray-100 text-[11px] text-gray-500">
                <span className="font-medium text-gray-700">Anomaly Detection Algorithm:</span> Scikit-learn Isolation Forest + DGMS Dynamic Envelope.
              </div>
            </div>
          ) : (
            <div className="h-48 flex items-center justify-center text-xs text-gray-400">
              Select a sensor card to view live telemetry trends.
            </div>
          )}
        </div>
      </div>

      {/* Manual Sensor Entry Modal */}
      <Modal
        isOpen={manualModalOpen}
        onClose={() => setManualModalOpen(false)}
        title="Submit Field IoT Sensor Reading"
      >
        <form onSubmit={handleManualSubmit} className="space-y-4 text-xs">
          <div>
            <label className="block font-medium text-gray-700 mb-1">Select IoT Sensor Instrument</label>
            <select
              required
              value={manualForm.sensor_id}
              onChange={(e) => setManualForm({ ...manualForm, sensor_id: e.target.value })}
              className="w-full text-xs rounded border border-gray-300 p-2 focus:ring-1 focus:ring-blue-500"
            >
              <option value="">-- Choose Sensor --</option>
              {sensors.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.sensor_code} - {s.name} ({s.unit}) [{s.zone_name}]
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block font-medium text-gray-700 mb-1">Recorded Metric Value</label>
            <input
              type="number"
              step="0.01"
              required
              value={manualForm.value}
              onChange={(e) => setManualForm({ ...manualForm, value: e.target.value })}
              placeholder="e.g. 1.45"
              className="w-full text-xs rounded border border-gray-300 p-2 focus:ring-1 focus:ring-blue-500"
            />
          </div>

          <div className="flex justify-end space-x-2 pt-3 border-t border-gray-200">
            <button
              type="button"
              onClick={() => setManualModalOpen(false)}
              className="px-3 py-1.5 rounded border border-gray-300 text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-3.5 py-1.5 rounded bg-blue-600 text-white hover:bg-blue-700 font-medium"
            >
              Ingest & Evaluate Telemetry
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default SensorMonitoring;

