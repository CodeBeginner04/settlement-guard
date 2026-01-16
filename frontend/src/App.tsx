import { useState } from 'react';
import { analyzeTrade } from './services/api';
import type { TradeRequest } from './services/api';
import RiskGauge from './components/dashboard/RiskGauge';
import ExplainabilityChart from './components/dashboard/ExplainabilityChart';
import LiveFeedTable from './components/dashboard/LiveFeedTable';
import ActionPanel from './components/dashboard/ActionPanel';

// Mock Data for Table
const MOCK_TRADES = [
  { Trade_ID: 'TRD-2024-001', Asset_Class: 'Corp Bond', Counterparty: 'Lehman Bros Legacy', failure_probability: 0.92, risk_level: 'CRITICAL', shap_explanation: { base_value: 0, feature_contributions: [0.5, 0.3, 0] } },
  { Trade_ID: 'TRD-2024-002', Asset_Class: 'Equity', Counterparty: 'Goldman Sachs', failure_probability: 0.05, risk_level: 'LOW', shap_explanation: { base_value: 0, feature_contributions: [] } },
  { Trade_ID: 'TRD-2024-003', Asset_Class: 'FX', Counterparty: 'JP Morgan', failure_probability: 0.12, risk_level: 'LOW', shap_explanation: { base_value: 0, feature_contributions: [] } },
];

function App() {
  const [selectedTrade, setSelectedTrade] = useState<any>(MOCK_TRADES[0]);
  const [tableData, setTableData] = useState<any[]>(MOCK_TRADES);
  const [analyzing, setAnalyzing] = useState(false);

  // Simulation Function
  const simulateNewTrade = async () => {
    // Defines a "Risky" trade (SSI Mismatch)
    const riskyTrade: TradeRequest = {
      Notional_Amount_USD: 15000000,
      Market_Volatility_Index: 35.0, // High Volatility
      Asset_Class: 'Corp Bond',
      Counterparty_Rating: 'CCC',
      SSI_Status: 'Mismatch', // FATAL
      Liquidity_Score: 'Low',
      Custodian_Location: 'EU',
      Operation_Type: 'DVP',
      Currency: 'EUR'
    };

    setAnalyzing(true);
    try {
      const result = await analyzeTrade(riskyTrade);
      const newRecord = {
        ...result,
        Trade_ID: `TRD-${Math.floor(Math.random() * 10000)}`,
        Asset_Class: 'Corp Bond',
        Counterparty: 'Risky Bank Intl',
      };

      // Add to top of list
      setTableData(prev => [newRecord, ...prev]);
      setSelectedTrade(newRecord);
    } catch (err) {
      console.error("Analysis Failed", err);
    } finally {
      setAnalyzing(false);
    }
  };

  const handleAutoCorrect = async () => {
    if (!selectedTrade) return;

    // Simulate fixing the SSI
    const fixedTrade: TradeRequest = {
      Notional_Amount_USD: 15000000,
      Market_Volatility_Index: 35.0,
      Asset_Class: 'Corp Bond',
      Counterparty_Rating: 'CCC',
      SSI_Status: 'Match', // FIX: Match
      Liquidity_Score: 'Low',
      Custodian_Location: 'EU',
      Operation_Type: 'DVP',
      Currency: 'EUR'
    };

    setAnalyzing(true);
    try {
      const result = await analyzeTrade(fixedTrade);
      const fixedRecord = {
        ...selectedTrade,
        ...result,
      };
      // Update in list
      setTableData(prev => prev.map(t => t.Trade_ID === selectedTrade.Trade_ID ? fixedRecord : t));
      setSelectedTrade(fixedRecord);
    } catch (err) {
      console.error("Fix Failed", err);
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-white p-6 font-sans">
      <header className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-emerald-400 tracking-tight">SettlementGuard <span className="text-slate-500 text-lg font-normal">v1.0</span></h1>
          <p className="text-slate-400">Intelligent Trade Failure Prediction</p>
        </div>
        <button
          onClick={simulateNewTrade}
          disabled={analyzing}
          className="bg-emerald-600 hover:bg-emerald-500 text-white px-6 py-2 rounded-lg font-semibold shadow-lg shadow-emerald-500/20 transition-all border border-emerald-500"
        >
          {analyzing ? 'Analyzing...' : '+ Ingest Trade Stream'}
        </button>
      </header>

      <main className="grid grid-cols-12 gap-6 h-[calc(100vh-140px)]">
        {/* Left Column: Feed */}
        <div className="col-span-12 lg:col-span-7 flex flex-col gap-6">
          <LiveFeedTable rowData={tableData} onRowClick={setSelectedTrade} />
        </div>

        {/* Right Column: Analytics */}
        <div className="col-span-12 lg:col-span-5 flex flex-col gap-6">
          {selectedTrade ? (
            <>
              <div className="grid grid-cols-2 gap-6">
                <RiskGauge probability={selectedTrade.failure_probability} riskLevel={selectedTrade.risk_level} />
                <ActionPanel onAutoCorrect={handleAutoCorrect} isProcessing={analyzing} />
              </div>
              <div className="flex-1">
                <ExplainabilityChart shapData={selectedTrade.shap_explanation} featureNames={[]} />
              </div>
            </>
          ) : (
            <div className="bg-slate-800 rounded-xl border border-slate-700 p-8 flex items-center justify-center h-full text-slate-500">
              Select a trade to view risk analysis
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
