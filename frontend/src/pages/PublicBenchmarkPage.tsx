import React, { useState } from 'react';
import { Database, AlertTriangle, CheckCircle2, ShieldAlert, Cpu, Activity, BarChart2, Info, ChevronDown, ChevronUp, Sparkles, HelpCircle } from 'lucide-react';
import { api } from '../services/api';
import { PublicPredictionPayload, PublicPredictionResponse } from '../types/api';

const DEFAULT_SAMPLE_LEGIT: PublicPredictionPayload = {
  Time: 100.0,
  V1: 0.05, V2: -0.10, V3: 0.85, V4: -0.40, V5: 0.12,
  V6: -0.05, V7: 0.20, V8: 0.01, V9: 0.15, V10: 0.08,
  V11: -0.20, V12: 0.45, V13: -0.10, V14: 0.30, V15: 0.05,
  V16: 0.10, V17: 0.25, V18: -0.15, V19: 0.02, V20: -0.05,
  V21: 0.01, V22: 0.05, V23: -0.02, V24: 0.10, V25: -0.05,
  V26: 0.02, V27: 0.01, V28: -0.01,
  Amount: 49.99,
  include_explanations: true
};

const DEFAULT_SAMPLE_FRAUD: PublicPredictionPayload = {
  Time: 406.0,
  V1: -2.3122, V2: 1.9519, V3: -1.6098, V4: 3.9979, V5: -0.5221,
  V6: -1.4265, V7: -2.5373, V8: 1.3916, V9: -2.7700, V10: -2.7722,
  V11: 3.2020, V12: -2.8999, V13: -0.5952, V14: -4.2892, V15: 0.3897,
  V16: -1.1407, V17: -2.8300, V18: -0.0168, V19: 0.4169, V20: 0.1269,
  V21: 0.5172, V22: -0.0350, V23: -0.4652, V24: 0.3201, V25: 0.0445,
  V26: 0.1778, V27: 0.2611, V28: -0.1432,
  Amount: 0.00,
  include_explanations: true
};

