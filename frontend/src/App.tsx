import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { SimulatorPage } from './pages/SimulatorPage';
import { AnalystPage } from './pages/AnalystPage';
import { PolicyPage } from './pages/PolicyPage';
import { MetricsPage } from './pages/MetricsPage';
import { PublicBenchmarkPage } from './pages/PublicBenchmarkPage';
import { api } from './services/api';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'simulator' | 'analyst' | 'policies' | 'metrics' | 'public_benchmark'>('simulator');
  const [pendingQueueCount, setPendingQueueCount] = useState(0);

  useEffect(() => {
    const fetchQueueCount = async () => {
      try {
        const queue = await api.getAnalystQueue('ESCALATED_TO_ANALYST');
        setPendingQueueCount(queue.length);
      } catch (err) {
        // Silently handle if backend is starting
      }
    };
    fetchQueueCount();
    const interval = setInterval(fetchQueueCount, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col selection:bg-cyan-500 selection:text-white">
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        pendingQueueCount={pendingQueueCount}
      />

      <main className="flex-1">
        {activeTab === 'simulator' && <SimulatorPage />}
        {activeTab === 'analyst' && <AnalystPage />}
        {activeTab === 'policies' && <PolicyPage />}
        {activeTab === 'metrics' && <MetricsPage />}
        {activeTab === 'public_benchmark' && <PublicBenchmarkPage />}
      </main>

      <footer className="border-t border-slate-900 bg-slate-950 py-6 text-center text-xs text-slate-500">
        <p>PAYGUARD AI &mdash; Explainable Adaptive Transaction Risk Manager &bull; Hackathon Technical Submission</p>
      </footer>
    </div>
  );
};
