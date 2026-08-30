import React from 'react';
import { AlertTriangle, CheckCircle, ShieldAlert, Lock } from 'lucide-react';

interface RiskGaugeProps {
  score: number; // 0-1000
  calibratedProba: number;
  rawProba: number;
  action: 'APPROVE' | 'VERIFY' | 'HOLD';
  riskLevel: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
}

export const RiskGauge: React.FC<RiskGaugeProps> = ({
  score,
  calibratedProba,
  rawProba,
  action,
  riskLevel,
}) => {
  const percentage = Math.min(100, Math.max(0, (score / 1000) * 100));

  const getActionBadge = () => {
    switch (action) {
      case 'APPROVE':
        return (
          <div className="flex items-center space-x-2 px-4 py-2 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
            <CheckCircle className="h-5 w-5" />
            <span className="font-bold text-base tracking-wider">ACTION: APPROVE</span>
          </div>
        );
      case 'VERIFY':
        return (
          <div className="flex items-center space-x-2 px-4 py-2 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-400 animate-pulse">
            <Lock className="h-5 w-5" />
            <span className="font-bold text-base tracking-wider">ACTION: VERIFY (2FA OTP)</span>
          </div>
        );
      case 'HOLD':
        return (
          <div className="flex items-center space-x-2 px-4 py-2 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400">
            <ShieldAlert className="h-5 w-5" />
            <span className="font-bold text-base tracking-wider">ACTION: HOLD / REVIEW</span>
          </div>
        );
    }
  };

  const getScoreColor = () => {
    if (score < 250) return 'text-emerald-400 border-emerald-500';
    if (score < 650) return 'text-amber-400 border-amber-500';
    if (score < 850) return 'text-orange-400 border-orange-500';
    return 'text-red-400 border-red-500';
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 flex flex-col items-center justify-between shadow-xl">
      <div className="w-full flex items-center justify-between mb-4">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Transaction Risk Score</span>
        <span className={`text-xs font-bold px-2.5 py-1 rounded-full uppercase ${
          riskLevel === 'LOW' ? 'bg-emerald-500/20 text-emerald-300' :
          riskLevel === 'MEDIUM' ? 'bg-amber-500/20 text-amber-300' :
          riskLevel === 'HIGH' ? 'bg-orange-500/20 text-orange-300' :
          'bg-red-500/20 text-red-300'
        }`}>
          {riskLevel} RISK
        </span>
      </div>

      {/* Circle Gauge Meter */}
      <div className="relative w-48 h-48 flex items-center justify-center my-2">
        <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
          {/* Background track */}
          <circle
            cx="50"
            cy="50"
            r="40"
            stroke="currentColor"
            strokeWidth="8"
            className="text-slate-800"
            fill="transparent"
          />
          {/* Progress track */}
          <circle
            cx="50"
            cy="50"
            r="40"
            stroke="currentColor"
            strokeWidth="8"
            strokeDasharray={251.2}
            strokeDashoffset={251.2 - (251.2 * percentage) / 100}
            strokeLinecap="round"
            className={`transition-all duration-1000 ease-out ${getScoreColor()}`}
            fill="transparent"
          />
        </svg>

        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={`text-4xl font-extrabold font-mono tracking-tight ${getScoreColor().split(' ')[0]}`}>
            {score}
          </span>
          <span className="text-xs text-slate-400 font-medium">out of 1000</span>
        </div>
      </div>

      {/* Action Badge */}
      <div className="w-full mt-4 flex justify-center">
        {getActionBadge()}
      </div>

      {/* Probability Details */}
      <div className="w-full grid grid-cols-2 gap-3 mt-6 pt-4 border-t border-slate-800 text-center">
        <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-800">
          <p className="text-xs text-slate-400">Calibrated Fraud Prob.</p>
          <p className="text-sm font-bold font-mono text-cyan-400">{(calibratedProba * 100).toFixed(2)}%</p>
        </div>
        <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-800">
          <p className="text-xs text-slate-400">Raw Logit Proba.</p>
          <p className="text-sm font-bold font-mono text-slate-400">{(rawProba * 100).toFixed(2)}%</p>
        </div>
      </div>

    </div>
  );
};
