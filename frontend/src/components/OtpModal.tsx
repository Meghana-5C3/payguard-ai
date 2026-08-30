import React, { useState } from 'react';
import { Lock, CheckCircle2, AlertCircle, ShieldAlert } from 'lucide-react';
import { api } from '../services/api';

interface OtpModalProps {
  isOpen: boolean;
  transactionId: string;
  challengeToken: string;
  onSuccess: () => void;
  onClose: () => void;
}

export const OtpModal: React.FC<OtpModalProps> = ({
  isOpen,
  transactionId,
  challengeToken,
  onSuccess,
  onClose
}) => {
  const [otpCode, setOtpCode] = useState('849201');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await api.verifyChallenge(transactionId, challengeToken, otpCode);
      onSuccess();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Verification failed. Please check OTP code.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-fadeIn">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-5">
        
        <div className="flex items-center space-x-3">
          <div className="h-12 w-12 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400">
            <Lock className="h-6 w-6" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">2FA Verification Required</h3>
            <p className="text-xs text-slate-400">Transaction step-up challenge triggered by Risk Policy</p>
          </div>
        </div>

        <div className="bg-slate-950 p-3.5 rounded-xl border border-slate-800 text-xs space-y-1 font-mono text-slate-300">
          <div className="flex justify-between">
            <span className="text-slate-400">Transaction ID:</span>
            <span className="text-cyan-400 font-bold">{transactionId.slice(0, 16)}...</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Challenge Token:</span>
            <span>{challengeToken}</span>
          </div>
        </div>

        <form onSubmit={handleVerify} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">
              Simulated SMS / Authenticator OTP Code
            </label>
            <input
              type="text"
              maxLength={6}
              value={otpCode}
              onChange={(e) => setOtpCode(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-center text-2xl font-mono tracking-widest text-cyan-400 focus:outline-none focus:border-cyan-500"
              placeholder="123456"
              required
            />
            <p className="text-xs text-slate-400 mt-1 text-center">
              (Enter any 6-digit number to simulate customer verification)
            </p>
          </div>

          {error && (
            <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-xl flex items-center space-x-2 text-xs text-red-400">
              <AlertCircle className="h-4 w-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <div className="flex space-x-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-2.5 px-4 rounded-xl border border-slate-800 text-sm font-semibold text-slate-400 hover:bg-slate-800 transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 py-2.5 px-4 rounded-xl bg-gradient-to-r from-amber-500 to-orange-600 text-slate-950 font-bold text-sm hover:brightness-110 transition shadow-lg shadow-amber-500/20 disabled:opacity-50"
            >
              {loading ? 'Verifying...' : 'Submit Code'}
            </button>
          </div>
        </form>

      </div>
    </div>
  );
};
