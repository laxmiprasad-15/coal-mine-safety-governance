import React, { useState, useEffect } from 'react';
import {
  Map, Eye, Activity, Users, Wrench, AlertTriangle,
  FileCheck2, ShieldAlert, Clock, RefreshCw, X, ChevronRight, Play, Pause
} from 'lucide-react';
import { getDigitalTwinApi, getZonePanelApi } from '../services/api';
import RiskBadge from '../components/RiskBadge';

const DigitalTwin = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [replayOffset, setReplayOffset] = useState(0); // in minutes
  const [isPlaying, setIsPlaying] = useState(false);
  const [selectedZone, setSelectedZone] = useState(null);
  const [zoneDetails, setZoneDetails] = useState(null);
  const [detailsLoading, setDetailsLoading] = useState(false);
  const [filterType, setFilterType] = useState('all'); // all, sensors, workers, cameras, equipment

  const fetchTwinData = async (offset = replayOffset) => {
    try {
      const res = await getDigitalTwinApi(offset);
      setData(res.data);
      // If a zone is currently selected, refresh its details
      if (selectedZone) {
        fetchZoneDetails(selectedZone.id);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const fetchZoneDetails = async (zoneId) => {
    try {
      setDetailsLoading(true);
      const res = await getZonePanelApi(zoneId);
      setZoneDetails(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setDetailsLoading(false);
    }
  };

  useEffect(() => {
    fetchTwinData(replayOffset);
  }, [replayOffset]);

  // Periodic refresh when live (replayOffset === 0)
  useEffect(() => {
    if (replayOffset === 0 && !isPlaying) {
      const interval = setInterval(() => fetchTwinData(0), 10000);
      return () => clearInterval(interval);
    }
  }, [replayOffset, isPlaying]);

  // History Replay Animation
  useEffect(() => {
    let playTimer;
    if (isPlaying) {
      playTimer = setInterval(() => {
        setReplayOffset((prev) => {
          if (prev <= 0) {
            setIsPlaying(false);
            return 0;
          }
          return Math.max(0, prev - 15);
        });
      }, 1500);
    }
    return () => clearInterval(playTimer);
  }, [isPlaying]);

  const handleZoneClick = (zone) => {
    setSelectedZone(zone);
    fetchZoneDetails(zone.id);
  };

  if (loading || !data) {
    return (
      <div className="flex items-center justify-center h-64 text-sm text-gray-500">
        Loading 2D Underground Mine Digital Twin schematic...
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between bg-white p-4 rounded-lg border border-gray-200">
        <div>
          <div className="flex items-center space-x-2">
            <h2 className="text-base font-semibold text-gray-900">2D Coal Mine Digital Twin</h2>
            <span className="text-xs px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200">
              {data.mine_name}
            </span>
            {replayOffset > 0 && (
              <span className="text-xs px-2 py-0.5 rounded bg-amber-50 text-amber-700 border border-amber-200 flex items-center">
                <Clock size={12} className="mr-1" /> Replay Mode (-{replayOffset}m)
              </span>
            )}
          </div>
          <p className="text-xs text-gray-500 mt-0.5">
            Real-time interactive schematic of underground haulage corridors, extraction panels, ventilation zones, and life support chambers.
          </p>
        </div>

        {/* Filter controls */}
        <div className="mt-3 md:mt-0 flex items-center space-x-2">
          <span className="text-xs text-gray-500">Markers:</span>
          {['all', 'sensors', 'workers', 'cameras', 'equipment'].map((f) => (
            <button
              key={f}
              onClick={() => setFilterType(f)}
              className={`px-2.5 py-1 text-xs rounded border transition-colors ${
                filterType === f
                  ? 'bg-gray-900 text-white border-gray-900 font-medium'
                  : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'
              }`}
            >
              {f.charAt(0).toUpperCase() + f.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Main 2D Schematic Canvas & Side Inspection Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        {/* Interactive 2D SVG Map */}
        <div className={`bg-[#0F172A] rounded-lg border border-gray-800 p-4 relative overflow-hidden flex flex-col justify-between ${selectedZone ? 'lg:col-span-3' : 'lg:col-span-4'}`}>
          {/* Map Legend */}
          <div className="absolute top-6 left-6 z-10 bg-slate-900/90 backdrop-blur border border-slate-700 rounded p-2.5 text-[11px] text-gray-300 space-y-1">
            <div className="font-semibold text-white mb-1.5 flex items-center justify-between">
              <span>Risk Status Legend</span>
            </div>
            <div className="flex items-center space-x-2"><span className="w-2.5 h-2.5 rounded bg-emerald-500" /><span>Green: Normal / Safe (&lt;25)</span></div>
            <div className="flex items-center space-x-2"><span className="w-2.5 h-2.5 rounded bg-amber-400" /><span>Yellow: Moderate Risk (26-50)</span></div>
            <div className="flex items-center space-x-2"><span className="w-2.5 h-2.5 rounded bg-orange-500" /><span>Orange: High Risk (51-75)</span></div>
            <div className="flex items-center space-x-2"><span className="w-2.5 h-2.5 rounded bg-red-600" /><span>Red: Critical Hazard (&gt;75)</span></div>
          </div>

          {/* SVG Map Canvas */}
          <div className="w-full overflow-x-auto py-2">
            <svg
              viewBox="0 0 820 420"
              className="w-full h-auto min-w-[760px] select-none"
            >
              {/* Mine Tunnel Corridors & Roadway Network */}
              <defs>
                <pattern id="coalTexture" width="20" height="20" patternUnits="userSpaceOnUse">
                  <path d="M 0 10 L 20 10 M 10 0 L 10 20" stroke="#1E293B" strokeWidth="1" />
                </pattern>
              </defs>

              <rect width="820" height="420" fill="#0F172A" />

              {/* Haulage tunnel connectors */}
              <path d="M 120 65 L 750 65" stroke="#334155" strokeWidth="24" strokeLinecap="round" />
              <path d="M 350 65 L 350 325" stroke="#334155" strokeWidth="20" strokeLinecap="round" />
              <path d="M 630 65 L 630 215" stroke="#334155" strokeWidth="20" strokeLinecap="round" />
              <path d="M 120 65 L 120 205" stroke="#334155" strokeWidth="18" strokeLinecap="round" />
              <path d="M 260 325 L 680 325" stroke="#334155" strokeWidth="20" strokeLinecap="round" />

              {/* Track Rails on main haulage */}
              <line x1="120" y1="61" x2="740" y2="61" stroke="#475569" strokeWidth="2" strokeDasharray="6,4" />
              <line x1="120" y1="69" x2="740" y2="69" stroke="#475569" strokeWidth="2" strokeDasharray="6,4" />

              {/* Mine Zones */}
              {data.zones.map((zone) => {
                const isSelected = selectedZone?.id === zone.id;
                const isCritical = zone.risk_level === 'Critical';

                return (
                  <g
                    key={zone.id}
                    onClick={() => handleZoneClick(zone)}
                    className="cursor-pointer transition-all duration-200 group"
                  >
                    {/* Zone Boundary Box */}
                    <rect
                      x={zone.map_x}
                      y={zone.map_y}
                      width={zone.map_width}
                      height={zone.map_height}
                      rx="6"
                      fill="#1E293B"
                      stroke={isSelected ? '#3B82F6' : zone.risk_color}
                      strokeWidth={isSelected ? '3.5' : isCritical ? '3' : '2'}
                      className="group-hover:fill-slate-800 transition-colors"
                    />

                    {/* Zone Status Banner */}
                    <rect
                      x={zone.map_x}
                      y={zone.map_y}
                      width={zone.map_width}
                      height="20"
                      rx="4"
                      fill={zone.risk_color}
                      fillOpacity={isCritical ? '0.95' : '0.8'}
                    />

                    {/* Zone Title Text */}
                    <text
                      x={zone.map_x + 8}
                      y={zone.map_y + 14}
                      fill="#FFFFFF"
                      fontSize="9.5"
                      fontWeight="bold"
                    >
                      {zone.code}: {zone.name.length > 20 ? zone.name.slice(0, 18) + '...' : zone.name}
                    </text>

                    {/* Risk score pill inside zone */}
                    <rect
                      x={zone.map_x + zone.map_width - 32}
                      y={zone.map_y + 4}
                      width="26"
                      height="12"
                      rx="3"
                      fill="#0F172A"
                    />
                    <text
                      x={zone.map_x + zone.map_width - 19}
                      y={zone.map_y + 13}
                      fill="#FFFFFF"
                      fontSize="8"
                      fontWeight="bold"
                      textAnchor="middle"
                    >
                      {zone.risk_score}
                    </text>

                    {/* Markers inside Zone */}
                    {/* Sensors */}
                    {(filterType === 'all' || filterType === 'sensors') &&
                      zone.sensors.map((s) => (
                        <g key={`sensor-${s.id}`}>
                          <circle
                            cx={s.map_x}
                            cy={s.map_y}
                            r="5"
                            fill={s.is_alert ? '#EF4444' : '#10B981'}
                            stroke="#FFFFFF"
                            strokeWidth="1.5"
                          />
                          <text
                            x={s.map_x}
                            y={s.map_y - 7}
                            fill="#94A3B8"
                            fontSize="7.5"
                            textAnchor="middle"
                          >
                            {s.type} {s.value}{s.unit}
                          </text>
                        </g>
                      ))}

                    {/* Workers */}
                    {(filterType === 'all' || filterType === 'workers') &&
                      zone.workers.map((w) => (
                        <g key={`worker-${w.id}`}>
                          <circle
                            cx={w.map_x}
                            cy={w.map_y}
                            r="4.5"
                            fill={w.is_alert ? '#DC2626' : '#3B82F6'}
                            stroke="#FFFFFF"
                            strokeWidth="1"
                          />
                          <text
                            x={w.map_x}
                            y={w.map_y + 10}
                            fill="#E2E8F0"
                            fontSize="6.5"
                            textAnchor="middle"
                          >
                            {w.code}
                          </text>
                        </g>
                      ))}

                    {/* Equipment */}
                    {(filterType === 'all' || filterType === 'equipment') &&
                      zone.equipment.map((eq) => (
                        <g key={`eq-${eq.id}`}>
                          <rect
                            x={eq.map_x - 5}
                            y={eq.map_y - 5}
                            width="10"
                            height="10"
                            fill="#F59E0B"
                            stroke="#FFFFFF"
                            strokeWidth="1"
                            rx="1"
                          />
                        </g>
                      ))}

                    {/* Open Cases Alert Badge */}
                    {zone.active_cases.length > 0 && (
                      <g>
                        <rect
                          x={zone.map_x + 8}
                          y={zone.map_y + zone.map_height - 18}
                          width="70"
                          height="13"
                          rx="3"
                          fill="#EF4444"
                        />
                        <text
                          x={zone.map_x + 43}
                          y={zone.map_y + zone.map_height - 8}
                          fill="#FFFFFF"
                          fontSize="7.5"
                          fontWeight="bold"
                          textAnchor="middle"
                        >
                          {zone.active_cases.length} Open Case(s)
                        </text>
                      </g>
                    )}
                  </g>
                );
              })}
            </svg>
          </div>

          {/* History Replay & Time Scrubbing Controls */}
          <div className="mt-4 bg-slate-900 border border-slate-800 rounded p-3 flex flex-col md:flex-row md:items-center md:justify-between text-xs text-gray-300">
            <div className="flex items-center space-x-3 mb-2 md:mb-0">
              <button
                onClick={() => setIsPlaying(!isPlaying)}
                className="p-1.5 rounded bg-blue-600 text-white hover:bg-blue-700"
              >
                {isPlaying ? <Pause size={14} /> : <Play size={14} />}
              </button>
              <div>
                <span className="font-medium text-white">Historical Replay Slider</span>
                <span className="text-[11px] text-gray-400 ml-2">
                  {replayOffset === 0 ? 'Live Stream' : `-${replayOffset} minutes prior`}
                </span>
              </div>
            </div>

            <div className="flex items-center space-x-3 flex-1 max-w-md mx-4">
              <span className="text-[11px] text-gray-400">-180m</span>
              <input
                type="range"
                min="0"
                max="180"
                step="15"
                value={replayOffset}
                onChange={(e) => {
                  setIsPlaying(false);
                  setReplayOffset(Number(e.target.value));
                }}
                className="w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-blue-600"
              />
              <span className="text-[11px] text-gray-400">Live</span>
            </div>

            <button
              onClick={() => {
                setReplayOffset(0);
                setIsPlaying(false);
              }}
              className="text-[11px] px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-gray-300 transition-colors"
            >
              Reset to Live
            </button>
          </div>
        </div>

        {/* Selected Zone Inspection Side Panel */}
        {selectedZone && (
          <div className="bg-white rounded-lg border border-gray-200 p-5 flex flex-col justify-between overflow-y-auto max-h-[580px]">
            <div>
              <div className="flex items-start justify-between border-b border-gray-100 pb-3 mb-3">
                <div>
                  <span className="text-xs text-gray-500 font-mono">{selectedZone.code}</span>
                  <h3 className="text-sm font-semibold text-gray-900">{selectedZone.name}</h3>
                </div>
                <button
                  onClick={() => setSelectedZone(null)}
                  className="text-gray-400 hover:text-gray-600 p-1 rounded"
                >
                  <X size={16} />
                </button>
              </div>

              {detailsLoading ? (
                <div className="text-xs text-gray-500 py-8 text-center">Loading zone telemetry...</div>
              ) : zoneDetails ? (
                <div className="space-y-4">
                  {/* Current Risk Level & Score */}
                  <div className="p-3 bg-gray-50 rounded border border-gray-200 flex items-center justify-between">
                    <div>
                      <span className="text-xs text-gray-500">Current AI Risk Status</span>
                      <div className="mt-1">
                        <RiskBadge level={zoneDetails.zone.risk_level} score={zoneDetails.zone.risk_score} />
                      </div>
                    </div>
                    <div className="text-right">
                      <span className="text-xs text-gray-500">Floor Level</span>
                      <p className="text-xs font-medium text-gray-800">{zoneDetails.zone.floor_level}</p>
                    </div>
                  </div>

                  {/* Explainable AI (XAI) Insight */}
                  <div className="p-3 bg-blue-50/60 rounded border border-blue-200 text-xs">
                    <span className="font-semibold text-blue-900 flex items-center mb-1">
                      <ShieldAlert size={14} className="mr-1 text-blue-700" /> Explainable AI Root Cause
                    </span>
                    <p className="text-blue-950 leading-relaxed text-[11px]">
                      {zoneDetails.xai_explanation}
                    </p>
                  </div>

                  {/* Real-time Environmental Telemetry */}
                  <div>
                    <h4 className="text-xs font-semibold text-gray-800 mb-2">Atmospheric Sensors</h4>
                    <div className="space-y-1.5">
                      {zoneDetails.latest_telemetry.map((t) => (
                        <div
                          key={t.sensor_id}
                          className={`p-2 rounded border flex items-center justify-between text-xs ${
                            t.is_anomaly ? 'bg-red-50 border-red-200' : 'bg-gray-50 border-gray-100'
                          }`}
                        >
                          <div>
                            <span className="font-medium text-gray-800">{t.name}</span>
                            <span className="text-[10px] text-gray-400 ml-1">({t.type})</span>
                          </div>
                          <div className="text-right">
                            <span className={`font-semibold ${t.is_anomaly ? 'text-red-700' : 'text-gray-900'}`}>
                              {t.value !== null ? `${t.value} ${t.unit}` : 'N/A'}
                            </span>
                            {t.is_anomaly && (
                              <span className="block text-[9px] text-red-600 font-medium">Exceeds limit</span>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Prescriptive Remediation Actions */}
                  <div>
                    <h4 className="text-xs font-semibold text-gray-800 mb-1.5">Recommended Actions</h4>
                    <ul className="space-y-1">
                      {zoneDetails.prescriptive_actions.map((act, i) => (
                        <li key={i} className="text-[11px] text-gray-600 flex items-start space-x-1.5">
                          <span className="text-blue-600 font-bold">•</span>
                          <span>{act}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Active Compliance Cases */}
                  <div>
                    <h4 className="text-xs font-semibold text-gray-800 mb-1.5">
                      Active Compliance Cases ({zoneDetails.active_cases.length})
                    </h4>
                    {zoneDetails.active_cases.length === 0 ? (
                      <p className="text-[11px] text-gray-500">No open cases in this zone.</p>
                    ) : (
                      <div className="space-y-1.5">
                        {zoneDetails.active_cases.map((c) => (
                          <div key={c.id} className="p-2 rounded bg-gray-50 border border-gray-200 text-xs">
                            <div className="flex items-center justify-between mb-0.5">
                              <span className="font-mono text-[10px] text-blue-600 font-semibold">{c.case_number}</span>
                              <span className="text-[10px] px-1.5 py-0.2 rounded bg-gray-200 text-gray-700">{c.status}</span>
                            </div>
                            <p className="text-gray-800 font-medium text-[11px] truncate">{c.title}</p>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ) : null}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DigitalTwin;

