import React from 'react';
import { ShieldCheck, Activity, Sliders, BarChart3, Database, ShieldAlert } from 'lucide-react';

interface NavbarProps {
  activeTab: 'simulator' | 'analyst' | 'policies' | 'metrics' | 'public_benchmark';
  setActiveTab: (tab: 'simulator' | 'analyst' | 'policies' | 'metrics' | 'public_benchmark') => void;
  pendingQueueCount: number;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab, pendingQueueCount }) => {
  return (
    <header className="border-b border-slate-800 bg-slate-900/90 backdrop-blur-md sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
        
        {/* Brand */}
        <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveTab('simulator')}>
          <div className="h-11 w-11 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
            <ShieldCheck className="h-6 w-6 text-white" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-extrabold text-xl tracking-tight text-white font-mono">PAYGUARD</span>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">AI PLATFORM</span>
            </div>
            <p className="text-xs text-slate-400">AI-Powered Payment Fraud Detection & Risk Intelligence</p>
          </div>
        </div>

        {/* Nav Tabs */}
        <nav className="hidden md:flex space-x-1 lg:space-x-2">
          <button
            onClick={() => setActiveTab('simulator')}
            className={`flex flex-col items-start px-3.5 py-2 rounded-xl text-left transition-all ${
              activeTab === 'simulator'
                ? 'bg-cyan-500/15 text-cyan-400 border border-cyan-500/30 shadow-md shadow-cyan-500/5'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <div className="flex items-center space-x-1.5 text-xs font-bold">
              <Activity className="h-3.5 w-3.5" />
              <span>Risk Simulator</span>
            </div>
            <span className="text-[10px] opacity-75 font-normal">Synthetic Demo</span>
          </button>

          <button
            onClick={() => setActiveTab('analyst')}
            className={`relative flex flex-col items-start px-3.5 py-2 rounded-xl text-left transition-all ${
              activeTab === 'analyst'
                ? 'bg-amber-500/15 text-amber-400 border border-amber-500/30 shadow-md shadow-amber-500/5'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <div className="flex items-center space-x-1.5 text-xs font-bold">
              <ShieldAlert className="h-3.5 w-3.5" />
              <span>Analyst Queue</span>
              {pendingQueueCount > 0 && (
                <span className="ml-1 px-1.5 py-0.2 text-[10px] font-bold bg-amber-500 text-slate-950 rounded-full animate-pulse">
                  {pendingQueueCount}
                </span>
              )}
            </div>
            <span className="text-[10px] opacity-75 font-normal">Human-in-the-Loop</span>
          </button>

          <button
            onClick={() => setActiveTab('policies')}
            className={`flex flex-col items-start px-3.5 py-2 rounded-xl text-left transition-all ${
              activeTab === 'policies'
                ? 'bg-purple-500/15 text-purple-400 border border-purple-500/30 shadow-md shadow-purple-500/5'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <div className="flex items-center space-x-1.5 text-xs font-bold">
              <Sliders className="h-3.5 w-3.5" />
              <span>Policy Engine</span>
            </div>
            <span className="text-[10px] opacity-75 font-normal">Escalation Rules</span>
          </button>

          <button
            onClick={() => setActiveTab('metrics')}
            className={`flex flex-col items-start px-3.5 py-2 rounded-xl text-left transition-all ${
              activeTab === 'metrics'
                ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 shadow-md shadow-emerald-500/5'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <div className="flex items-center space-x-1.5 text-xs font-bold">
              <BarChart3 className="h-3.5 w-3.5" />
              <span>System Health</span>
            </div>
            <span className="text-[10px] opacity-75 font-normal">Metrics & Audit</span>
          </button>

          <button
            onClick={() => setActiveTab('public_benchmark')}
            className={`flex flex-col items-start px-3.5 py-2 rounded-xl text-left transition-all ${
              activeTab === 'public_benchmark'
                ? 'bg-blue-500/15 text-blue-400 border border-blue-500/30 shadow-md shadow-blue-500/5'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <div className="flex items-center space-x-1.5 text-xs font-bold">
              <Database className="h-3.5 w-3.5" />
              <span>Public Benchmark</span>
            </div>
            <span className="text-[10px] opacity-75 font-normal">Frozen ML Benchmark</span>
          </button>
        </nav>

        {/* System Badge */}
        <div className="flex items-center space-x-2 text-xs bg-slate-950 px-3.5 py-1.5 rounded-xl border border-slate-800">
          <span className="h-2 w-2 rounded-full bg-emerald-400 animate-ping"></span>
          <span className="text-slate-300 font-mono text-[11px]">XGBoost + Isotonic Calibrated</span>
        </div>

      </div>
    </header>
  );
};
