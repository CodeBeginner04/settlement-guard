import React from 'react';
import { clsx } from 'clsx';

interface RiskGaugeProps {
    probability: number; // 0 to 1
    riskLevel: string;
}

const RiskGauge: React.FC<RiskGaugeProps> = ({ probability, riskLevel }) => {
    // Convert 0-1 to 0-180 degrees
    const rotation = probability * 180;

    const colorClass =
        probability > 0.8 ? 'text-red-500' :
            probability > 0.5 ? 'text-orange-500' :
                'text-emerald-500';

    const bgClass =
        probability > 0.8 ? 'bg-red-500' :
            probability > 0.5 ? 'bg-orange-500' :
                'bg-emerald-500';

    return (
        <div className="flex flex-col items-center justify-center p-6 bg-slate-800 rounded-xl border border-slate-700 shadow-lg">
            <h3 className="text-slate-400 text-sm font-semibold uppercase tracking-wider mb-4">Settlement Risk Score</h3>

            {/* Semi Circle Gauge */}
            <div className="relative w-48 h-24 overflow-hidden mb-2">
                <div className="absolute w-48 h-48 bg-slate-700 rounded-full"></div>
                <div
                    className={clsx("absolute w-48 h-48 rounded-full origin-bottom transition-transform duration-1000 ease-out opacity-80", bgClass)}
                    style={{ transform: `rotate(${rotation - 180}deg)` }}
                ></div>
                <div className="absolute w-40 h-40 bg-slate-800 rounded-full bottom-0 left-4 z-10 flex items-end justify-center pb-2">
                    <span className={clsx("text-4xl font-bold font-mono", colorClass)}>
                        {(probability * 100).toFixed(1)}%
                    </span>
                </div>
            </div>

            <div className={clsx("mt-2 px-3 py-1 rounded-full text-xs font-bold bg-opacity-20 border border-opacity-30", bgClass.replace('bg-', 'bg-'), colorClass.replace('text-', 'border-'))}>
                {riskLevel} RISK
            </div>
        </div>
    );
};

export default RiskGauge;
