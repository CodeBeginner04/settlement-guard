import axios from 'axios';

// Use localhost:8000 for local dev
const API_URL = 'http://localhost:8000';

const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export interface TradeRequest {
    Notional_Amount_USD: number;
    Market_Volatility_Index: number;
    Asset_Class: string;
    Counterparty_Rating: string;
    SSI_Status: string;
    Liquidity_Score: string;
    Custodian_Location?: string;
    Operation_Type?: string;
    Currency?: string;
    Trade_Day?: string;
    Trade_Hour?: number;
}

export interface PredictionResponse {
    failure_probability: number;
    risk_level: string;
    shap_explanation: {
        base_value: number;
        feature_contributions: number[];
    };
}

export const analyzeTrade = async (trade: TradeRequest): Promise<PredictionResponse> => {
    const response = await api.post<PredictionResponse>('/predict', trade);
    return response.data;
};

export default api;
