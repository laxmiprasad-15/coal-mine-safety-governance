import React, { useState, useEffect } from 'react';
import {
  FileCheck2, Search, Filter, Plus, Clock, AlertTriangle,
  CheckCircle2, User, ArrowUpRight, MessageSquare, Send, X, ExternalLink
} from 'lucide-react';
import { getCasesApi, getCaseDetailsApi, createCaseApi, updateCaseApi, addCaseCommentApi, getZonesApi } from '../services/api';
import RiskBadge from '../components/RiskBadge';
import Modal from '../components/Modal';

const CATEGORIES = ['All', 'PPE', 'Environmental', 'Equipment', 'Worker Health', 'Inspection', 'Operational'];
const STATUSES = ['All', 'Open', 'In Progress', 'Pending Verification', 'Closed', 'Overdue'];
const RISK_LEVELS = ['All', 'Low', 'Medium', 'High', 'Critical'];

const ComplianceCases = () => {
  const [cases, setCases] = useState([]);
  const [zones, setZones] = useState([]);
  const [loading, setLoading] = useState(true);

  // Filters
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [selectedStatus, setSelectedStatus] = useState('All');
  const [selectedRisk, setSelectedRisk] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');

  // Details Modal
  const [detailsModalOpen, setDetailsModalOpen] = useState(false);
  const [activeCaseDetails, setActiveCaseDetails] = useState(null);
  const [detailsLoading, setDetailsLoading] = useState(false);
  const [commentInput, setCommentInput] = useState('');

  // Create Case Modal
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [newCaseForm, setNewCaseForm] = useState({
    title: '',
    category: 'Environmental',
    source: 'Manual Inspection',
    risk_level: 'Medium',
    risk_score: 45.0,
    zone_id: '1',
    deadline: '',
    corrective_action_summary: ''
  });

  const loadCases = async () => {
    try {
      setLoading(true);
      const params = {};
      if (selectedCategory !== 'All') params.category = selectedCategory;
      if (selectedStatus !== 'All') params.status = selectedStatus;
      if (selectedRisk !== 'All') params.risk_level = selectedRisk;
      if (searchQuery.trim()) params.search = searchQuery.trim();

      const [cRes, zRes] = await Promise.all([
        getCasesApi(params),
        getZonesApi()
      ]);
      setCases(cRes.data);
      setZones(zRes.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCases();
  }, [selectedCategory, selectedStatus, selectedRisk]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    loadCases();
  };

  const handleOpenDetails = async (caseId) => {
    try {
      setDetailsModalOpen(true);
      setDetailsLoading(true);
      const res = await getCaseDetailsApi(caseId);
      setActiveCaseDetails(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setDetailsLoading(false);
    }
  };

  const handleUpdateStatus = async (newStatus) => {
    if (!activeCaseDetails) return;
    try {
      await updateCaseApi(activeCaseDetails.case.id, {
        status: newStatus,
        verification_remarks: newStatus === 'Closed' ? 'Verified on-site by statutory authority.' : undefined
      });
      const updated = await getCaseDetailsApi(activeCaseDetails.case.id);
      setActiveCaseDetails(updated.data);
      await loadCases();
    } catch (e) {
      alert("Error updating case: " + e.message);
    }
  };

  const handleAddComment = async (e) => {
    e.preventDefault();
    if (!commentInput.trim() || !activeCaseDetails) return;

    try {
      await addCaseCommentApi(activeCaseDetails.case.id, commentInput.trim());
      setCommentInput('');
      const updated = await getCaseDetailsApi(activeCaseDetails.case.id);
      setActiveCaseDetails(updated.data);
    } catch (e) {
      alert("Error adding comment: " + e.message);
    }
  };

  const handleCreateCaseSubmit = async (e) => {
    e.preventDefault();
    try {
      const deadlineDate = newCaseForm.deadline
        ? new Date(newCaseForm.deadline).toISOString()
        : new Date(Date.now() + 24 * 3600 * 1000).toISOString();

      await createCaseApi({
        title: newCaseForm.title,
        category: newCaseForm.category,
        source: newCaseForm.source,
        risk_level: newCaseForm.risk_level,
        risk_score: Number(newCaseForm.risk_score),
        zone_id: Number(newCaseForm.zone_id),
        deadline: deadlineDate,
        corrective_action_summary: newCaseForm.corrective_action_summary
      });
      setCreateModalOpen(false);
      setNewCaseForm({
        title: '',
        category: 'Environmental',
        source: 'Manual Inspection',
        risk_level: 'Medium',
        risk_score: 45.0,
        zone_id: '1',
        deadline: '',
        corrective_action_summary: ''
      });
      await loadCases();
    } catch (err) {
      alert("Error creating case: " + err.message);
    }
  };

  const getStatusBadge = (status) => {
    const s = status.toLowerCase();
    if (s === 'closed') return 'bg-green-100 text-green-800';
    if (s === 'overdue') return 'bg-red-100 text-red-800 font-semibold';
    if (s === 'pending verification') return 'bg-purple-100 text-purple-800';
    if (s === 'in progress') return 'bg-blue-100 text-blue-800';
    return 'bg-amber-100 text-amber-800';
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-xl font-semibold text-gray-900 tracking-tight">Compliance Case Governance Ledger</h2>
          <p className="text-xs text-gray-500 mt-1">
            End-to-end traceable compliance lifecycle: Detection → AI Assessment → Case Creation → Action Assignment → Verification → Closure.
          </p>
        </div>
        <div className="mt-3 md:mt-0 flex items-center space-x-2">
          <button
            onClick={() => setCreateModalOpen(true)}
            className="inline-flex items-center text-xs font-medium px-3 py-1.5 rounded bg-blue-600 text-white hover:bg-blue-700"
          >
            <Plus size={14} className="mr-1.5" />
            Initiate Compliance Case
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white p-4 rounded-lg border border-gray-200 flex flex-col md:flex-row md:items-center md:justify-between gap-3 text-xs">
        <form onSubmit={handleSearchSubmit} className="relative flex-1 max-w-sm">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by case #, keyword, hazard..."
            className="w-full text-xs rounded border border-gray-300 pl-8 pr-3 py-1.5 focus:ring-1 focus:ring-blue-500"
          />
          <Search size={14} className="absolute left-2.5 top-2.5 text-gray-400" />
        </form>

        <div className="flex flex-wrap items-center gap-2">
          <div className="flex items-center space-x-1.5">
            <span className="text-gray-500">Category:</span>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="text-xs rounded border border-gray-300 py-1 px-2 bg-white text-gray-800"
            >
              {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>

          <div className="flex items-center space-x-1.5">
            <span className="text-gray-500">Status:</span>
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="text-xs rounded border border-gray-300 py-1 px-2 bg-white text-gray-800"
            >
              {STATUSES.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>

          <div className="flex items-center space-x-1.5">
            <span className="text-gray-500">Risk:</span>
            <select
              value={selectedRisk}
              onChange={(e) => setSelectedRisk(e.target.value)}
              className="text-xs rounded border border-gray-300 py-1 px-2 bg-white text-gray-800"
            >
              {RISK_LEVELS.map(r => <option key={r} value={r}>{r}</option>)}
            </select>
          </div>
        </div>
      </div>

      {/* Main Compliance Cases Table */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-gray-50 text-gray-500 border-b border-gray-200 font-semibold">
              <tr>
                <th className="py-3 px-4">Case Number</th>
                <th className="py-3 px-4">Title / Hazard Description</th>
                <th className="py-3 px-4">Category</th>
                <th className="py-3 px-4">Source</th>
                <th className="py-3 px-4">Sector</th>
                <th className="py-3 px-4">Risk Level</th>
                <th className="py-3 px-4">Responsible</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 text-gray-700">
              {cases.length === 0 ? (
                <tr>
                  <td colSpan={9} className="py-8 text-center text-gray-400">
                    No compliance cases matching selected criteria.
                  </td>
                </tr>
              ) : (
                cases.map((c) => (
                  <tr key={c.id} className="hover:bg-gray-50/70 transition-colors">
                    <td className="py-3 px-4 font-mono font-medium text-blue-600">
                      {c.case_number}
                    </td>
                    <td className="py-3 px-4 font-medium text-gray-900 max-w-xs truncate">
                      {c.title}
                    </td>
                    <td className="py-3 px-4">
                      <span className="px-2 py-0.5 rounded bg-gray-100 text-gray-700 text-[11px]">
                        {c.category}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-gray-500 font-mono text-[11px]">{c.source}</td>
                    <td className="py-3 px-4 text-gray-600">{c.zone_name}</td>
                    <td className="py-3 px-4">
                      <RiskBadge level={c.risk_level} score={c.risk_score} />
                    </td>
                    <td className="py-3 px-4 text-gray-600">{c.responsible_user_name}</td>
                    <td className="py-3 px-4">
                      <span className={`inline-block px-2 py-0.5 rounded text-[11px] font-medium ${getStatusBadge(c.status)}`}>
                        {c.status}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={() => handleOpenDetails(c.id)}
                        className="px-2.5 py-1 rounded bg-gray-100 hover:bg-gray-200 text-gray-800 font-medium text-[11px]"
                      >
                        Inspect
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Case Details & Traceability Lifecycle Modal */}
      <Modal
        isOpen={detailsModalOpen}
        onClose={() => setDetailsModalOpen(false)}
        title={activeCaseDetails ? `${activeCaseDetails.case.case_number} - ${activeCaseDetails.case.title}` : 'Case Details'}
        maxWidth="max-w-3xl"
      >
        {detailsLoading || !activeCaseDetails ? (
          <div className="py-8 text-center text-xs text-gray-400">Loading case details...</div>
        ) : (
          <div className="space-y-5 text-xs">
            {/* Header Meta Strip */}
            <div className="p-3 bg-gray-50 rounded border border-gray-200 flex flex-wrap items-center justify-between gap-2">
              <div className="flex items-center space-x-2">
                <RiskBadge level={activeCaseDetails.case.risk_level} score={activeCaseDetails.case.risk_score} />
                <span className={`px-2 py-0.5 rounded font-medium ${getStatusBadge(activeCaseDetails.case.status)}`}>
                  {activeCaseDetails.case.status}
                </span>
                <span className="text-gray-400">|</span>
                <span className="text-gray-600">Category: <b>{activeCaseDetails.case.category}</b></span>
              </div>
              <div className="text-gray-500 text-[11px]">
                Statutory Deadline: <span className="font-mono text-red-600 font-medium">{new Date(activeCaseDetails.case.deadline).toLocaleString()}</span>
              </div>
            </div>

            {/* Evidence Preview if present */}
            {activeCaseDetails.case.evidence_path && (
              <div className="p-3 bg-gray-50 rounded border border-gray-200">
                <span className="text-gray-500 block mb-1 font-medium">Digital Vision Evidence / Snapshot:</span>
                <div className="max-h-48 rounded overflow-hidden bg-black flex items-center justify-center">
                  <img
                    src={activeCaseDetails.case.evidence_path}
                    alt="Case Evidence"
                    className="max-h-48 object-contain"
                  />
                </div>
              </div>
            )}

            {/* Corrective Action Summary */}
            <div>
              <h4 className="font-semibold text-gray-900 mb-1">Prescribed Corrective Action:</h4>
              <p className="p-3 bg-slate-50 rounded border border-slate-200 text-slate-800 leading-relaxed">
                {activeCaseDetails.case.corrective_action_summary || "Perform on-site safety protocol verification and log corrective remediation notes."}
              </p>
            </div>

            {/* Linked Corrective Actions Progress */}
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">Assigned Remediation Tasks ({activeCaseDetails.actions.length}):</h4>
              {activeCaseDetails.actions.length === 0 ? (
                <p className="text-gray-400">No action tasks directly created yet.</p>
              ) : (
                <div className="space-y-2">
                  {activeCaseDetails.actions.map(act => (
                    <div key={act.id} className="p-2.5 rounded bg-gray-50 border border-gray-200 flex items-center justify-between">
                      <div>
                        <p className="font-medium text-gray-900">{act.title}</p>
                        <p className="text-[11px] text-gray-500">Assigned to: {act.assigned_to}</p>
                      </div>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-medium ${
                        act.status === 'Closed' ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800'
                      }`}>
                        {act.status}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Audit Timeline */}
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">Statutory Audit Traceability Timeline:</h4>
              <div className="border-l-2 border-blue-500 pl-3 ml-1 space-y-2">
                {activeCaseDetails.timeline.map((item, idx) => (
                  <div key={idx} className="relative">
                    <span className="font-medium text-gray-800">{item.event}</span>
                    <span className="text-[10px] text-gray-400 block">
                      {new Date(item.timestamp).toLocaleString()} ({item.actor})
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Comments / Discussion Thread */}
            <div>
              <h4 className="font-semibold text-gray-900 mb-2 flex items-center">
                <MessageSquare size={13} className="mr-1.5 text-gray-500" />
                Case Comments & Investigation Log
              </h4>
              <div className="space-y-2 max-h-36 overflow-y-auto mb-3">
                {activeCaseDetails.comments.map(c => (
                  <div key={c.id} className="p-2 bg-gray-50 rounded border border-gray-100">
                    <div className="flex items-center justify-between mb-0.5">
                      <span className="font-semibold text-gray-800">{c.user_name}</span>
                      <span className="text-[10px] text-gray-400">{new Date(c.created_at).toLocaleTimeString()}</span>
                    </div>
                    <p className="text-gray-700 text-[11px]">{c.comment}</p>
                  </div>
                ))}
              </div>
              <form onSubmit={handleAddComment} className="flex space-x-2">
                <input
                  type="text"
                  value={commentInput}
                  onChange={(e) => setCommentInput(e.target.value)}
                  placeholder="Add note, finding, or supervisor log..."
                  className="flex-1 text-xs rounded border border-gray-300 p-2 focus:ring-1 focus:ring-blue-500"
                />
                <button
                  type="submit"
                  className="px-3 py-1.5 rounded bg-blue-600 text-white hover:bg-blue-700 inline-flex items-center font-medium"
                >
                  <Send size={12} className="mr-1" /> Send
                </button>
              </form>
            </div>

            {/* Status Transition Action Buttons */}
            <div className="flex items-center justify-between pt-3 border-t border-gray-200">
              <span className="text-gray-500 text-[11px]">Update Case Lifecycle:</span>
              <div className="flex space-x-2">
                {activeCaseDetails.case.status === 'Open' && (
                  <button
                    onClick={() => handleUpdateStatus('In Progress')}
                    className="px-3 py-1.5 rounded bg-blue-50 text-blue-700 hover:bg-blue-100 font-medium"
                  >
                    Mark In Progress
                  </button>
                )}
                {activeCaseDetails.case.status === 'In Progress' && (
                  <button
                    onClick={() => handleUpdateStatus('Pending Verification')}
                    className="px-3 py-1.5 rounded bg-purple-50 text-purple-700 hover:bg-purple-100 font-medium"
                  >
                    Submit for Verification
                  </button>
                )}
                {activeCaseDetails.case.status !== 'Closed' && (
                  <button
                    onClick={() => handleUpdateStatus('Closed')}
                    className="px-3 py-1.5 rounded bg-green-600 text-white hover:bg-green-700 font-medium"
                  >
                    Verify & Close Case
                  </button>
                )}
              </div>
            </div>
          </div>
        )}
      </Modal>

      {/* Initiate Case Modal */}
      <Modal
        isOpen={createModalOpen}
        onClose={() => setCreateModalOpen(false)}
        title="Initiate New Statutory Compliance Case"
      >
        <form onSubmit={handleCreateCaseSubmit} className="space-y-4 text-xs">
          <div>
            <label className="block font-medium text-gray-700 mb-1">Case Title / Hazard</label>
            <input
              type="text"
              required
              value={newCaseForm.title}
              onChange={(e) => setNewCaseForm({ ...newCaseForm, title: e.target.value })}
              placeholder="e.g. Excessive Methane Accumulation in Bleeder Drift"
              className="w-full text-xs rounded border border-gray-300 p-2 focus:ring-1 focus:ring-blue-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-medium text-gray-700 mb-1">Category</label>
              <select
                value={newCaseForm.category}
                onChange={(e) => setNewCaseForm({ ...newCaseForm, category: e.target.value })}
                className="w-full text-xs rounded border border-gray-300 p-2"
              >
                {CATEGORIES.filter(c => c !== 'All').map(c => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
            <div>
              <label className="block font-medium text-gray-700 mb-1">Detection Source</label>
              <select
                value={newCaseForm.source}
                onChange={(e) => setNewCaseForm({ ...newCaseForm, source: e.target.value })}
                className="w-full text-xs rounded border border-gray-300 p-2"
              >
                <option value="Manual Inspection">Manual Inspection</option>
                <option value="YOLOv8">YOLOv8 Vision</option>
                <option value="Sensor Anomaly">Sensor Anomaly</option>
                <option value="Predictive Model">Predictive Risk Model</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="block font-medium text-gray-700 mb-1">Sector / Zone</label>
              <select
                value={newCaseForm.zone_id}
                onChange={(e) => setNewCaseForm({ ...newCaseForm, zone_id: e.target.value })}
                className="w-full text-xs rounded border border-gray-300 p-2"
              >
                {zones.map(z => <option key={z.id} value={z.id}>{z.code}: {z.name}</option>)}
              </select>
            </div>
            <div>
              <label className="block font-medium text-gray-700 mb-1">Risk Severity</label>
              <select
                value={newCaseForm.risk_level}
                onChange={(e) => setNewCaseForm({ ...newCaseForm, risk_level: e.target.value })}
                className="w-full text-xs rounded border border-gray-300 p-2"
              >
                <option value="Low">Low</option>
                <option value="Medium">Medium</option>
                <option value="High">High</option>
                <option value="Critical">Critical</option>
              </select>
            </div>
            <div>
              <label className="block font-medium text-gray-700 mb-1">Risk Score (0-100)</label>
              <input
                type="number"
                min="0"
                max="100"
                value={newCaseForm.risk_score}
                onChange={(e) => setNewCaseForm({ ...newCaseForm, risk_score: e.target.value })}
                className="w-full text-xs rounded border border-gray-300 p-2"
              />
            </div>
          </div>

          <div>
            <label className="block font-medium text-gray-700 mb-1">Statutory Deadline</label>
            <input
              type="datetime-local"
              value={newCaseForm.deadline}
              onChange={(e) => setNewCaseForm({ ...newCaseForm, deadline: e.target.value })}
              className="w-full text-xs rounded border border-gray-300 p-2"
            />
          </div>

          <div>
            <label className="block font-medium text-gray-700 mb-1">Required Corrective Action Protocol</label>
            <textarea
              rows={3}
              value={newCaseForm.corrective_action_summary}
              onChange={(e) => setNewCaseForm({ ...newCaseForm, corrective_action_summary: e.target.value })}
              placeholder="Detail specific remediation steps, inspection requirements, and personnel assignments..."
              className="w-full text-xs rounded border border-gray-300 p-2"
            />
          </div>

          <div className="flex justify-end space-x-2 pt-3 border-t border-gray-200">
            <button
              type="button"
              onClick={() => setCreateModalOpen(false)}
              className="px-3 py-1.5 rounded border border-gray-300 text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-3.5 py-1.5 rounded bg-blue-600 text-white hover:bg-blue-700 font-medium"
            >
              Create Traceable Case
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default ComplianceCases;

