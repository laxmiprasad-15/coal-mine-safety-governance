import React, { useState, useEffect } from 'react';
import {
  FileText, Download, Plus, FileSpreadsheet,
  CheckCircle2, RefreshCw, Calendar, ShieldCheck
} from 'lucide-react';
import { getReportsApi, generateReportApi, getReportDownloadUrl } from '../services/api';
import Modal from '../components/Modal';

const REPORT_TYPES = [
  { id: 'Daily Safety', name: 'Daily Safety Inspection Brief', format: 'pdf' },
  { id: 'Weekly Compliance', name: 'Weekly DGMS Statutory Compliance Audit', format: 'pdf' },
  { id: 'PPE Violations', name: 'Computer Vision PPE Adherence Digest', format: 'pdf' },
  { id: 'Environmental', name: 'Atmospheric Gas & Ventilation Telemetry Report', format: 'excel' },
  { id: 'Equipment Health', name: 'Predictive Machinery Maintenance Report', format: 'excel' },
  { id: 'Risk Forecast', name: 'Predictive Risk Shift Forecast & XAI Summary', format: 'pdf' }
];

const Reports = () => {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  // Generate modal
  const [modalOpen, setModalOpen] = useState(false);
  const [reportType, setReportType] = useState('Daily Safety');
  const [reportFormat, setReportFormat] = useState('pdf');
  const [customTitle, setCustomTitle] = useState('');

  const loadReports = async () => {
    try {
      setLoading(true);
      const res = await getReportsApi();
      setReports(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadReports();
  }, []);

  const handleGenerateSubmit = async (e) => {
    e.preventDefault();
    try {
      setGenerating(true);
      await generateReportApi({
        report_type: reportType,
        title: customTitle || undefined,
        format: reportFormat
      });
      setModalOpen(false);
      setCustomTitle('');
      await loadReports();
    } catch (err) {
      alert("Error generating report: " + err.message);
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-xl font-semibold text-gray-900 tracking-tight">Automated Compliance Reports & Audit Exports</h2>
          <p className="text-xs text-gray-500 mt-1">
            Generate Directorate General of Mines Safety (DGMS) compliant statutory PDF and multi-tab Excel reports with AI executive summaries and digital signature blocks.
          </p>
        </div>
        <div className="mt-3 md:mt-0 flex items-center space-x-2">
          <button
            onClick={() => setModalOpen(true)}
            className="inline-flex items-center text-xs font-medium px-3.5 py-1.5 rounded bg-blue-600 text-white hover:bg-blue-700"
          >
            <Plus size={14} className="mr-1.5" />
            Generate New Report
          </button>
        </div>
      </div>

      {/* Reports Table */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-gray-50 text-gray-500 border-b border-gray-200 font-semibold">
              <tr>
                <th className="py-3 px-4">Report Title</th>
                <th className="py-3 px-4">Report Type</th>
                <th className="py-3 px-4">Format</th>
                <th className="py-3 px-4">AI Executive Summary Extract</th>
                <th className="py-3 px-4">Date Generated</th>
                <th className="py-3 px-4 text-right">Download</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 text-gray-700">
              {reports.map((r) => (
                <tr key={r.id} className="hover:bg-gray-50/70">
                  <td className="py-3 px-4 font-semibold text-gray-900">
                    <div className="flex items-center space-x-2">
                      {r.file_format === 'pdf' ? (
                        <FileText size={16} className="text-red-500" />
                      ) : (
                        <FileSpreadsheet size={16} className="text-emerald-600" />
                      )}
                      <span>{r.title}</span>
                    </div>
                  </td>
                  <td className="py-3 px-4 text-gray-600 font-medium">{r.report_type}</td>
                  <td className="py-3 px-4">
                    <span className="uppercase font-mono text-[10px] px-2 py-0.5 rounded bg-gray-100 text-gray-700">
                      {r.file_format}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-gray-500 max-w-sm truncate text-[11px]">
                    {r.summary_text}
                  </td>
                  <td className="py-3 px-4 font-mono text-gray-500 text-[11px]">
                    {new Date(r.created_at).toLocaleString()}
                  </td>
                  <td className="py-3 px-4 text-right">
                    <a
                      href={getReportDownloadUrl(r.id)}
                      download
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center px-2.5 py-1 rounded border border-gray-300 text-gray-700 hover:bg-gray-50 font-medium text-[11px]"
                    >
                      <Download size={12} className="mr-1 text-gray-500" />
                      Download
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Generate Report Modal */}
      <Modal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        title="Generate Official Statutory Compliance Report"
      >
        <form onSubmit={handleGenerateSubmit} className="space-y-4 text-xs">
          <div>
            <label className="block font-medium text-gray-700 mb-1">Select Report Template</label>
            <select
              value={reportType}
              onChange={(e) => {
                setReportType(e.target.value);
                const tmpl = REPORT_TYPES.find(t => t.id === e.target.value);
                if (tmpl) setReportFormat(tmpl.format);
              }}
              className="w-full text-xs rounded border border-gray-300 p-2"
            >
              {REPORT_TYPES.map(t => (
                <option key={t.id} value={t.id}>{t.name} ({t.format.toUpperCase()})</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block font-medium text-gray-700 mb-1">Output File Format</label>
            <div className="flex space-x-4">
              <label className="flex items-center space-x-1.5 cursor-pointer">
                <input
                  type="radio"
                  name="fmt"
                  value="pdf"
                  checked={reportFormat === 'pdf'}
                  onChange={() => setReportFormat('pdf')}
                  className="text-blue-600 focus:ring-blue-500"
                />
                <span className="text-xs text-gray-800">PDF Document (Includes charts & auditor signature)</span>
              </label>
              <label className="flex items-center space-x-1.5 cursor-pointer">
                <input
                  type="radio"
                  name="fmt"
                  value="excel"
                  checked={reportFormat === 'excel'}
                  onChange={() => setReportFormat('excel')}
                  className="text-blue-600 focus:ring-blue-500"
                />
                <span className="text-xs text-gray-800">Excel (.xlsx) Multi-tab Workbook</span>
              </label>
            </div>
          </div>

          <div>
            <label className="block font-medium text-gray-700 mb-1">Custom Title (Optional)</label>
            <input
              type="text"
              value={customTitle}
              onChange={(e) => setCustomTitle(e.target.value)}
              placeholder="e.g. DGMS Pre-Shift Safety Verification Audit Report"
              className="w-full text-xs rounded border border-gray-300 p-2"
            />
          </div>

          <div className="p-3 bg-blue-50/60 rounded border border-blue-100 text-[11px] text-blue-900">
            <span className="font-semibold">Note:</span> The AI engine will automatically compile real-time telemetry, active cases, XAI root-cause explanations, and append an official statutory certification signature block.
          </div>

          <div className="flex justify-end space-x-2 pt-3 border-t border-gray-200">
            <button
              type="button"
              onClick={() => setModalOpen(false)}
              className="px-3 py-1.5 rounded border border-gray-300 text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={generating}
              className="px-3.5 py-1.5 rounded bg-blue-600 text-white hover:bg-blue-700 font-medium inline-flex items-center"
            >
              {generating && <RefreshCw size={12} className="animate-spin mr-1.5" />}
              {generating ? 'Compiling Report...' : 'Compile & Export'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default Reports;

