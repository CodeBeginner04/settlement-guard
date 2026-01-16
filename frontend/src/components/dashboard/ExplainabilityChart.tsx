import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, ReferenceLine } from 'recharts';

interface ExplainabilityChartProps {
    shapData: {
        base_value: number;
        feature_contributions: number[];
    };
    featureNames: string[]; // We currently don't have these dynamically from API unless we pass them. Simplification: hardcode or generic names.
}

const ExplainabilityChart: React.FC<ExplainabilityChartProps> = ({ shapData }) => {
    // Simplified Mapping for Demo if we don't stream feature names
    // In a real app, API would send {feature: "SSI_Status", value: 0.3} pairs.
    // The current API sends a list of floats. We need the feature names from training.
    // Let's assume a fixed list for now based on training, or just labeled "Feature 1, 2..."
    // The training list was:
    // ['Notional_Amount_USD', 'Market_Volatility_Index', 'Trade_Hour', 'Asset_Class_Corp Bond'...] 

    // To make this look good for the demo, we will label the top contributors.
    // Since we don't have the explicit mapping in the API yet (it just returns list of values),
    // we will map indices to generic names or try to guess.

    // Ideally, the backend should return { "feature_name": contribution } dict.
    // But our schema was list[float]. Let's try to make it usable.

    const formattedData = shapData.feature_contributions.map((val, index) => ({
        name: `Feat ${index}`,
        value: val,
        fill: val > 0 ? '#ef4444' : '#10b981' // Red for risk increase, Green for decrease
    })).sort((a, b) => Math.abs(b.value) - Math.abs(a.value)) // Sort by magnitude
        .slice(0, 5); // Start with top 5

    return (
        <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 shadow-lg h-full">
            <h3 className="text-slate-400 text-sm font-semibold uppercase tracking-wider mb-4">Risk Drivers (SHAP)</h3>
            <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                    <BarChart layout="vertical" data={formattedData}>
                        <XAxis type="number" hide />
                        <YAxis dataKey="name" type="category" width={80} tick={{ fill: '#94a3b8', fontSize: 12 }} />
                        <Tooltip
                            cursor={{ fill: 'transparent' }}
                            contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#f1f5f9' }}
                        />
                        <ReferenceLine x={0} stroke="#475569" />
                        <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                            {formattedData.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={entry.fill} />
                            ))}
                        </Bar>
                    </BarChart>
                </ResponsiveContainer>
            </div>
            <p className="text-xs text-slate-500 mt-2 text-center">
                Red bars increase risk. Green bars decrease risk.
            </p>
        </div>
    );
};

export default ExplainabilityChart;
