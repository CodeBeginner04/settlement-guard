import React, { useMemo } from 'react';
import { AgGridReact } from 'ag-grid-react';
import { ModuleRegistry, AllCommunityModule } from 'ag-grid-community';
import type { ColDef } from 'ag-grid-community';
import type { PredictionResponse } from '../../services/api';

// Register all community modules
ModuleRegistry.registerModules([AllCommunityModule]);

interface TradeRow extends PredictionResponse {
    Trade_ID: string;
    Asset_Class: string;
    Counterparty: string;
}

interface LiveFeedTableProps {
    rowData: TradeRow[];
    onRowClick: (data: TradeRow) => void;
}

const LiveFeedTable: React.FC<LiveFeedTableProps> = ({ rowData, onRowClick }) => {
    const columnDefs: ColDef<TradeRow>[] = useMemo(() => [
        { field: 'Trade_ID', headerName: 'Trade ID', width: 120 },
        { field: 'Asset_Class', headerName: 'Asset', width: 100 },
        { field: 'Counterparty', headerName: 'Counterparty', flex: 1 },
        {
            field: 'failure_probability',
            headerName: 'Prob',
            width: 90,
            valueFormatter: (p: any) => `${(p.value * 100).toFixed(1)}%`,
            cellStyle: (params: any) => {
                if (params.value > 0.8) return { color: '#ef4444', fontWeight: 'bold' };
                if (params.value > 0.5) return { color: '#f97316', fontWeight: 'normal' };
                return { color: '#10b981', fontWeight: 'normal' };
            }
        },
        {
            field: 'risk_level',
            headerName: 'Risk',
            width: 100,
            cellRenderer: (params: any) => (
                <span className={`px-2 py-1 rounded text-xs font-bold ${params.value === 'CRITICAL' ? 'bg-red-500/20 text-red-500' :
                    params.value === 'HIGH' ? 'bg-orange-500/20 text-orange-500' :
                        'bg-emerald-500/20 text-emerald-500'
                    }`}>
                    {params.value}
                </span>
            )
        }
    ], []);

    const defaultColDef = useMemo(() => ({
        sortable: true,
        filter: true,
        resizable: true,
    }), []);

    const getRowStyle = (params: any) => {
        if (params.data && params.data.failure_probability > 0.8) {
            return { background: 'rgba(239, 68, 68, 0.1)' };
        }
        return undefined;
    }

    return (
        <div className="ag-theme-quartz-dark h-full w-full rounded-xl overflow-hidden shadow-lg border border-slate-700">
            <AgGridReact
                rowData={rowData}
                columnDefs={columnDefs}
                defaultColDef={defaultColDef}
                rowSelection="single"
                onRowClicked={(e) => {
                    if (e.data) onRowClick(e.data);
                }}
                getRowStyle={getRowStyle}
            />
        </div>
    );
};

export default LiveFeedTable;
