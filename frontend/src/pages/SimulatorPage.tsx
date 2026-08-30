import React, { useState } from 'react';
import { Play, Sparkles, ShieldCheck, RefreshCw, Zap, Lock, Activity, ShieldAlert, CheckCircle2, ArrowRight } from 'lucide-react';
import { TransactionPayload, RiskEvaluationResponse } from '../types/api';
import { api } from '../services/api';
import { RiskGauge } from '../components/RiskGauge';
import { ShapWaterfall } from '../components/ShapWaterfall';
import { OtpModal } from '../components/OtpModal';

interface ScenarioPreset {
  name: string;
  badge: string;
  badgeColor: string;
  description: string;
  payload: TransactionPayload;
}

const PRESET_SCENARIOS: ScenarioPreset[] = [
  {
    name: "Normal Local Purchase",
    badge: "Low Risk",
    badgeColor: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
    description: "Standard daily coffee transaction from regular device and home location.",
    payload: {
      user_id: "usr_99812",
      merchant_id: "mer_4410",
      amount: 45.50,
      currency: "USD",
      payment_method: "CREDIT_CARD",
      device_fingerprint: "dev_mac_8819ab",
      ip_address: "192.168.1.105",
      geo_location: "US-NY",
      lat: 40.7128,
      lon: -74.0060
    }
  },
  {
    name: "Velocity Spike (High Tx Rate)",
    badge: "Medium Risk",
    badgeColor: "bg-amber-500/20 text-amber-400 border-amber-500/30",
    description: "Repeated purchases within 1 hour triggering velocity policy rules.",
    payload: {
      user_id: "usr_99812",
      merchant_id: "mer_8820",
      amount: 480.00,
      currency: "USD",
      payment_method: "CREDIT_CARD",
      device_fingerprint: "dev_mac_8819ab",
      ip_address: "192.168.1.105",
      geo_location: "US-NY",
      lat: 40.7128,
      lon: -74.0060
    }
  },
  {
    name: "Account Takeover & Proxy IP",
    badge: "High Risk",
    badgeColor: "bg-orange-500/20 text-orange-400 border-orange-500/30",
    description: "Unrecognized new device combined with known Tor proxy IP address.",
    payload: {
      user_id: "usr_99812",
      merchant_id: "mer_9950",
      amount: 1850.00,
      currency: "USD",
      payment_method: "CREDIT_CARD",
      device_fingerprint: "dev_unknown_xyz99",
      ip_address: "185.220.101.5",
      geo_location: "US-NY",
      lat: 40.7128,
      lon: -74.0060
    }
  },
  {
    name: "High Value Crypto Transfer",
    badge: "Critical Risk",
    badgeColor: "bg-rose-500/20 text-rose-400 border-rose-500/30",
    description: "Large amount transfer to MCC Tier 5 merchant from high-risk segment user.",
    payload: {
      user_id: "usr_11094",
      merchant_id: "mer_9950",
      amount: 8500.00,
      currency: "USD",
      payment_method: "CREDIT_CARD",
      device_fingerprint: "dev_hacker_9901",
      ip_address: "109.70.100.12",
      geo_location: "CA-ON",
      lat: 43.6532,
      lon: -79.3832
    }
  }
];

