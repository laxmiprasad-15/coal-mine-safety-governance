import React, { useState, useEffect } from 'react';
import {
  CheckSquare, Clock, AlertTriangle, CheckCircle2,
  User, RefreshCw, ChevronRight, ShieldCheck, ArrowRight
} from 'lucide-react';
import { getActionsApi, updateActionApi } from '../services/api';
import Modal from '../components/Modal';

const ACTION_STATUSES = ['All', 'Assigned', 'In Progress', 'Submitted for Verification', 'Verified', 'Closed'];

const CorrectiveActions = () => {
  const [actions, setActions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('All');

  // Verify modal
  const [verifyModalOpen, setVerifyModalOpen] = useState(false);
  const [targetAction, setTargetAction] = useState(null);
  const [verificationNotes, setVerificationNotes] = useState('');

  const loadActions = async () => {
    try {
      setLoading(true);
      const params = {};
      if (statusFilter !== 'All') params.status_filter = statusFilter;
      const res = await getActionsApi(params);
      setActions(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadActions();
  }, [statusFilter]);

  const handleUpdateStatus = async (actionId, newStatus) => {
    try {
      await updateActionApi(actionId, { status: newStatus });
      await loadActions();
    } catch (e) {
      alert("Error updating action: " + e.message);
    }
  };

  const handleVerificationDecision = async (decision) => {
    if (!targetAction) return;
    try {
      const newStatus = decision === 'approve' ? 'Verified' : 'In Progress';
      await updateActionApi(targetAction.id, {
        status: newStatus,
        verification_notes: verificationNotes || (decision === 'approve' ? 'Remediation inspected and verified compliant.' : 'Reopened for further remediation.')
      });
      setVerifyModalOpen(false);
      setTargetAction(null);
      setVerificationNotes('');
      await loadActions();
    } catch (e) {
      alert("Error processing verification: " + e.message);
    }
  };

  const isOverdue = (dueDate, status) => {
    return new Date(dueDate) < new Date() && !['Verified', 'Closed'].includes(status);
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-xl font-semibold text-gray-900 tracking-tight">Corrective Action Workflow Tracking</h2>
          <p className="text-xs text-gray-500 mt-1">
            Accountable assignment, tracking, and statutory verification of underground remediation tasks.
          </p>
        </div>
        <div className="mt-3 md:mt-0 flex items-center space-x-2">
          <div className="flex items-center space-x-1.5 bg-white p-1 rounded-md border border-gray-200 text-xs">
            {ACTION_STATUSES.map(s => (
              <button
                key={s}
                onClick={() => setStatusFilter(s)}
                className={`px-2.5 py-1 rounded transition-colors ${
                  statusFilter === s
                    ? 'bg-blue-600 text-white font-medium'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                {s}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Actions Table */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-gray-50 text-gray-500 border-b border-gray-200 font-semibold">
              <tr>
                <th className="py-3 px-4">Action Title</th>
                <th className="py-3 px-4">Associated Case</th>
                <th className="py-3 px-4">Assigned To</th>
                <th className="py-3 px-4">Deadline</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Workflow Transition</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 text-gray-700">
              {actions.map((act) => {
                const overdue = isOverdue(act.due_date, act.status);
                return (
                  <tr key={act.id} className={`hover:bg-gray-50/70 ${overdue ? 'bg-red-50/20' : ''}`}>
                    <td className="py-3 px-4">
                      <span className="font-semibold text-gray-900 block">{act.title}</span>
                      <span className="text-[11px] text-gray-500 line-clamp-1">{act.description}</span>
                    </td>
                    <td className="py-3 px-4 font-medium text-blue-600 max-w-xs truncate">
                      {act.case_title}
                    </td>
                    <td className="py-3 px-4 text-gray-700">
                      <div className="flex items-center space-x-1.5">
                        <User size={13} className="text-gray-400" />
                        <span>{act.assigned_to_name}</span>
                      </div>
                    </td>
                    <td className="py-3 px-4 font-mono">
                      <span className={overdue ? 'text-red-600 font-semibold flex items-center' : 'text-gray-600'}>
                        {overdue && <AlertTriangle size={12} className="mr-1 text-red-600" />}
                        {new Date(act.due_date).toLocaleDateString()}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <span className={`inline-block px-2 py-0.5 rounded text-[11px] font-medium ${
                        act.status === 'Verified' || act.status === 'Closed' ? 'bg-green-100 text-green-800' :
                        act.status === 'Submitted for Verification' ? 'bg-purple-100 text-purple-800' :
                        act.status === 'In Progress' ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'
                      }`}>
                        {act.status}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right space-x-1.5">
                      {act.status === 'Assigned' && (
                        <button
                          onClick={() => handleUpdateStatus(act.id, 'In Progress')}
                          className="px-2.5 py-1 rounded bg-blue-50 text-blue-700 hover:bg-blue-100 font-medium text-[11px]"
                        >
                          Start Progress
                        </button>
                      )}
                      {act.status === 'In Progress' && (
                        <button
                          onClick={() => handleUpdateStatus(act.id, 'Submitted for Verification')}
                          className="px-2.5 py-1 rounded bg-purple-50 text-purple-700 hover:bg-purple-100 font-medium text-[11px]"
                        >
                          Submit Verification
                        </button>
                      )}
                      {act.status === 'Submitted for Verification' && (
                        <button
                          onClick={() => {
                            setTargetAction(act);
                            setVerifyModalOpen(true);
                          }}
                          className="px-2.5 py-1 rounded bg-green-600 text-white hover:bg-green-700 font-medium text-[11px]"
                        >
                          Approve / Reject
                        </button>
                      )}
                      {(act.status === 'Verified' || act.status === 'Closed') && (
                        <span className="text-[11px] text-green-700 font-medium inline-flex items-center">
                          <CheckCircle2 size={13} className="mr-1" /> Completed
                        </span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Verification Modal */}
      <Modal
        isOpen={verifyModalOpen}
        onClose={() => setVerifyModalOpen(false)}
        title="Safety Officer Statutory Action Sign-off"
      >
        {targetAction && (
          <div className="space-y-4 text-xs">
            <div className="p-3 bg-gray-50 rounded border border-gray-200">
              <span className="font-semibold text-gray-900">{targetAction.title}</span>
              <p className="text-gray-500 mt-1">Responsible: {targetAction.assigned_to_name}</p>
            </div>

            <div>
              <label className="block font-medium text-gray-700 mb-1">
                Verification Remarks & DGMS Evidence Notes
              </label>
              <textarea
                rows={3}
                value={verificationNotes}
                onChange={(e) => setVerificationNotes(e.target.value)}
                placeholder="Confirm that sensors were re-calibrated, ventilation curtains repaired, or PPE adherence confirmed..."
                className="w-full text-xs rounded border border-gray-300 p-2.5 focus:ring-1 focus:ring-blue-500"
              />
            </div>

            <div className="flex justify-end space-x-2 pt-3 border-t border-gray-200">
              <button
                onClick={() => handleVerificationDecision('reject')}
                className="px-3.5 py-1.5 rounded border border-red-300 text-red-700 hover:bg-red-50 font-medium"
              >
                Reject / Reopen Action
              </button>
              <button
                onClick={() => handleVerificationDecision('approve')}
                className="px-3.5 py-1.5 rounded bg-green-600 text-white hover:bg-green-700 font-medium"
              >
                Verify & Approve Completion
              </button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default CorrectiveActions;

