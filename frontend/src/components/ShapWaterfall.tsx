import React from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
  ReferenceLine
} from 'recharts';
import { ShapAttribution } from '../types/api';
import { Info, AlertCircle } from 'lucide-react';

interface ShapWaterfallProps {
  attributions: ShapAttribution[];
  naturalExplanation: string;
}

export const ShapWaterfall: React.FC<ShapWaterfallProps> = ({
  attributions,
  naturalExplanation
}) => {
  // Sort top 7 attributions by absolute impact
  const data = attributions.slice(0, 7).map((item) => ({
    name: item.label,
    shapValue: item.raw_shap_value,
    impact: item.impact,
    direction: item.direction,
    description: item.description,
    value: item.value
  }));

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col justify-between">
      
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-base font-bold text-white flex items-center space-x-2">
            <span>Explainable AI Attribution (SHAP)</span>
            <span className="text-xs px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 font-mono">
              TreeExplainer
            </span>
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Local SHAP value contribution per feature for this specific transaction
          </p>
        </div>
      </div>

      {/* SHAP Bar Chart */}
      <div className="h-64 w-full my-2">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={data}
            layout="vertical"
            margin={{ top: 5, right: 30, left: 100, bottom: 5 }}
          >
            <XAxis type="number" stroke="#64748b" tick={{ fontSize: 11 }} />
            <YAxis
              dataKey="name"
              type="category"
              stroke="#94a3b8"
              tick={{ fontSize: 11 }}
              width={160}
            />
            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const d = payload[0].payload;
                  return (
                    <div className="bg-slate-950 border border-slate-800 p-3 rounded-lg shadow-xl max-w-xs text-xs">
                      <p className="font-bold text-white mb-1">{d.name}</p>
                      <p className="text-slate-300 mb-1">
                        Recorded Value: <span className="font-mono text-cyan-400">{String(d.value)}</span>
                      </p>
                      <p className="text-slate-300 mb-2">
                        SHAP Impact: <span className={`font-mono font-bold ${d.shapValue > 0 ? 'text-red-400' : 'text-emerald-400'}`}>{d.impact}</span>
                      </p>
                      <p className="text-slate-400 italic border-t border-slate-800 pt-1.5">{d.description}</p>
                    </div>
                  );
                }
                return null;
              }}
            />
            <ReferenceLine x={0} stroke="#475569" strokeDasharray="3 3" />
            <Bar dataKey="shapValue" radius={[0, 4, 4, 0]}>
              {data.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={entry.shapValue > 0 ? '#f87171' : '#34d399'}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Legend & Summary */}
      <div className="space-y-3 pt-3 border-t border-slate-800">
        <div className="flex items-center space-x-6 text-xs text-slate-400">
          <div className="flex items-center space-x-2">
            <span className="h-3 w-3 rounded-sm bg-red-400 inline-block"></span>
            <span>Increases Risk Score (+SHAP)</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="h-3 w-3 rounded-sm bg-emerald-400 inline-block"></span>
            <span>Reduces Risk Score (-SHAP)</span>
          </div>
        </div>

        {/* Natural Language Explanation Box */}
        <div className="bg-slate-950 p-3.5 rounded-xl border border-slate-800 flex items-start space-x-3">
          <Info className="h-5 w-5 text-cyan-400 shrink-0 mt-0.5" />
          <div className="text-xs">
            <span className="font-semibold text-slate-200">Natural Language Rationale: </span>
            <span className="text-slate-300 leading-relaxed">{naturalExplanation}</span>
          </div>
        </div>
      </div>

    </div>
  );
};