export const SimulatorPage: React.FC = () => {
  const [payload, setPayload] = useState<TransactionPayload>(PRESET_SCENARIOS[0].payload);
  const [loading, setLoading] = useState(false);
  const [evaluation, setEvaluation] = useState<RiskEvaluationResponse | null>(null);
  const [isOtpOpen, setIsOtpOpen] = useState(false);
  const [verificationSuccess, setVerificationSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleEvaluate = async (customPayload?: TransactionPayload) => {
    setLoading(true);
    setVerificationSuccess(false);
    setError(null);
    try {
      const res = await api.evaluateTransaction(customPayload || payload);
      setEvaluation(res);
    } catch (err: any) {
      console.error("Evaluation error:", err);
      setError("Unable to analyze the transaction. Please check the backend connection and try again.");
    } finally {
      setLoading(false);
    }
  };

  const selectPreset = (preset: ScenarioPreset) => {
    setPayload(preset.payload);
    handleEvaluate(preset.payload);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Header Platform Banner */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 sm:p-8 backdrop-blur-md relative overflow-hidden">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 relative z-10">
          <div className="space-y-2 max-w-3xl">
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-xs font-semibold">
              <Sparkles className="h-3.5 w-3.5" />
              <span>Real-Time Synthetic Payment Risk Simulator</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              AI-Powered Payment Fraud Detection & Risk Intelligence
            </h1>
            <p className="text-sm text-slate-400 leading-relaxed">
              Detect suspicious transactions, understand model decisions, and review high-risk activity using explainable machine learning combined with dynamic business policy escalation.
            </p>
          </div>

          {/* Platform Status Cards */}
          <div className="grid grid-cols-2 gap-3 shrink-0">
            <div className="bg-slate-950/80 border border-slate-800 p-3 rounded-xl">
              <p className="text-[10px] uppercase font-bold text-slate-500">Pipeline Status</p>
              <div className="flex items-center space-x-1.5 mt-1">
                <span className="h-2 w-2 rounded-full bg-emerald-400"></span>
                <span className="text-xs font-bold text-slate-200">Active</span>
              </div>
            </div>
            <div className="bg-slate-950/80 border border-slate-800 p-3 rounded-xl">
              <p className="text-[10px] uppercase font-bold text-slate-500">Decision Engine</p>
              <span className="text-xs font-bold text-cyan-400 mt-1 block">XGBoost + Policy</span>
            </div>
          </div>
        </div>
      </div>

      {/* Preset Scenario Cards */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-bold text-slate-300 uppercase tracking-wider flex items-center space-x-2">
            <Sparkles className="h-4 w-4 text-cyan-400" />
            <span>Demonstration Scenarios</span>
          </h2>
          <span className="text-xs text-slate-500">Click any scenario to evaluate instantly</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {PRESET_SCENARIOS.map((preset, idx) => (
            <button
              key={idx}
              onClick={() => selectPreset(preset)}
              className="text-left bg-slate-900 hover:bg-slate-800/90 border border-slate-800 hover:border-cyan-500/50 p-4 rounded-2xl transition group relative overflow-hidden shadow-lg"
            >
              <div className="flex justify-between items-start mb-2">
                <span className="text-sm font-bold text-slate-200 group-hover:text-cyan-400 transition">
                  {preset.name}
                </span>
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${preset.badgeColor}`}>
                  {preset.badge}
                </span>
              </div>
              <p className="text-xs text-slate-400 line-clamp-2 mb-3">{preset.description}</p>
              <div className="flex items-center justify-between text-xs pt-2 border-t border-slate-800/80 font-mono">
                <span className="text-cyan-400 font-bold">${preset.payload.amount.toFixed(2)} USD</span>
                <span className="text-slate-500 group-hover:text-slate-300 flex items-center space-x-1">
                  <span>Run</span>
                  <ArrowRight className="h-3 w-3" />
                </span>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Main Grid: Input Form & Results */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Form Column */}
        <div className="lg:col-span-5 bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-5">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <h3 className="text-base font-bold text-white flex items-center space-x-2">
              <Zap className="h-4 w-4 text-cyan-400" />
              <span>Transaction Parameters</span>
            </h3>
            <span className="text-xs text-slate-500 font-mono">12 Features</span>
          </div>

          <div className="space-y-4 text-xs">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-slate-400 font-medium mb-1">Amount ($)</label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  value={payload.amount}
                  onChange={(e) => setPayload({ ...payload, amount: parseFloat(e.target.value) || 0 })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2.5 text-cyan-400 font-mono font-bold focus:border-cyan-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-slate-400 font-medium mb-1">Currency</label>
                <input
                  type="text"
                  value={payload.currency}
                  onChange={(e) => setPayload({ ...payload, currency: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2.5 text-slate-200 font-mono focus:border-cyan-500 focus:outline-none"
                />
              </div>
            </div>

            <div>
              <label className="block text-slate-400 font-medium mb-1">User Identifier</label>
              <input
                type="text"
                value={payload.user_id}
                onChange={(e) => setPayload({ ...payload, user_id: e.target.value })}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2.5 text-slate-200 font-mono focus:border-cyan-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-slate-400 font-medium mb-1">Merchant Identifier</label>
              <input
                type="text"
                value={payload.merchant_id}
                onChange={(e) => setPayload({ ...payload, merchant_id: e.target.value })}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2.5 text-slate-200 font-mono focus:border-cyan-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-slate-400 font-medium mb-1">Device Fingerprint</label>
              <input
                type="text"
                value={payload.device_fingerprint}
                onChange={(e) => setPayload({ ...payload, device_fingerprint: e.target.value })}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2.5 text-slate-200 font-mono focus:border-cyan-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-slate-400 font-medium mb-1">IP Address & Proxy Check</label>
              <input
                type="text"
                value={payload.ip_address}
                onChange={(e) => setPayload({ ...payload, ip_address: e.target.value })}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2.5 text-slate-200 font-mono focus:border-cyan-500 focus:outline-none"
              />
            </div>
          </div>

          <button
            onClick={() => handleEvaluate()}
            disabled={loading}
            className="w-full py-3.5 px-4 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:brightness-110 text-white font-bold text-sm transition shadow-lg shadow-cyan-500/20 flex items-center justify-center space-x-2 disabled:opacity-50 mt-4"
          >
            {loading ? (
              <>
                <RefreshCw className="h-4 w-4 animate-spin" />
                <span>Analyzing transaction...</span>
              </>
            ) : (
              <>
                <Play className="h-4 w-4 fill-white" />
                <span>Evaluate Risk Engine (POST /api/risk/evaluate)</span>
              </>
            )}
          </button>
        </div>

        {/* Output Column (Gauge + Policies + SHAP) */}
        <div className="lg:col-span-7 space-y-6">
          
          {error && (
            <div className="bg-rose-500/10 border border-rose-500/30 rounded-2xl p-4 text-xs text-rose-300">
              <p className="font-semibold">{error}</p>
            </div>
          )}

          {evaluation ? (
            <>
              <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
                
                {/* Risk Score Gauge */}
                <div className="md:col-span-6">
                  <RiskGauge
                    score={evaluation.risk_score}
                    calibratedProba={evaluation.calibrated_probability}
                    rawProba={evaluation.raw_probability}
                    action={verificationSuccess ? 'APPROVE' : evaluation.recommended_action}
                    riskLevel={evaluation.risk_level}
                  />

                  {/* Verification challenge button if VERIFY state */}
                  {evaluation.recommended_action === 'VERIFY' && !verificationSuccess && (
                    <button
                      onClick={() => setIsOtpOpen(true)}
                      className="w-full mt-4 py-3 px-4 rounded-xl bg-amber-500/20 border border-amber-500/40 text-amber-400 font-bold text-xs hover:bg-amber-500/30 transition flex items-center justify-center space-x-2 shadow-lg shadow-amber-500/10"
                    >
                      <Lock className="h-4 w-4" />
                      <span>Launch Simulated 2FA Challenge</span>
                    </button>
                  )}

                  {verificationSuccess && (
                    <div className="w-full mt-4 p-3 bg-emerald-500/15 border border-emerald-500/30 rounded-xl text-center text-xs font-bold text-emerald-400 flex items-center justify-center space-x-2">
                      <ShieldCheck className="h-4 w-4" />
                      <span>Verification Complete! Status Updated to Approved.</span>
                    </div>
                  )}
                </div>

                {/* Triggered Policy Rules */}
                <div className="md:col-span-6 bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-3">
                  <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                    Triggered Business Risk Rules
                  </h3>
                  <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
                    {evaluation.policy_triggers.map((trigger, idx) => (
                      <div
                        key={idx}
                        className="bg-slate-950 border border-slate-800 p-3 rounded-xl flex items-start justify-between"
                      >
                        <div>
                          <p className="text-xs font-bold text-slate-200">{trigger.rule_name}</p>
                          <p className="text-[11px] text-slate-400 mt-0.5">{trigger.description}</p>
                        </div>
                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase shrink-0 ml-2 ${
                          trigger.action === 'HOLD' ? 'bg-rose-500/20 text-rose-300' :
                          trigger.action === 'VERIFY' ? 'bg-amber-500/20 text-amber-300' :
                          'bg-emerald-500/20 text-emerald-300'
                        }`}>
                          {trigger.action}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

              </div>

              {/* SHAP Waterfall Chart */}
              <ShapWaterfall
                attributions={evaluation.explanations}
                naturalExplanation={evaluation.natural_explanation}
              />
            </>
          ) : (
            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-12 text-center space-y-3">
              <ShieldCheck className="h-12 w-12 text-slate-600 mx-auto" />
              <h3 className="text-base font-bold text-slate-300">Ready to Evaluate Risk</h3>
              <p className="text-xs text-slate-500 max-w-sm mx-auto">
                Select a demonstration scenario above or click "Evaluate Risk Engine" to calculate calibrated probabilities and SHAP explanations.
              </p>
            </div>
          )}

        </div>

      </div>

      {/* OTP Challenge Modal */}
      {evaluation && evaluation.challenge_token && (
        <OtpModal
          isOpen={isOtpOpen}
          transactionId={evaluation.transaction_id}
          challengeToken={evaluation.challenge_token}
          onSuccess={() => {
            setIsOtpOpen(false);
            setVerificationSuccess(true);
          }}
          onClose={() => setIsOtpOpen(false)}
        />
      )}

    </div>
  );
};
