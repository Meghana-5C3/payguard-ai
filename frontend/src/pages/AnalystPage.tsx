import React, { useState, useEffect } from 'react';
import { ShieldAlert, CheckCircle, XCircle, Search, Filter, Eye, AlertCircle, RefreshCw } from 'lucide-react';
import { AnalystQueueItem } from '../types/api';
import { api } from '../services/api';

export const AnalystPage: React.FC = () => {
  const [queue, setQueue] = useState<AnalystQueueItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedItem, setSelectedItem] = useState<AnalystQueueItem | null>(null);
  const [overrideAction, setOverrideAction] = useState<'APPROVE' | 'REJECT'>('REJECT');
  const [reasonCode, setReasonCode] = useState('SUSPECTED_FRAUD_RING');
  const [analystNotes, setAnalystNotes] = useState('IP address matched known malicious proxy range.');
  const [submitting, setSubmitting] = useState(false);

  const fetchQueue = async () => {
    setLoading(true);
    try {
      const data = await api.getAnalystQueue('ALL');
      setQueue(data);
      if (data.length > 0 && !selectedItem) {
        setSelectedItem(data[0]);
      }
    } catch (err) {
      console.error("Queue fetch error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQueue();
  }, []);

  const handleOverride = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedItem) return;
    setSubmitting(true);
    try {
      await api.submitAnalystOverride(selectedItem.evaluation_id, overrideAction, reasonCode, analystNotes);
      fetchQueue();
    } catch (err) {
      console.error("Override error:", err);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center space-x-2">
            <ShieldAlert className="h-6 w-6 text-amber-400" />
            <span>Fraud Analyst Workbench & Escalation Queue</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Human-in-the-loop review queue for transactions flagged for manual investigation (`HOLD`).
          </p>
        </div>
        <button
          onClick={fetchQueue}
          className="py-2 px-3 bg-slate-900 border border-slate-800 rounded-xl text-xs font-semibold text-slate-300 hover:bg-slate-800 transition flex items-center space-x-2"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Queue</span>
        </button>
      </div>

      {/* Main Grid: Queue Table (Left) & Deep Investigation Drawer (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Table Column */}
        <div className="lg:col-span-7 bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider text-slate-400">
              Flagged Evaluations Queue ({queue.length})
            </h3>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950 text-slate-400 uppercase font-mono border-b border-slate-800">
                <tr>
                  <th className="p-3">Risk Score</th>
                  <th className="p-3">User & Amount</th>
                  <th className="p-3">Action State</th>
                  <th className="p-3">Status</th>
                  <th className="p-3 text-right">View</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {queue.map((item) => (
                  <tr
                    key={item.evaluation_id}
                    onClick={() => setSelectedItem(item)}
                    className={`cursor-pointer transition ${
                      selectedItem?.evaluation_id === item.evaluation_id
                        ? 'bg-slate-800/80 border-l-4 border-amber-500'
                        : 'hover:bg-slate-800/40'
                    }`}
                  >
                    <td className="p-3">
                      <span className={`font-mono font-bold px-2 py-0.5 rounded ${
                        item.risk_score >= 850 ? 'bg-red-500/20 text-red-400' : 'bg-amber-500/20 text-amber-400'
                      }`}>
                        {item.risk_score} / 1000
                      </span>
                    </td>
                    <td className="p-3">
                      <p className="font-bold text-white">${item.amount.toFixed(2)} {item.currency}</p>
                      <p className="text-[11px] text-slate-400 font-mono">{item.user_email}</p>
                    </td>
                    <td className="p-3">
                      <span className={`font-bold uppercase text-[10px] px-2 py-0.5 rounded border ${
                        item.decision_action === 'HOLD' ? 'bg-red-500/10 text-red-400 border-red-500/20' :
                        item.decision_action === 'VERIFY' ? 'bg-amber-500/10 text-amber-400 border-amber-500/20' :
                        'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                      }`}>
                        {item.decision_action}
                      </span>
                    </td>
                    <td className="p-3 text-slate-300 font-mono text-[11px]">
                      {item.status}
                    </td>
                    <td className="p-3 text-right">
                      <Eye className="h-4 w-4 text-cyan-400 inline-block" />
                    </td>
                  </tr>
                ))}
                {queue.length === 0 && (
                  <tr>
                    <td colSpan={5} className="p-8 text-center text-slate-500">
                      No evaluations currently in queue.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Deep Investigation Column */}
        <div className="lg:col-span-5 bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-5">
          {selectedItem ? (
            <>
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <div>
                  <h3 className="text-base font-bold text-white">Investigation Drawer</h3>
                  <p className="text-xs text-slate-400 font-mono">TX ID: {selectedItem.transaction_id.slice(0, 16)}...</p>
                </div>
                <span className="text-xs font-bold font-mono px-3 py-1 bg-slate-950 border border-slate-800 rounded-lg text-cyan-400">
                  {(selectedItem.calibrated_probability * 100).toFixed(1)}% Fraud Prob.
                </span>
              </div>

              {/* Rationale */}
              <div className="bg-slate-950 p-3.5 rounded-xl border border-slate-800 text-xs">
                <span className="font-bold text-slate-200">System Explanation: </span>
                <span className="text-slate-300">{selectedItem.natural_explanation}</span>
              </div>

              {/* SHAP Drivers */}
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Top SHAP Drivers</h4>
                <div className="space-y-1.5 max-h-40 overflow-y-auto pr-1">
                  {selectedItem.shap_attributions?.slice(0, 4).map((att, idx) => (
                    <div key={idx} className="bg-slate-950 p-2 rounded border border-slate-800/80 flex justify-between text-xs">
                      <span className="text-slate-300">{att.label}: <strong className="font-mono text-cyan-400">{String(att.value)}</strong></span>
                      <span className={`font-mono font-bold ${att.raw_shap_value > 0 ? 'text-red-400' : 'text-emerald-400'}`}>
                        {att.impact}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Manual Override Form */}
              <form onSubmit={handleOverride} className="pt-4 border-t border-slate-800 space-y-4">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">Human Decision Override</h4>
                
                <div className="grid grid-cols-2 gap-3">
                  <button
                    type="button"
                    onClick={() => setOverrideAction('REJECT')}
                    className={`py-2 px-3 rounded-xl border text-xs font-bold flex items-center justify-center space-x-2 transition ${
                      overrideAction === 'REJECT'
                        ? 'bg-red-500/20 border-red-500 text-red-400'
                        : 'bg-slate-950 border-slate-800 text-slate-400'
                    }`}
                  >
                    <XCircle className="h-4 w-4" />
                    <span>Reject & Flag Fraud</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setOverrideAction('APPROVE')}
                    className={`py-2 px-3 rounded-xl border text-xs font-bold flex items-center justify-center space-x-2 transition ${
                      overrideAction === 'APPROVE'
                        ? 'bg-emerald-500/20 border-emerald-500 text-emerald-400'
                        : 'bg-slate-950 border-slate-800 text-slate-400'
                    }`}
                  >
                    <CheckCircle className="h-4 w-4" />
                    <span>Override Approve</span>
                  </button>
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">Reason Code</label>
                  <select
                    value={reasonCode}
                    onChange={(e) => setReasonCode(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none"
                  >
                    <option value="SUSPECTED_FRAUD_RING">Suspected Fraud Ring / ATO</option>
                    <option value="PROXY_TOR_IP">Confirmed TOR/Proxy Exit Node</option>
                    <option value="VERIFIED_CUSTOMER_CALL">Verified Identity via Phone Call</option>
                    <option value="FALSE_POSITIVE_WHALE">Legitimate High Net Worth Transaction</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">Analyst Notes & Audit Rationale</label>
                  <textarea
                    rows={2}
                    value={analystNotes}
                    onChange={(e) => setAnalystNotes(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none"
                    placeholder="Enter audit rationale..."
                  />
                </div>

                <button
                  type="submit"
                  disabled={submitting}
                  className="w-full py-2.5 bg-gradient-to-r from-amber-500 to-orange-600 text-slate-950 font-bold text-xs rounded-xl shadow-lg shadow-amber-500/20 hover:brightness-110 transition disabled:opacity-50"
                >
                  {submitting ? 'Submitting Override...' : 'Commit Manual Override & Audit Log'}
                </button>
              </form>
            </>
          ) : (
            <div className="p-8 text-center text-slate-500 text-xs">
              Select a transaction from the queue to inspect attributions.
            </div>
          )}
        </div>

      </div>

    </div>
  );
};
