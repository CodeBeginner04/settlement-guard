# SettlementGuard: AI-Powered Trade Failure Prediction

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Status](https://img.shields.io/badge/status-production-green.svg)

## The Business Problem
Trade settlement failures (T+1 issues) cost the financial industry billions annually in capital charges, operational friction, and CSDR penalties. Traditional rules-based engines fail to detect complex, non-linear risk patterns buried in transaction data.

## The Solution
**SettlementGuard** is a containerized microservices engine that predicts settlement risk at T-2 using Machine Learning (XGBoost). It provides:
1.  **Predictive Intelligence**: Flags trades with >80% failure probability.
2.  **Explainability (Glass Box)**: Uses SHAP values to tell Operations *why* a trade is risky (e.g., "Counterparty Rating CCC" + "SSI Mismatch").
3.  **Prescriptive Action**: Allows one-click simulation of fixes (e.g., Auto-Correct SSI) to see risk reduction in real-time.

---

## Architecture

The system follows a modern Microservices architecture:
-   **Frontend**: React.js + TypeScript + Tailwind + AG Grid (The "Cockpit").
-   **Backend**: Python FastAPI + Pydantic (High-performance API Gateway).
-   **Intelligence**: XGBoost + SMOTE + SHAP (Embedded Model).
-   **Infrastructure**: Docker Compose (Orchestration).

### Key Features
*   **Synthetic Data Foundry**: Generates realistic financial datasets with causal logic (Fat Finger errors, Liquidity crises).
*   **Imbalanced Learning**: Uses SMOTE to handle the 98/2 success/fail ratio inherent in financial data.
*   **Zero-Latency Inference**: Models are loaded into memory via FastAPI Lifespan events.

---

## Getting Started

### Prerequisites
- Docker & Docker Compose

### Installation
1.  Clone the repository:
    ```bash
    git clone https://github.com/yourname/settlement-guard.git
    cd settlement-guard
    ```

2.  Launch the System:
    ```bash
    docker-compose up --build
    ```

3.  Access the Dashboard:
    - Open [http://localhost:3000](http://localhost:3000)

### Usage Guide
1.  **Ingest Trade**: Click "+ Ingest Trade Stream" to simulate a live trade entering the system.
2.  **Analyze Risk**: Watch the Risk Gauge. If it turns **RED**, the trade is Critical.
3.  **Explain**: Look at the "Risk Drivers" chart to see which features contributed to the risk.
4.  **Act**: Click "Auto-Correct SSI" to simulate an operational fix and watch the risk drop.

---

## CI/CD Pipeline
Automated testing is configured via GitHub Actions.
-   **Triggers**: On Push to `main`.
-   **Steps**: Installs dependencies and runs `pytest` for API health checks.

## Technology Stack
-   **Language**: Python 3.10, TypeScript
-   **ML**: Scikit-Learn, XGBoost, SHAP, Imbalanced-Learn
-   **Web**: React, Vite, Tailwind CSS, Recharts
-   **API**: FastAPI, Uvicorn
-   **Ops**: Docker, GitHub Actions

---

**Developed for BNY Mellon Advanced Engineering Simulation**
