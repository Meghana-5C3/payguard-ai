import React, { useState, useEffect } from 'react';
import { BarChart3, Database, ShieldCheck, Activity, CheckCircle, FileText } from 'lucide-react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  BarChart,
  Bar,
  Cell
} from 'recharts';
import { ModelMetricsResponse, AuditLogItem } from '../types/api';
import { api } from '../services/api';

export const MetricsPage: React.FC = () => {
  const [metrics, setMetrics] = useState<ModelMetricsResponse | null>(null);
  const [auditLogs, setAuditLogs] = useState<AuditLogItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const [mRes, aRes] = await Promise.all([
          api.getMetrics(),
          api.getAuditLogs()
        ]);
        setMetrics(mRes);
        setAuditLogs(aRes);
      } catch (err) {
        console.error("Metrics load error:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading || !metrics) {
    return (
      <div className="p-12 text-center text-slate-400 text-sm">
        Loading Model Health & Calibration Diagnostics...
      </div>
    );
  }

  // Format Calibration Curve Data for Recharts
  const calibData = metrics.calibration_curve.map((bin) => ({
    binLabel: `${(bin.bin_lower * 100).toFixed(0)}-${(bin.bin_upper * 100).toFixed(0)}%`,
    predictedProb: bin.predicted_prob,
    actualRate: bin.actual_rate,
    perfectLine: (bin.bin_lower + bin.bin_upper) / 2
  }));

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Metrics Banner KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        
        <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl shadow-xl flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-400 uppercase font-semibold">Test ROC-AUC Score</p>
            <p className="text-2xl font-extrabold font-mono text-emerald-400 mt-1">{metrics.roc_auc.toFixed(4)}</p>
            <p className="text-[11px] text-slate-500 mt-0.5">Discriminative capability</p>
          </div>
          <div className="h-10 w-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
            <Activity className="h-5 w-5" />
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl shadow-xl flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-400 uppercase font-semibold">Expected Calibration Error</p>
            <p className="text-2xl font-extrabold font-mono text-cyan-400 mt-1">{metrics.ece_calibrated.toFixed(4)}</p>
            <p className="text-[11px] text-slate-500 mt-0.5">Raw ECE: {metrics.ece_raw.toFixed(4)}</p>
          </div>
          <div className="h-10 w-10 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400">
            <ShieldCheck className="h-5 w-5" />
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl shadow-xl flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-400 uppercase font-semibold">Brier Score Loss</p>
            <p className="text-2xl font-extrabold font-mono text-purple-400 mt-1">{metrics.brier_score_calibrated.toFixed(4)}</p>
            <p className="text-[11px] text-slate-500 mt-0.5">Raw Brier: {metrics.brier_score_raw.toFixed(4)}</p>
          </div>
          <div className="h-10 w-10 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400">
            <BarChart3 className="h-5 w-5" />
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl shadow-xl flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-400 uppercase font-semibold">Model Artifacts</p>
            <p className="text-sm font-bold text-white mt-1">XGBoost + Isotonic</p>
            <p className="text-[11px] text-slate-500 mt-0.5">N={metrics.n_train.toLocaleString()} trained</p>
          </div>
          <div className="h-10 w-10 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
            <Database className="h-5 w-5" />
          </div>
        </div>

      </div>

      {/* Grid: Reliability Calibration Chart & Global Feature Importance */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Reliability Diagram (Calibration Curve) */}
        <div className="lg:col-span-7 bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
          <div>
            <h3 className="text-base font-bold text-white">Probability Reliability Diagram (Calibration Curve)</h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Compares predicted probabilities against true empirical fraud rates across probability decile bins.
            </p>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={calibData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="binLabel" stroke="#64748b" tick={{ fontSize: 11 }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 11 }} domain={[0, 1]} />
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const d = payload[0].payload;
                      return (
                        <div className="bg-slate-950 border border-slate-800 p-3 rounded-lg text-xs space-y-1">
                          <p className="font-bold text-white">Probability Bin: {d.binLabel}</p>
                          <p className="text-cyan-400">Actual Fraud Rate: {(d.actualRate * 100).toFixed(2)}%</p>
                          <p className="text-purple-400">Avg Predicted Prob: {(d.predictedProb * 100).toFixed(2)}%</p>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Line type="monotone" dataKey="perfectLine" stroke="#475569" strokeDasharray="5 5" name="Perfect Calibration" />
                <Line type="monotone" dataKey="actualRate" stroke="#38bdf8" strokeWidth={2} dot={{ r: 4 }} name="Actual Calibrated Rate" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Global Feature Importance */}
        <div className="lg:col-span-5 bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
          <div>
            <h3 className="text-base font-bold text-white">Global Feature Importance</h3>
            <p className="text-xs text-slate-400 mt-0.5">XGBoost Gain metric across feature vector space.</p>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={metrics.global_feature_importance.slice(0, 6)} layout="vertical">
                <XAxis type="number" stroke="#64748b" tick={{ fontSize: 11 }} />
                <YAxis dataKey="label" type="category" stroke="#94a3b8" tick={{ fontSize: 10 }} width={140} />
                <Tooltip />
                <Bar dataKey="importance" fill="#818cf8" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>

      {/* Immutable Audit Log Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <h3 className="text-base font-bold text-white flex items-center space-x-2">
            <FileText className="h-5 w-5 text-cyan-400" />
            <span>Immutable System & Analyst Audit Logs ({auditLogs.length})</span>
          </h3>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950 text-slate-400 uppercase font-mono border-b border-slate-800">
              <tr>
                <th className="p-3">Timestamp</th>
                <th className="p-3">Actor</th>
                <th className="p-3">Action</th>
                <th className="p-3">State Change</th>
                <th className="p-3">Notes & Audit Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {auditLogs.map((log) => (
                <tr key={log.id} className="hover:bg-slate-800/30">
                  <td className="p-3 text-slate-400 text-[11px]">
                    {new Date(log.timestamp).toLocaleTimeString()}
                  </td>
                  <td className="p-3">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      log.actor_type === 'SYSTEM' ? 'bg-cyan-500/10 text-cyan-400' :
                      log.actor_type === 'ANALYST' ? 'bg-amber-500/10 text-amber-400' :
                      'bg-purple-500/10 text-purple-400'
                    }`}>
                      {log.actor_type}:{log.actor_id}
                    </span>
                  </td>
                  <td className="p-3 font-bold text-slate-200">{log.action_taken}</td>
                  <td className="p-3 text-slate-300">
                    {log.previous_state || 'NONE'} &rarr; <strong className="text-cyan-400">{log.new_state}</strong>
                  </td>
                  <td className="p-3 text-slate-400 text-[11px] max-w-md truncate">
                    {log.notes || '-'}
                  </td>
                </tr>
              ))}
              {auditLogs.length === 0 && (
                <tr>
                  <td colSpan={5} className="p-6 text-center text-slate-500">
                    No audit log records recorded yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
};
