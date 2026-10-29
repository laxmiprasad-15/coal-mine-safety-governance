import React, { useState, useEffect } from 'react';
import {
  TrendingUp, ShieldAlert, AlertTriangle, CheckCircle2,
  BrainCircuit, ArrowRight, RefreshCw, BarChart2, HelpCircle
} from 'lucide-react';
import { getNextShiftForecastApi, predictZoneRiskApi } from '../services/api';
import RiskBadge from '../components/RiskBadge';

const RiskForecast = () => {
  const [forecastData, setForecastData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedZone, setSelectedZone] = useState(null);
  const [recomputing, setRecomputing] = useState(false);

  const fetchForecast = async () => {
    try {
      setLoading(true);
      const res = await getNextShiftForecastApi();
      setForecastData(res.data);
      if (res.data.forecasts.length > 0) {
        setSelectedZone(res.data.forecasts[0]);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchForecast();
  }, []);

  const handleRecalculateZone = async (zoneId) => {
    try {
      setRecomputing(true);
      await predictZoneRiskApi(zoneId);
      await fetchForecast();
    } catch (e) {
      alert("Error recomputing risk: " + e.message);
    } finally {
      setRecomputing(false);
    }
  };

  if (loading || !forecastData) {
    return (
      <div className="flex items-center justify-center h-64 text-sm text-gray-500">
        Executing Random Forest predictive risk forecasting models...
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-xl font-semibold text-gray-900 tracking-tight">Predictive Risk Engine & Explainable AI (XAI)</h2>
          <p className="text-xs text-gray-500 mt-1">
            Machine Learning ensemble forecasting shift-ahead hazard probabilities with transparent feature attribution and prescriptive mitigation recommendations.
          </p>
        </div>
        <div className="mt-3 md:mt-0 flex items-center space-x-2">
          <span className="text-xs font-medium px-2.5 py-1 rounded bg-blue-50 text-blue-700 border border-blue-200">
            {forecastData.shift_name}
          </span>
          <button
            onClick={fetchForecast}
            className="inline-flex items-center text-xs font-medium px-3 py-1.5 rounded bg-white border border-gray-200 text-gray-700 hover:bg-gray-50"
          >
            <RefreshCw size={13} className="mr-1.5 text-gray-500" />
            Recalculate All Sectors
          </button>
        </div>
      </div>

      {/* Summary Forecast Alert Banner */}
      <div className="bg-white p-4 rounded-lg border border-gray-200 flex flex-col md:flex-row md:items-center md:justify-between">
        <div className="flex items-center space-x-3 mb-2 md:mb-0">
          <div className="p-2 rounded bg-amber-100 text-amber-700">
            <BrainCircuit size={18} />
          </div>
          <div>
            <h4 className="text-xs font-semibold text-gray-900">Next Shift Predictive Summary</h4>
            <p className="text-[11px] text-gray-500">
              {forecastData.high_or_critical_count} of {forecastData.total_zones} sectors projected in High or Critical danger zone for next operating shift.
            </p>
          </div>
        </div>
        <div className="text-xs text-gray-500 font-mono">
          Last Model Run: {new Date(forecastData.evaluation_timestamp).toLocaleTimeString()}
        </div>
      </div>

      {/* Main Grid: Sector Forecast Cards & XAI Breakdown Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Sector Forecast Cards List */}
        <div className="lg:col-span-1 space-y-3 max-h-[640px] overflow-y-auto pr-1">
          {forecastData.forecasts.map((f) => {
            const isSelected = selectedZone?.zone_id === f.zone_id;
            return (
              <div
                key={f.zone_id}
                onClick={() => setSelectedZone(f)}
                className={`p-4 rounded-lg border cursor-pointer transition-all ${
                  isSelected
                    ? 'border-blue-600 ring-1 ring-blue-600 bg-blue-50/20'
                    : 'border-gray-200 bg-white hover:border-gray-300'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <span className="text-[10px] font-mono text-gray-400">{f.zone_code}</span>
                    <h4 className="text-xs font-semibold text-gray-900 leading-tight">{f.zone_name}</h4>
                  </div>
                  <RiskBadge level={f.forecasted_risk} score={f.risk_score} />
                </div>

                <div className="mt-2.5 pt-2 border-t border-gray-100 flex items-center justify-between text-[11px] text-gray-500">
                  <span>Confidence: {Math.round(f.confidence * 100)}%</span>
                  <span className="text-blue-600 font-medium inline-flex items-center">
                    Inspect XAI <ArrowRight size={11} className="ml-0.5" />
                  </span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Explainable AI Deep Dive Panel */}
        {selectedZone && (
          <div className="lg:col-span-2 bg-white p-6 rounded-lg border border-gray-200 space-y-5">
            <div className="flex items-start justify-between border-b border-gray-100 pb-4">
              <div>
                <span className="text-xs font-mono text-gray-400">{selectedZone.zone_code}</span>
                <h3 className="text-base font-semibold text-gray-900">{selectedZone.zone_name}</h3>
                <div className="mt-1 flex items-center space-x-2">
                  <span className="text-xs text-gray-500">Forecasted Shift Risk:</span>
                  <RiskBadge level={selectedZone.forecasted_risk} score={selectedZone.risk_score} />
                </div>
              </div>
              <button
                onClick={() => handleRecalculateZone(selectedZone.zone_id)}
                disabled={recomputing}
                className="inline-flex items-center text-xs font-medium px-3 py-1.5 rounded border border-gray-200 hover:bg-gray-50 text-gray-700"
              >
                <RefreshCw size={12} className={`mr-1.5 ${recomputing ? 'animate-spin' : ''}`} />
                Re-predict
              </button>
            </div>

            {/* Natural Language XAI Narrative */}
            <div className="p-4 bg-slate-50 rounded-lg border border-slate-200">
              <h4 className="text-xs font-semibold text-slate-900 flex items-center mb-1.5">
                <BrainCircuit size={15} className="mr-1.5 text-blue-600" />
                Explainable AI (XAI) Audit Explanation for Safety Officers
              </h4>
              <p className="text-xs text-slate-700 leading-relaxed">
                "{selectedZone.xai_explanation}"
              </p>
            </div>

            {/* SHAP-style Feature Importance Bar Visualization */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <h4 className="text-xs font-semibold text-gray-800">
                  Top Contributing Risk Factors (Feature Attribution Weights)
                </h4>
                <span className="text-[11px] text-gray-400">Normalized Hazard Contribution</span>
              </div>

              <div className="space-y-3 pt-1">
                {(selectedZone.top_factors || []).map((factor, i) => {
                  const pct = Math.min(100, Math.max(5, factor.contribution_score * 2.2));
                  const isHighImpact = factor.contribution_score > 20;

                  return (
                    <div key={i} className="space-y-1">
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-medium text-gray-700">{factor.label}</span>
                        <div className="space-x-2 font-mono text-[11px]">
                          <span className="text-gray-500">Value: {factor.value}</span>
                          <span className={`font-semibold ${isHighImpact ? 'text-red-600' : 'text-gray-800'}`}>
                            +{factor.contribution_score} pts
                          </span>
                        </div>
                      </div>
                      <div className="w-full bg-gray-100 rounded-full h-2 overflow-hidden">
                        <div
                          className={`h-2 rounded-full transition-all duration-500 ${
                            isHighImpact ? 'bg-red-500' : 'bg-blue-600'
                          }`}
                          style={{ width: `${pct}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Prescriptive Remediation Actions */}
            <div className="pt-2">
              <h4 className="text-xs font-semibold text-gray-800 mb-2">Prescriptive Statutory Actions:</h4>
              <div className="space-y-2">
                {(selectedZone.prescriptive_actions || []).map((act, i) => (
                  <div key={i} className="p-2.5 rounded bg-blue-50/50 border border-blue-100 flex items-start space-x-2 text-xs text-blue-950">
                    <CheckCircle2 size={15} className="text-blue-600 flex-shrink-0 mt-0.5" />
                    <span>{act}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default RiskForecast;

