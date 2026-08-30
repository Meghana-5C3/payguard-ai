import React, { useState, useEffect } from 'react';
import { Sliders, Plus, RotateCcw, CheckCircle2, AlertTriangle, ShieldCheck } from 'lucide-react';
import { PolicyRule } from '../types/api';
import { api } from '../services/api';

export const PolicyPage: React.FC = () => {
  const [policies, setPolicies] = useState<PolicyRule[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingRule, setEditingRule] = useState<PolicyRule | null>(null);

  const fetchPolicies = async () => {
    setLoading(true);
    try {
      const data = await api.getPolicies();
      setPolicies(data);
    } catch (err) {
      console.error("Policy fetch error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPolicies();
  }, []);

  const handleToggleRule = async (rule: PolicyRule) => {
    try {
      await api.updatePolicy(rule.id, {
        ...rule,
        is_active: !rule.is_active
      });
      fetchPolicies();
    } catch (err) {
      console.error("Toggle rule error:", err);
    }
  };

  const handleResetDefaults = async () => {
    try {
      await api.resetPolicies();
      fetchPolicies();
    } catch (err) {
      console.error("Reset error:", err);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center space-x-2">
            <Sliders className="h-6 w-6 text-purple-400" />
            <span>Adaptive Risk Policy Matrix Manager</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Dynamic business rules taking calibrated ML risk scores and feature vectors as inputs to yield authoritative actions (`APPROVE`, `VERIFY`, `HOLD`).
          </p>
        </div>
        <button
          onClick={handleResetDefaults}
          className="py-2 px-3 bg-slate-900 border border-slate-800 hover:border-purple-500/50 rounded-xl text-xs font-semibold text-slate-300 transition flex items-center space-x-2"
        >
          <RotateCcw className="h-3.5 w-3.5" />
          <span>Reset Defaults</span>
        </button>
      </div>

      {/* Policy Rules List */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider text-slate-400">
            Active Rule Evaluation Order (Priority Ascending)
          </h3>
        </div>

        <div className="space-y-3">
          {policies.map((rule) => (
            <div
              key={rule.id}
              className={`bg-slate-950 border p-4 rounded-xl flex items-center justify-between transition ${
                rule.is_active ? 'border-slate-800 hover:border-purple-500/40' : 'border-slate-800/40 opacity-60'
              }`}
            >
              <div className="space-y-1 max-w-2xl">
                <div className="flex items-center space-x-3">
                  <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-purple-500/10 text-purple-400 border border-purple-500/20">
                    P{rule.priority}
                  </span>
                  <h4 className="text-sm font-bold text-white">{rule.rule_name}</h4>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase ${
                    rule.action === 'HOLD' ? 'bg-red-500/20 text-red-300' :
                    rule.action === 'VERIFY' ? 'bg-amber-500/20 text-amber-300' :
                    'bg-emerald-500/20 text-emerald-300'
                  }`}>
                    ACTION: {rule.action}
                  </span>
                </div>
                <p className="text-xs text-slate-400 leading-relaxed">{rule.description}</p>
                <div className="text-[11px] font-mono text-cyan-400 bg-slate-900/80 px-3 py-1 rounded inline-block">
                  Condition: {JSON.stringify(rule.condition_json)}
                </div>
              </div>

              {/* Toggle Switch */}
              <div className="flex items-center space-x-3">
                <span className="text-xs text-slate-400 font-medium">{rule.is_active ? 'Active' : 'Disabled'}</span>
                <button
                  onClick={() => handleToggleRule(rule)}
                  className={`w-12 h-6 rounded-full transition-colors p-1 relative flex items-center ${
                    rule.is_active ? 'bg-purple-600 justify-end' : 'bg-slate-800 justify-start'
                  }`}
                >
                  <span className="h-4 w-4 rounded-full bg-white shadow-md"></span>
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
};
