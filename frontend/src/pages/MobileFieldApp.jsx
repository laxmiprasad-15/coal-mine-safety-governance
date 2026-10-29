import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  MapPin, Camera, AlertTriangle, ShieldCheck, CheckCircle2,
  Wifi, WifiOff, UploadCloud, Users, ArrowLeft, RefreshCw, Send,
  FileText, Clock, HardHat, Sparkles
} from 'lucide-react';
import axios from 'axios';

const SUBSIDIARY_NAMES = {
  BCCL: 'Bharat Coking Coal Limited (Dhanbad)',
  ECL: 'Eastern Coalfields Limited (Sanctoria)',
  CCL: 'Central Coalfields Limited (Ranchi)',
  WCL: 'Western Coalfields Limited (Nagpur)',
  SECL: 'South Eastern Coalfields (Bilaspur)',
  MCL: 'Mahanadi Coalfields (Sambalpur)',
  NCL: 'Northern Coalfields (Singrauli)',
  SCCL: 'Singareni Collieries (Telangana)'
};

export default function MobileFieldApp() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('inspect'); // inspect, history, contractor, sync
  const [coords, setCoords] = useState({ lat: 23.7957, lng: 86.4304, accuracy: 4.2 });
  const [gpsLocked, setGpsLocked] = useState(false);
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [inspections, setInspections] = useState([]);
  const [offlineQueue, setOfflineQueue] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('coal_mine_offline_inspections') || '[]');
    } catch {
      return [];
    }
  });

  // Form State
  const [locationName, setLocationName] = useState('Haul Road No. 4 Junction (BCCL Jharia)');
  const [inspectionType, setInspectionType] = useState('Safety Observation');
  const [hazardLevel, setHazardLevel] = useState('Medium');
  const [observationNotes, setObservationNotes] = useState('');
  const [recommendation, setRecommendation] = useState('');
  const [photoPreview, setPhotoPreview] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');

  // Contractor verify state
  const [contractorCode, setContractorCode] = useState('CONT-BGC-01');
  const [contractorResult, setContractorResult] = useState(null);

  // GPS Geolocation Hook
  useEffect(() => {
    if ('geolocation' in navigator) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          setCoords({
            lat: Number(pos.coords.latitude.toFixed(5)),
            lng: Number(pos.coords.longitude.toFixed(5)),
            accuracy: Math.round(pos.coords.accuracy)
          });
          setGpsLocked(true);
        },
        () => {
          // Fallback to Jharia Coalfield Coordinates
          setCoords({ lat: 23.7957, lng: 86.4304, accuracy: 5 });
          setGpsLocked(true);
        },
        { enableHighAccuracy: true, timeout: 5000 }
      );
    }

    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    loadRecentInspections();

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  const loadRecentInspections = async () => {
    try {
      const res = await axios.get('/api/v1/inspections/');
      setInspections(res.data);
    } catch (e) {
      console.error(e);
    }
  };

  const handlePhotoCapture = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setPhotoPreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!observationNotes) return;

    setSubmitting(true);
    const payload = {
      zone_id: 1,
      latitude: coords.lat,
      longitude: coords.lng,
      location_name: locationName,
      inspection_type: inspectionType,
      hazard_level: hazardLevel,
      observation_notes: observationNotes,
      corrective_recommendation: recommendation,
      photo_url: photoPreview || null,
      is_offline_synced: !isOnline
    };

    if (!isOnline) {
      // Store in offline queue
      const updatedQueue = [...offlineQueue, { ...payload, timestamp: new Date().toISOString() }];
      setOfflineQueue(updatedQueue);
      localStorage.setItem('coal_mine_offline_inspections', JSON.stringify(updatedQueue));
      setSuccessMsg('Saved to offline storage. Will auto-sync when network returns.');
      resetForm();
      setSubmitting(false);
      return;
    }

    try {
      await axios.post('/api/v1/inspections/', payload);
      setSuccessMsg('Inspection & Geo-Tag successfully transmitted to Ministry / DGMS Portal!');
      resetForm();
      loadRecentInspections();
    } catch (err) {
      // Fallback to offline on error
      const updatedQueue = [...offlineQueue, { ...payload, timestamp: new Date().toISOString() }];
      setOfflineQueue(updatedQueue);
      localStorage.setItem('coal_mine_offline_inspections', JSON.stringify(updatedQueue));
      setSuccessMsg('Network issue. Observation queued offline locally.');
      resetForm();
    } finally {
      setSubmitting(false);
    }
  };

  const handleSyncOffline = async () => {
    if (offlineQueue.length === 0) return;
    try {
      setSubmitting(true);
      await axios.post('/api/v1/inspections/sync-offline', offlineQueue);
      setOfflineQueue([]);
      localStorage.removeItem('coal_mine_offline_inspections');
      setSuccessMsg(`Successfully synchronized all offline field inspections!`);
      loadRecentInspections();
    } catch (err) {
      alert('Sync failed: ' + err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleVerifyContractor = async () => {
    try {
      const res = await axios.get('/api/v1/contractors/');
      const match = res.data.find(c => c.code.toLowerCase() === contractorCode.toLowerCase());
      setContractorResult(match || { not_found: true });
    } catch (e) {
      console.error(e);
    }
  };

  const resetForm = () => {
    setObservationNotes('');
    setRecommendation('');
    setPhotoPreview(null);
    setTimeout(() => setSuccessMsg(''), 4500);
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col font-sans max-w-md mx-auto shadow-2xl relative pb-20">
      {/* Mobile Top Bar */}
      <header className="bg-slate-950 border-b border-slate-800 p-4 sticky top-0 z-30 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <button
            onClick={() => navigate('/')}
            className="p-1.5 rounded-lg bg-slate-800 text-slate-300 hover:text-white"
            title="Switch to Web Dashboard"
          >
            <ArrowLeft size={18} />
          </button>
          <div>
            <h1 className="text-sm font-bold text-white flex items-center tracking-wide">
              <HardHat size={16} className="text-amber-500 mr-1.5" />
              MINE FIELD APP
            </h1>
            <p className="text-[10px] text-slate-400">DGMS Field Inspection v2.4</p>
          </div>
        </div>

        {/* Network & GPS Pills */}
        <div className="flex items-center space-x-2">
          <div className={`px-2 py-0.5 rounded-full text-[10px] font-medium flex items-center ${
            isOnline ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' : 'bg-amber-950 text-amber-400 border border-amber-800 animate-pulse'
          }`}>
            {isOnline ? <Wifi size={10} className="mr-1" /> : <WifiOff size={10} className="mr-1" />}
            {isOnline ? 'LIVE' : 'OFFLINE'}
          </div>

          <div className="px-2 py-0.5 rounded-full text-[10px] bg-blue-950 text-blue-400 border border-blue-800 flex items-center">
            <MapPin size={10} className="mr-1 text-blue-400" />
            GPS: ±{coords.accuracy}m
          </div>
        </div>
      </header>

      {/* Live GPS Ribbon */}
      <div className="bg-slate-800/80 px-4 py-2 text-[11px] text-slate-300 flex items-center justify-between border-b border-slate-700/60 backdrop-blur">
        <div className="flex items-center space-x-1.5 truncate">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping"></span>
          <span className="font-mono text-emerald-400">
            {coords.lat.toFixed(4)}°N, {coords.lng.toFixed(4)}°E
          </span>
          <span className="text-slate-400 truncate">| Jharia Coalfield</span>
        </div>
        <span className="text-[10px] text-slate-400 whitespace-nowrap">
          {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </span>
      </div>

      {/* Success Notification Banner */}
      {successMsg && (
        <div className="mx-4 mt-3 p-3 rounded-lg bg-emerald-950/90 border border-emerald-700 text-emerald-200 text-xs flex items-center space-x-2 animate-fade-in">
          <CheckCircle2 size={16} className="text-emerald-400 flex-shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}

      {/* Main Container */}
      <main className="p-4 flex-1 space-y-4">
        {activeTab === 'inspect' && (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="bg-slate-800/60 border border-slate-700/80 rounded-xl p-4 space-y-3">
              <h2 className="text-xs font-semibold text-slate-200 uppercase tracking-wider flex items-center">
                <ShieldCheck size={14} className="text-amber-400 mr-1.5" />
                Geo-Tagged Safety Observation
              </h2>

              {/* Location Select */}
              <div>
                <label className="text-[11px] text-slate-400 block mb-1">Mine Inspection Sector</label>
                <select
                  value={locationName}
                  onChange={(e) => setLocationName(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg text-xs p-2.5 text-white focus:outline-none focus:border-blue-500"
                >
                  <option value="Haul Road No. 4 Junction (BCCL Jharia)">Haul Road No. 4 Junction (BCCL Jharia)</option>
                  <option value="Working Face 4A Support Line (Moonidih)">Working Face 4A Support Line (Moonidih)</option>
                  <option value="Main Incline & Pithead Entry">Main Incline & Pithead Entry</option>
                  <option value="Conveyor Belt Transfer Point 2">Conveyor Belt Transfer Point 2</option>
                  <option value="Explosive Magazine Approach">Explosive Magazine Approach</option>
                  <option value="Ventilation Return District 1">Ventilation Return District 1</option>
                </select>
              </div>

              {/* Category & Hazard Level Grid */}
              <div className="grid grid-cols-2 gap-2.5">
                <div>
                  <label className="text-[11px] text-slate-400 block mb-1">Observation Type</label>
                  <select
                    value={inspectionType}
                    onChange={(e) => setInspectionType(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg text-xs p-2.5 text-white"
                  >
                    <option value="Safety Observation">Safety Observation</option>
                    <option value="PPE Compliance">PPE Non-Compliance</option>
                    <option value="Roof & Strata Control">Roof / Strata Control</option>
                    <option value="Gas / Ventilation Check">Ventilation Deficit</option>
                    <option value="Haul Road & Machinery">Haul Road / Dump</option>
                    <option value="Statutory CMR Blasting">Blasting Clearance</option>
                  </select>
                </div>

                <div>
                  <label className="text-[11px] text-slate-400 block mb-1">Risk Severity</label>
                  <select
                    value={hazardLevel}
                    onChange={(e) => setHazardLevel(e.target.value)}
                    className={`w-full border rounded-lg text-xs p-2.5 font-bold ${
                      hazardLevel === 'Critical' ? 'bg-red-950/80 border-red-700 text-red-300' :
                      hazardLevel === 'High' ? 'bg-amber-950/80 border-amber-700 text-amber-300' :
                      hazardLevel === 'Medium' ? 'bg-yellow-950/80 border-yellow-700 text-yellow-300' :
                      'bg-emerald-950/80 border-emerald-700 text-emerald-300'
                    }`}
                  >
                    <option value="Low">Low Risk</option>
                    <option value="Medium">Medium Hazard</option>
                    <option value="High">High Violation</option>
                    <option value="Critical">Critical Emergency</option>
                  </select>
                </div>
              </div>

              {/* Observation Notes */}
              <div>
                <label className="text-[11px] text-slate-400 block mb-1">Field Findings & Deficiencies</label>
                <textarea
                  rows={3}
                  value={observationNotes}
                  onChange={(e) => setObservationNotes(e.target.value)}
                  placeholder="e.g. Dumper operator working without high-vis vest near loading shovel. Water spraying not executed..."
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg text-xs p-2.5 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
                  required
                />
              </div>

              {/* Corrective Recommendation */}
              <div>
                <label className="text-[11px] text-slate-400 block mb-1">Recommended Corrective Action</label>
                <input
                  type="text"
                  value={recommendation}
                  onChange={(e) => setRecommendation(e.target.value)}
                  placeholder="e.g. Issue immediate stop-work or reassign water tanker"
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg text-xs p-2 text-white placeholder-slate-500"
                />
              </div>

              {/* Photo Evidence Capture */}
              <div>
                <label className="text-[11px] text-slate-400 block mb-1">Photo Evidence (Geo-Stamped)</label>
                <div className="flex items-center space-x-3">
                  <label className="flex-1 border-2 border-dashed border-slate-700 hover:border-slate-500 rounded-lg p-3 text-center cursor-pointer bg-slate-900/50">
                    <Camera size={18} className="mx-auto text-slate-400 mb-1" />
                    <span className="text-[11px] text-slate-300 block">Tap to Open Camera / Upload</span>
                    <input
                      type="file"
                      accept="image/*"
                      capture="environment"
                      onChange={handlePhotoCapture}
                      className="hidden"
                    />
                  </label>

                  {photoPreview && (
                    <div className="relative w-16 h-16 rounded-lg overflow-hidden border border-slate-700">
                      <img src={photoPreview} alt="Preview" className="w-full h-full object-cover" />
                    </div>
                  )}
                </div>
              </div>
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="w-full bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs py-3.5 rounded-xl shadow-lg shadow-blue-900/40 flex items-center justify-center space-x-2 transition disabled:opacity-50"
            >
              <Send size={15} />
              <span>{submitting ? 'Transmitting Geo-Record...' : 'Submit Geo-Tagged Observation'}</span>
            </button>
          </form>
        )}

        {/* Tab 2: Recent Inspections Log */}
        {activeTab === 'history' && (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h2 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                Recent Field Logs ({inspections.length})
              </h2>
              <button
                onClick={loadRecentInspections}
                className="text-[11px] text-blue-400 flex items-center"
              >
                <RefreshCw size={12} className="mr-1" /> Refresh
              </button>
            </div>

            <div className="space-y-2.5">
              {inspections.map((item) => (
                <div key={item.id} className="bg-slate-800/60 border border-slate-700/80 rounded-xl p-3 text-xs space-y-1.5">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-white truncate max-w-[200px]">
                      {item.location_name}
                    </span>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      item.hazard_level === 'Critical' ? 'bg-red-950 text-red-400 border border-red-800' :
                      item.hazard_level === 'High' ? 'bg-amber-950 text-amber-400 border border-amber-800' :
                      item.hazard_level === 'Medium' ? 'bg-yellow-950 text-yellow-400 border border-yellow-800' :
                      'bg-emerald-950 text-emerald-400 border border-emerald-800'
                    }`}>
                      {item.hazard_level}
                    </span>
                  </div>

                  <p className="text-slate-300 text-[11px] leading-relaxed">
                    {item.observation_notes}
                  </p>

                  <div className="flex items-center justify-between text-[10px] text-slate-400 pt-1 border-t border-slate-700/50">
                    <span className="font-mono text-emerald-400 flex items-center">
                      <MapPin size={9} className="mr-0.5" />
                      {item.latitude ? `${item.latitude.toFixed(3)}, ${item.longitude.toFixed(3)}` : 'Jharia Sector'}
                    </span>
                    <span>
                      {new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Tab 3: Contractor Verification on Site */}
        {activeTab === 'contractor' && (
          <div className="space-y-4">
            <div className="bg-slate-800/60 border border-slate-700/80 rounded-xl p-4 space-y-3">
              <h2 className="text-xs font-semibold text-slate-200 uppercase tracking-wider flex items-center">
                <Users size={14} className="text-blue-400 mr-1.5" />
                Contractor Field Clearance Check
              </h2>
              <p className="text-[11px] text-slate-400">
                Verify statutory Form B labor registers, PME medical certificates, and VTC induction in the field.
              </p>

              <div className="flex space-x-2">
                <input
                  type="text"
                  value={contractorCode}
                  onChange={(e) => setContractorCode(e.target.value.toUpperCase())}
                  placeholder="CONT-BGC-01"
                  className="flex-1 bg-slate-900 border border-slate-700 rounded-lg text-xs p-2 text-white font-mono uppercase"
                />
                <button
                  type="button"
                  onClick={handleVerifyContractor}
                  className="bg-blue-600 hover:bg-blue-500 text-white text-xs px-3.5 py-2 rounded-lg font-medium"
                >
                  Verify
                </button>
              </div>

              {contractorResult && (
                <div className={`p-3 rounded-lg border text-xs space-y-2 ${
                  contractorResult.not_found ? 'bg-red-950/60 border-red-700' : 'bg-slate-900 border-slate-700'
                }`}>
                  {contractorResult.not_found ? (
                    <p className="text-red-300 font-semibold">❌ Contractor code not recognized in DGMS portal.</p>
                  ) : (
                    <>
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-white">{contractorResult.name}</span>
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-blue-900 text-blue-300 font-mono">
                          {contractorResult.subsidiary}
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-400">{contractorResult.category}</p>

                      <div className="grid grid-cols-3 gap-2 pt-1 border-t border-slate-800 text-center">
                        <div className="bg-slate-800/80 p-1.5 rounded">
                          <span className="text-[10px] text-slate-400 block">PME (Form O)</span>
                          <span className={`text-[11px] font-bold ${contractorResult.pme_valid ? 'text-emerald-400' : 'text-red-400'}`}>
                            {contractorResult.pme_valid ? 'VALID ✓' : 'EXPIRED ✗'}
                          </span>
                        </div>
                        <div className="bg-slate-800/80 p-1.5 rounded">
                          <span className="text-[10px] text-slate-400 block">VTC Trained</span>
                          <span className={`text-[11px] font-bold ${contractorResult.vtc_trained ? 'text-emerald-400' : 'text-red-400'}`}>
                            {contractorResult.vtc_trained ? 'PASS ✓' : 'DUE ✗'}
                          </span>
                        </div>
                        <div className="bg-slate-800/80 p-1.5 rounded">
                          <span className="text-[10px] text-slate-400 block">Compliance</span>
                          <span className="text-[11px] font-bold text-amber-400">
                            {contractorResult.compliance_score}%
                          </span>
                        </div>
                      </div>
                    </>
                  )}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Tab 4: Offline Queue & Sync */}
        {activeTab === 'sync' && (
          <div className="bg-slate-800/60 border border-slate-700/80 rounded-xl p-4 space-y-3">
            <h2 className="text-xs font-semibold text-slate-200 uppercase tracking-wider flex items-center">
              <UploadCloud size={15} className="text-amber-400 mr-1.5" />
              Offline Buffer & Cloud Sync
            </h2>
            <p className="text-[11px] text-slate-400">
              When mining underground beyond Wi-Fi / 4G coverage, inspections are securely buffered in device storage.
            </p>

            <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 flex items-center justify-between">
              <div>
                <span className="text-xs font-semibold text-white block">Queued Records</span>
                <span className="text-[11px] text-slate-400">{offlineQueue.length} field reports pending upload</span>
              </div>
              <span className={`text-base font-bold ${offlineQueue.length > 0 ? 'text-amber-400' : 'text-emerald-400'}`}>
                {offlineQueue.length}
              </span>
            </div>

            <button
              onClick={handleSyncOffline}
              disabled={offlineQueue.length === 0 || submitting}
              className="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs py-3 rounded-xl flex items-center justify-center space-x-2 disabled:opacity-40"
            >
              <UploadCloud size={15} />
              <span>{submitting ? 'Synchronizing...' : 'Sync Queued Records to Cloud'}</span>
            </button>
          </div>
        )}
      </main>

      {/* Mobile Bottom Navigation Bar */}
      <nav className="fixed bottom-0 left-0 right-0 max-w-md mx-auto bg-slate-950/95 border-t border-slate-800 p-2 flex items-center justify-around z-40 backdrop-blur">
        <button
          onClick={() => setActiveTab('inspect')}
          className={`flex flex-col items-center py-1 px-3 rounded-lg text-[10px] font-medium transition ${
            activeTab === 'inspect' ? 'text-blue-400 bg-blue-950/50' : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <Camera size={18} className="mb-0.5" />
          <span>Inspect</span>
        </button>

        <button
          onClick={() => setActiveTab('history')}
          className={`flex flex-col items-center py-1 px-3 rounded-lg text-[10px] font-medium transition ${
            activeTab === 'history' ? 'text-blue-400 bg-blue-950/50' : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <Clock size={18} className="mb-0.5" />
          <span>Field Logs</span>
        </button>

        <button
          onClick={() => setActiveTab('contractor')}
          className={`flex flex-col items-center py-1 px-3 rounded-lg text-[10px] font-medium transition ${
            activeTab === 'contractor' ? 'text-blue-400 bg-blue-950/50' : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <Users size={18} className="mb-0.5" />
          <span>Contractors</span>
        </button>

        <button
          onClick={() => setActiveTab('sync')}
          className={`flex flex-col items-center py-1 px-3 rounded-lg text-[10px] font-medium relative transition ${
            activeTab === 'sync' ? 'text-blue-400 bg-blue-950/50' : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <UploadCloud size={18} className="mb-0.5" />
          <span>Sync</span>
          {offlineQueue.length > 0 && (
            <span className="absolute top-0.5 right-2 w-2 h-2 rounded-full bg-amber-500 animate-pulse"></span>
          )}
        </button>
      </nav>
    </div>
  );
}