export const PublicBenchmarkPage: React.FC = () => {
  const [formData, setFormData] = useState<PublicPredictionPayload>(DEFAULT_SAMPLE_LEGIT);
  const [result, setResult] = useState<PublicPredictionResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [isPcaExpanded, setIsPcaExpanded] = useState<boolean>(false);
  const [showPcaHelp, setShowPcaHelp] = useState<boolean>(false);

  const handleInputChange = (field: keyof PublicPredictionPayload, val: string) => {
    const num = parseFloat(val);
    setFormData(prev => ({
      ...prev,
      [field]: isNaN(num) ? 0 : num
    }));
  };

  const handlePresetSelect = (preset: 'legit' | 'fraud') => {
    setError(null);
    setResult(null);
    setFormData(preset === 'fraud' ? DEFAULT_SAMPLE_FRAUD : DEFAULT_SAMPLE_LEGIT);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const res = await api.predictPublicBenchmark({
        ...formData,
        include_explanations: true
      });
      setResult(res);
    } catch (err: any) {
      console.error("Public benchmark inference error:", err);
      setError("Unable to analyze the transaction. Please check the entered values and try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Header Banner */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 sm:p-8 backdrop-blur-md relative overflow-hidden">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 relative z-10">
          <div className="space-y-2 max-w-3xl">
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold">
              <Database size={14} />
              <span>Public Fraud Benchmark Pipeline</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Public Fraud Benchmark
            </h1>
            <p className="text-sm text-slate-400">
              Evaluate a transaction using the frozen PayGuard AI public benchmark model trained on the Kaggle Credit Card dataset.
            </p>
          </div>

          {/* Quick Info Badges */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 shrink-0">
            <div className="bg-slate-950/80 border border-slate-800 p-2.5 rounded-xl text-center">
              <span className="text-[10px] font-bold text-slate-500 uppercase block">Model</span>
              <span className="text-xs font-bold text-blue-400 font-mono">v1.0.0</span>
            </div>
            <div className="bg-slate-950/80 border border-slate-800 p-2.5 rounded-xl text-center">
              <span className="text-[10px] font-bold text-slate-500 uppercase block">Calibration</span>
              <span className="text-xs font-bold text-cyan-400 font-mono">Isotonic</span>
            </div>
            <div className="bg-slate-950/80 border border-slate-800 p-2.5 rounded-xl text-center">
              <span className="text-[10px] font-bold text-slate-500 uppercase block">Threshold</span>
              <span className="text-xs font-bold text-slate-200 font-mono">0.5</span>
            </div>
            <div className="bg-slate-950/80 border border-slate-800 p-2.5 rounded-xl text-center">
              <span className="text-[10px] font-bold text-slate-500 uppercase block">Benchmark</span>
              <span className="text-xs font-bold text-emerald-400 font-mono">Public Dataset</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Grid: Form + Results */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Form Column (7 Cols) */}
        <div className="lg:col-span-7 space-y-6">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
            
            <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-4">
              <div>
                <h2 className="text-base font-bold text-white flex items-center space-x-2">
                  <Cpu size={18} className="text-blue-400" />
                  <span>Transaction Features</span>
                </h2>
                <p className="text-xs text-slate-400">Time, Amount, and 28 PCA-transformed components</p>
              </div>

              {/* Sample Presets */}
              <div className="flex items-center space-x-2">
                <button
                  type="button"
                  onClick={() => handlePresetSelect('legit')}
                  className="px-3 py-1.5 rounded-xl text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 hover:bg-emerald-500/20 transition"
                >
                  Load Legit Sample
                </button>
                <button
                  type="button"
                  onClick={() => handlePresetSelect('fraud')}
                  className="px-3 py-1.5 rounded-xl text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/30 hover:bg-rose-500/20 transition"
                >
                  Load Fraud Sample
                </button>
              </div>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              
              {/* Primary Transaction Features */}
              <div className="space-y-3">
                <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                  Core Transaction Inputs
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 bg-slate-950/60 p-4 rounded-xl border border-slate-800">
                  <div>
                    <label className="block text-xs font-medium text-slate-300 mb-1">
                      Amount ($) <span className="text-rose-400">*</span>
                    </label>
                    <input
                      type="number"
                      step="any"
                      min="0"
                      value={formData.Amount}
                      onChange={(e) => handleInputChange("Amount", e.target.value)}
                      className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2.5 text-sm text-cyan-400 font-mono font-bold focus:border-blue-500 focus:outline-none"
                      required
                    />
                    <p className="text-[10px] text-slate-500 mt-1">Transaction dollar amount</p>
                  </div>

                  <div>
                    <label className="block text-xs font-medium text-slate-300 mb-1">
                      Time (sec) <span className="text-rose-400">*</span>
                    </label>
                    <input
                      type="number"
                      step="any"
                      min="0"
                      value={formData.Time}
                      onChange={(e) => handleInputChange("Time", e.target.value)}
                      className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2.5 text-sm text-slate-200 font-mono focus:border-blue-500 focus:outline-none"
                      required
                    />
                    <p className="text-[10px] text-slate-500 mt-1">Seconds elapsed since first dataset transaction</p>
                  </div>
                </div>
              </div>

              {/* PCA Features Collapsible Section */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                      Advanced Model Features (PCA Components V1 — V28)
                    </h3>
                    <button
                      type="button"
                      onClick={() => setShowPcaHelp(!showPcaHelp)}
                      className="text-slate-400 hover:text-cyan-400 transition"
                      title="What is PCA?"
                    >
                      <HelpCircle size={14} />
                    </button>
                  </div>
                  
                  <button
                    type="button"
                    onClick={() => setIsPcaExpanded(!isPcaExpanded)}
                    className="flex items-center space-x-1.5 text-xs font-semibold text-blue-400 hover:text-blue-300 transition"
                  >
                    <span>{isPcaExpanded ? "Collapse PCA Inputs" : "Expand All 28 PCA Inputs"}</span>
                    {isPcaExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                  </button>
                </div>

                {/* PCA Help Box */}
                {showPcaHelp && (
                  <div className="bg-slate-950 border border-cyan-500/30 p-3.5 rounded-xl text-xs text-cyan-200/90 space-y-1">
                    <p className="font-semibold text-cyan-400">Why are these features technical?</p>
                    <p className="text-[11px] leading-relaxed text-slate-300">
                      PCA (Principal Component Analysis) is a dimensionality-reduction technique used to transform original confidential numerical variables into a smaller set of mathematical components.
                    </p>
                    <p className="text-[11px] leading-relaxed text-amber-300/90 pt-1">
                      V1–V28 are PCA-transformed numerical components. They do not directly correspond to business concepts such as device risk, IP reputation, transaction velocity, OTP failures, or merchant risk.
                    </p>
                  </div>
                )}

                {/* PCA Inputs Grid (Always shows 4 key features, expands all 28) */}
                <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800 space-y-3">
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                    {Array.from({ length: isPcaExpanded ? 28 : 8 }, (_, idx) => {
                      const featName = `V${idx + 1}` as keyof PublicPredictionPayload;
                      return (
                        <div key={featName} className="bg-slate-900 border border-slate-800 p-2.5 rounded-lg">
                          <label className="block text-[11px] font-mono text-slate-400 mb-1">
                            {featName} <span className="text-[9px] text-slate-500">(PCA)</span>
                          </label>
                          <input
                            type="number"
                            step="any"
                            value={formData[featName] as number}
                            onChange={(e) => handleInputChange(featName, e.target.value)}
                            className="w-full bg-slate-950 border border-slate-800 rounded px-2 py-1 text-xs text-slate-200 font-mono focus:border-blue-500 focus:outline-none"
                          />
                        </div>
                      );
                    })}
                  </div>

                  {!isPcaExpanded && (
                    <button
                      type="button"
                      onClick={() => setIsPcaExpanded(true)}
                      className="w-full py-2 text-center text-xs font-semibold text-slate-400 hover:text-slate-200 transition bg-slate-900/60 rounded-lg border border-slate-800"
                    >
                      + Show Remaining 20 PCA Features
                    </button>
                  )}
                </div>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading}
                className="w-full py-3.5 px-4 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 disabled:opacity-50 text-white font-bold rounded-xl shadow-lg shadow-blue-500/20 transition flex items-center justify-center space-x-2"
              >
                {loading ? (
                  <>
                    <Activity className="animate-spin h-5 w-5 text-white" />
                    <span>Analyzing transaction...</span>
                  </>
                ) : (
                  <>
                    <Cpu className="h-5 w-5 text-white" />
                    <span>Analyze Public Benchmark Transaction</span>
                  </>
                )}
              </button>
            </form>
          </div>
        </div>

        {/* Output Column (5 Cols) */}
        <div className="lg:col-span-5 space-y-6">
          {error && (
            <div className="bg-rose-500/10 border border-rose-500/30 rounded-2xl p-4 text-xs text-rose-300">
              <p className="font-semibold">{error}</p>
            </div>
          )}

          {result ? (
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
              
              {/* Prominent Assessment Card */}
              <div className={`p-6 rounded-2xl border text-center space-y-3 relative overflow-hidden ${
                result.decision === 'FRAUD'
                  ? 'bg-rose-500/15 border-rose-500/40 text-rose-400'
                  : 'bg-emerald-500/15 border-emerald-500/40 text-emerald-400'
              }`}>
                <div className="inline-flex p-3 rounded-2xl bg-slate-950/80 border border-current">
                  {result.decision === 'FRAUD' ? (
                    <ShieldAlert size={36} className="text-rose-400" />
                  ) : (
                    <CheckCircle2 size={36} className="text-emerald-400" />
                  )}
                </div>

                <div>
                  <span className="text-[10px] font-extrabold uppercase tracking-widest block opacity-75">
                    MODEL ASSESSMENT RESULT
                  </span>
                  <h3 className="text-2xl font-black tracking-tight mt-1 font-mono">
                    {result.decision === 'FRAUD' ? 'FRAUD DETECTED' : 'LEGITIMATE TRANSACTION'}
                  </h3>
                  <p className="text-xs opacity-90 mt-1">
                    {result.decision === 'FRAUD'
                      ? 'Model assessment indicates this transaction is above the configured benchmark threshold.'
                      : 'Model assessment indicates this transaction is below the configured benchmark threshold.'}
                  </p>
                </div>
              </div>

              {/* Visual Probability Progress Indicator */}
              <div className="space-y-3 bg-slate-950 p-4 rounded-xl border border-slate-800">
                <div className="flex justify-between items-center text-xs">
                  <span className="text-slate-400">Calibrated Risk Probability:</span>
                  <span className="font-mono text-cyan-400 font-bold text-sm">{(result.calibrated_probability * 100).toFixed(2)}%</span>
                </div>

                {/* Probability Bar */}
                <div className="relative w-full bg-slate-800 h-3 rounded-full overflow-hidden">
                  <div
                    className={`h-full transition-all duration-500 ${
                      result.decision === 'FRAUD' ? 'bg-rose-500' : 'bg-emerald-500'
                    }`}
                    style={{ width: `${Math.min(100, Math.max(0, result.calibrated_probability * 100))}%` }}
                  />
                  {/* Threshold Marker */}
                  <div
                    className="absolute top-0 bottom-0 w-0.5 bg-white z-10"
                    style={{ left: '50%' }}
                    title="Threshold: 50%"
                  />
                </div>

                <div className="flex justify-between items-center text-[10px] text-slate-500">
                  <span>0%</span>
                  <span className="text-slate-300 font-semibold font-mono">50% Threshold</span>
                  <span>100%</span>
                </div>

                <div className="pt-2 border-t border-slate-900 flex justify-between items-center text-[11px]">
                  <span className="text-slate-400">Raw Probability: <strong className="text-slate-200 font-mono">{(result.raw_probability * 100).toFixed(2)}%</strong></span>
                  <span className="text-slate-500 text-[10px]">Method: {result.calibration_method}</span>
                </div>

                <p className="text-[10px] text-slate-500 italic pt-1">
                  Calibrated probability is the probability after isotonic calibration.
                </p>
              </div>

              {/* SHAP Explanation Section */}
              {result.top_positive_features && result.top_positive_features.length > 0 && (
                <div className="space-y-3 pt-2 border-t border-slate-800">
                  <div>
                    <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wider">
                      Why did the model make this prediction?
                    </h4>
                    <p className="text-[11px] text-slate-400">Model contribution analysis (SHAP TreeExplainer)</p>
                  </div>

                  <div className="space-y-2">
                    {result.top_positive_features.map(f => (
                      <div key={f.feature} className="bg-slate-950 border border-slate-800 p-2.5 rounded-xl flex items-center justify-between text-xs">
                        <div>
                          <span className="font-mono font-bold text-slate-200">{f.feature} &mdash; PCA-transformed component</span>
                          <span className="text-[10px] text-slate-500 block">Feature value = {f.feature_value}</span>
                        </div>
                        <span className="font-mono font-bold text-rose-400">+{f.shap_value.toFixed(4)}</span>
                      </div>
                    ))}
                  </div>

                  <p className="text-[10px] text-slate-500 italic">
                    SHAP values show how features contributed to the model prediction. They indicate model contribution, not causality.
                  </p>
                </div>
              )}

            </div>
          ) : (
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-12 text-center text-slate-500 space-y-3">
              <Cpu size={40} className="mx-auto text-slate-600" />
              <p className="text-xs font-medium text-slate-400">
                Click a sample preset above or fill transaction features, then click <strong>Analyze Public Benchmark Transaction</strong>.
              </p>
            </div>
          )}

          {/* Model Benchmark Performance Section */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4 shadow-xl">
            <div className="flex items-center space-x-2 text-slate-200 font-bold text-xs uppercase tracking-wider">
              <BarChart2 size={16} className="text-emerald-400" />
              <span>Model Benchmark Performance</span>
            </div>
            <p className="text-[11px] text-slate-400">
              These are frozen held-out benchmark evaluation results (Test Set, N=42,722).
            </p>

            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5">
              <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-800">
                <span className="text-[10px] text-slate-500 block">PR-AUC (Primary)</span>
                <span className="text-base font-bold text-emerald-400 font-mono">0.7842</span>
              </div>
              <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-800">
                <span className="text-[10px] text-slate-500 block">ROC-AUC</span>
                <span className="text-base font-bold text-slate-200 font-mono">0.9586</span>
              </div>
              <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-800">
                <span className="text-[10px] text-slate-500 block">Precision</span>
                <span className="text-base font-bold text-slate-200 font-mono">0.9423</span>
              </div>
              <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-800">
                <span className="text-[10px] text-slate-500 block">Recall</span>
                <span className="text-base font-bold text-slate-200 font-mono">0.6622</span>
              </div>
              <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-800">
                <span className="text-[10px] text-slate-500 block">F1 Score</span>
                <span className="text-base font-bold text-slate-200 font-mono">0.7778</span>
              </div>
              <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-800">
                <span className="text-[10px] text-slate-500 block">Brier Score</span>
                <span className="text-base font-bold text-slate-200 font-mono">0.0005</span>
              </div>
            </div>

            <div className="bg-slate-950/80 p-3 rounded-xl border border-slate-800 text-[10px] text-slate-400 leading-relaxed space-y-1">
              <div className="flex items-center space-x-1.5 text-amber-400 font-semibold">
                <AlertTriangle size={12} />
                <span>Research Benchmark Disclaimer</span>
              </div>
              <p>
                The public benchmark pipeline is intended for research, reproducibility, benchmarking, and demonstration. Its benchmark performance does not imply production payment-fraud detection capability.
              </p>
            </div>
          </div>

        </div>

      </div>

    </div>
  );
};
