import React from 'react';

interface ActionPanelProps {
    onAutoCorrect: () => void;
    isProcessing: boolean;
}

const ActionPanel: React.FC<ActionPanelProps> = ({ onAutoCorrect, isProcessing }) => {
    return (
        <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 shadow-lg flex flex-col justify-between">
            <div>
                <h3 className="text-slate-400 text-sm font-semibold uppercase tracking-wider mb-2">Prescriptive Action</h3>
                <p className="text-slate-300 text-sm mb-4">
                    Correct Standing Settlement Instructions (SSI) to match Counterparty preferences.
                </p>
            </div>
            <button
                onClick={onAutoCorrect}
                disabled={isProcessing}
                className={`w-full py-3 px-4 rounded-lg font-bold text-white transition-all transform hover:scale-105 active:scale-95 shadow-lg
            ${isProcessing
                        ? 'bg-slate-600 cursor-not-allowed'
                        : 'bg-indigo-600 hover:bg-indigo-500 shadow-indigo-500/30'
                    }`}
            >
                {isProcessing ? 'Processing Match...' : 'Auto-Correct SSI'}
            </button>
        </div>
    );
};

export default ActionPanel;
