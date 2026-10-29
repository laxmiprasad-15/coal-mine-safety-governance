import React, { useState, useEffect, useRef } from 'react';
import {
  HardHat, Upload, Camera, Check, X, ShieldAlert,
  AlertCircle, CheckCircle2, RefreshCw, FileCheck2, ChevronRight
} from 'lucide-react';
import { getPPEDetectionsApi, detectPPEApi, confirmPPEDetectionApi, getZonesApi } from '../services/api';
import Modal from '../components/Modal';

const PPEDetection = () => {
  const [detections, setDetections] = useState([]);
  const [zones, setZones] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedZone, setSelectedZone] = useState('1');
  const [uploading, setUploading] = useState(false);
  const [autoCreateCase, setAutoCreateCase] = useState(false);

  // Active detection inspection result
  const [activeResult, setActiveResult] = useState(null);

  // Confirmation Modal state
  const [confirmModalOpen, setConfirmModalOpen] = useState(false);
  const [targetDetection, setTargetDetection] = useState(null);
  const [officerNotes, setOfficerNotes] = useState('');

  const fileInputRef = useRef(null);

  const loadData = async () => {
    try {
      setLoading(true);
      const [detRes, zoneRes] = await Promise.all([
        getPPEDetectionsApi(),
        getZonesApi()
      ]);
      setDetections(detRes.data);
      setZones(zoneRes.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    try {
      setUploading(true);
      const formData = new FormData();
      formData.append('file', file);
      formData.append('zone_id', selectedZone);
      formData.append('auto_create_case', autoCreateCase);

      const res = await detectPPEApi(formData);
      setActiveResult(res.data);
      await loadData();
    } catch (err) {
      alert("Error analyzing PPE frame: " + (err.response?.data?.detail || err.message));
    } finally {
      setUploading(false);
    }
  };

  const handleQuickSample = async (sampleType) => {
    try {
      setUploading(true);
      // Fetch sample image blob from backend static uploads
      const url = sampleType === 'compliant'
        ? '/uploads/ppe/demo_worker_compliant.jpg'
        : '/uploads/ppe/demo_worker_frame.jpg';
      
      const response = await fetch(url);
      const blob = await response.blob();
      const file = new File([blob], `sample_${sampleType}.jpg`, { type: 'image/jpeg' });

      const formData = new FormData();
      formData.append('file', file);
      formData.append('zone_id', selectedZone);
      formData.append('auto_create_case', autoCreateCase);

      const res = await detectPPEApi(formData);
      setActiveResult(res.data);
      await loadData();
    } catch (err) {
      alert("Failed to load sample image: " + err.message);
    } finally {
      setUploading(false);
    }
  };

  const handleConfirmDecision = async (confirmed) => {
    if (!targetDetection) return;
    try {
      await confirmPPEDetectionApi(targetDetection.id, {
        confirmed,
        create_compliance_case: confirmed,
        notes: officerNotes || (confirmed ? "Verified on camera frame." : "Rejected false positive.")
      });
      setConfirmModalOpen(false);
      setTargetDetection(null);
      setOfficerNotes('');
      await loadData();
    } catch (e) {
      alert("Error confirming detection: " + e.message);
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-xl font-semibold text-gray-900 tracking-tight">AI Computer Vision PPE Detection</h2>
          <p className="text-xs text-gray-500 mt-1">
            YOLOv8 automated detection of Hardhats, High-Visibility Vests, Gloves, Goggles, and Safety Boots with human-in-the-loop verification.
          </p>
        </div>
        <div className="mt-3 md:mt-0 flex items-center space-x-2">
          <button
            onClick={() => handleQuickSample('violation')}
            disabled={uploading}
            className="text-xs font-medium px-3 py-1.5 rounded border border-red-200 bg-red-50 text-red-700 hover:bg-red-100 transition-colors"
          >
            Load Non-Compliant Sample
          </button>
          <button
            onClick={() => handleQuickSample('compliant')}
            disabled={uploading}
            className="text-xs font-medium px-3 py-1.5 rounded border border-green-200 bg-green-50 text-green-700 hover:bg-green-100 transition-colors"
          >
            Load Compliant Sample
          </button>
        </div>
      </div>

      {/* Upload and Live Inspection Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Upload & Configuration Card */}
        <div className="bg-white p-5 rounded-lg border border-gray-200 space-y-4">
          <h3 className="text-sm font-semibold text-gray-900">Upload Video Frame or Image</h3>
          
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Target Monitoring Sector</label>
            <select
              value={selectedZone}
              onChange={(e) => setSelectedZone(e.target.value)}
              className="w-full text-xs rounded border border-gray-300 p-2 focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
            >
              {zones.map((z) => (
                <option key={z.id} value={z.id}>{z.code}: {z.name}</option>
              ))}
            </select>
          </div>

          <div className="flex items-center space-x-2 pt-1">
            <input
              type="checkbox"
              id="autoCase"
              checked={autoCreateCase}
              onChange={(e) => setAutoCreateCase(e.target.checked)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500 h-4 w-4"
            />
            <label htmlFor="autoCase" className="text-xs text-gray-700 cursor-pointer">
              Auto-create Compliance Case on violation
            </label>
          </div>

          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileUpload}
            accept="image/*"
            className="hidden"
          />

          <div
            onClick={() => fileInputRef.current?.click()}
            className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-500 hover:bg-blue-50/20 cursor-pointer transition-colors"
          >
            <Upload className="mx-auto h-8 w-8 text-gray-400 mb-2" />
            <p className="text-xs font-medium text-gray-900">Click to upload camera snapshot</p>
            <p className="text-[11px] text-gray-500 mt-0.5">JPG, PNG, or video frame</p>
          </div>

          {uploading && (
            <div className="flex items-center justify-center space-x-2 text-xs text-blue-600 font-medium py-2">
              <RefreshCw className="animate-spin" size={14} />
              <span>Running YOLOv8 PPE inference...</span>
            </div>
          )}

          <div className="pt-2 border-t border-gray-100 text-[11px] text-gray-500">
            <p className="font-semibold text-gray-700 mb-1">Detected Mandatory Classes:</p>
            <div className="flex flex-wrap gap-1">
              {['Hardhat', 'Safety Vest', 'Gloves', 'Goggles', 'Boots', 'NO-PPE'].map((c) => (
                <span key={c} className="px-1.5 py-0.5 rounded bg-gray-100 border border-gray-200 text-[10px]">
                  {c}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Live Annotated Output Screen */}
        <div className="lg:col-span-2 bg-white p-5 rounded-lg border border-gray-200 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-semibold text-gray-900">YOLOv8 Detection Feed & Bounding Boxes</h3>
              {activeResult && (
                <span className="text-xs font-mono px-2 py-0.5 rounded bg-gray-100 text-gray-700 border border-gray-200">
                  Confidence: {Math.round(activeResult.confidence * 100)}%
                </span>
              )}
            </div>

            {activeResult ? (
              <div className="space-y-4">
                <div className="flex flex-col md:flex-row gap-4 items-start">
                  <div className="flex-1 bg-black rounded-lg overflow-hidden border border-gray-200 max-h-72 flex items-center justify-center">
                    <img
                      src={activeResult.annotated_image_path || activeResult.image_path}
                      alt="Annotated Detection"
                      className="max-h-72 object-contain"
                    />
                  </div>

                  <div className="w-full md:w-64 space-y-3">
                    <div className="p-3 bg-gray-50 rounded border border-gray-200 text-xs">
                      <span className="text-gray-500 block mb-0.5">Classification Result:</span>
                      <p className={`font-semibold text-sm ${
                        activeResult.violation_type.includes('Compliant') ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {activeResult.violation_type}
                      </p>
                      <p className="text-[11px] text-gray-500 mt-1">Sector: {activeResult.zone_name}</p>
                    </div>

                    <div>
                      <h4 className="text-xs font-medium text-gray-700 mb-1.5">Detected Object Classes:</h4>
                      <div className="space-y-1">
                        {(activeResult.detections || []).map((det, i) => (
                          <div key={i} className="flex items-center justify-between text-xs p-1.5 rounded bg-gray-50 border border-gray-100">
                            <span className="font-medium text-gray-800">{det.class}</span>
                            <span className="text-[11px] font-mono text-gray-500">{Math.round(det.confidence * 100)}%</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Safety Officer Manual Confirmation Bar */}
                {activeResult.status === 'Pending Confirmation' && (
                  <div className="p-3 bg-amber-50 rounded border border-amber-200 flex items-center justify-between">
                    <div>
                      <p className="text-xs font-semibold text-amber-900">Safety Officer Verification Required</p>
                      <p className="text-[11px] text-amber-800">Confirm detection to generate a traceable regulatory compliance case.</p>
                    </div>
                    <div className="flex space-x-2">
                      <button
                        onClick={() => {
                          setTargetDetection(activeResult);
                          setConfirmModalOpen(true);
                        }}
                        className="px-3 py-1 text-xs font-medium rounded bg-blue-600 text-white hover:bg-blue-700"
                      >
                        Review & Confirm
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="h-64 border border-dashed border-gray-200 rounded-lg flex flex-col items-center justify-center text-gray-400 p-6 text-center">
                <Camera size={32} className="mb-2 text-gray-300" />
                <p className="text-xs font-medium text-gray-700">No active camera snapshot selected</p>
                <p className="text-[11px] text-gray-400 mt-0.5">Upload an image or select a sample button above to test real-time PPE detection.</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Historical PPE Detections Table */}
      <div className="bg-white rounded-lg border border-gray-200 p-5">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-semibold text-gray-900">PPE Detections & Verification History</h3>
            <p className="text-xs text-gray-500">Audit record of computer vision optical detections</p>
          </div>
          <button onClick={loadData} className="p-1.5 text-gray-400 hover:text-gray-600 rounded">
            <RefreshCw size={14} />
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-gray-50 text-gray-500 border-y border-gray-200">
              <tr>
                <th className="py-2.5 px-3">Date / Timestamp</th>
                <th className="py-2.5 px-3">Sector</th>
                <th className="py-2.5 px-3">Detected Violation</th>
                <th className="py-2.5 px-3">Confidence</th>
                <th className="py-2.5 px-3">Status</th>
                <th className="py-2.5 px-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 text-gray-700">
              {detections.map((d) => (
                <tr key={d.id} className="hover:bg-gray-50/60">
                  <td className="py-2.5 px-3 font-mono text-gray-500">
                    {new Date(d.created_at).toLocaleString()}
                  </td>
                  <td className="py-2.5 px-3 font-medium text-gray-900">{d.zone_name}</td>
                  <td className="py-2.5 px-3">
                    <span className={`font-medium ${
                      d.violation_type.includes('Compliant') ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {d.violation_type}
                    </span>
                  </td>
                  <td className="py-2.5 px-3">{Math.round(d.confidence * 100)}%</td>
                  <td className="py-2.5 px-3">
                    <span className={`inline-block px-2 py-0.5 rounded text-[11px] font-medium ${
                      d.status === 'Confirmed' ? 'bg-amber-100 text-amber-800' :
                      d.status === 'Case Created' ? 'bg-blue-100 text-blue-800' :
                      d.status === 'Compliant' ? 'bg-green-100 text-green-800' :
                      d.status === 'Pending Confirmation' ? 'bg-purple-100 text-purple-800' : 'bg-gray-100 text-gray-700'
                    }`}>
                      {d.status}
                    </span>
                  </td>
                  <td className="py-2.5 px-3 text-right space-x-1">
                    <button
                      onClick={() => setActiveResult(d)}
                      className="px-2 py-1 rounded bg-gray-100 hover:bg-gray-200 text-gray-700 text-[11px]"
                    >
                      Inspect
                    </button>
                    {d.status === 'Pending Confirmation' && (
                      <button
                        onClick={() => {
                          setTargetDetection(d);
                          setConfirmModalOpen(true);
                        }}
                        className="px-2 py-1 rounded bg-blue-50 text-blue-700 hover:bg-blue-100 text-[11px] font-medium"
                      >
                        Verify
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Safety Officer Confirmation Modal */}
      <Modal
        isOpen={confirmModalOpen}
        onClose={() => setConfirmModalOpen(false)}
        title="Safety Officer Decision: Confirm / Reject AI Detection"
      >
        {targetDetection && (
          <div className="space-y-4 text-xs">
            <div className="p-3 bg-gray-50 rounded border border-gray-200">
              <p className="font-semibold text-gray-900">{targetDetection.violation_type}</p>
              <p className="text-gray-500 mt-0.5">Location: {targetDetection.zone_name} | AI Confidence: {Math.round(targetDetection.confidence * 100)}%</p>
            </div>

            <div>
              <label className="block font-medium text-gray-700 mb-1">
                Official Statutory Verification Remarks
              </label>
              <textarea
                rows={3}
                value={officerNotes}
                onChange={(e) => setOfficerNotes(e.target.value)}
                placeholder="Enter field verification notes, responsible crew details, or reason for dismissal..."
                className="w-full text-xs rounded border border-gray-300 p-2.5 focus:ring-1 focus:ring-blue-500"
              />
            </div>

            <div className="flex justify-end space-x-3 pt-3 border-t border-gray-200">
              <button
                onClick={() => handleConfirmDecision(false)}
                className="px-3.5 py-1.5 rounded border border-gray-300 text-gray-700 hover:bg-gray-50 font-medium"
              >
                Reject (False Positive)
              </button>
              <button
                onClick={() => handleConfirmDecision(true)}
                className="px-3.5 py-1.5 rounded bg-blue-600 text-white hover:bg-blue-700 font-medium"
              >
                Confirm & Create Compliance Case
              </button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default PPEDetection;

