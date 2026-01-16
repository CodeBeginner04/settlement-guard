import pandas as pd
import numpy as np
import random
from faker import Faker
from datetime import datetime, timedelta

# Initialize Faker
fake = Faker()
Faker.seed(42)
np.random.seed(42)

def generate_market_data(num_rows=100000):
    """
    Generates a synthetic dataset of trades with probabilistic failure logic.
    """
    print(f"Generating {num_rows} trades...")
    
    # 1. Setup Distributions (The "Physics" of the market)
    asset_classes = ['Equity', 'Gov Bond', 'Corp Bond', 'FX', 'Derivatives']
    ratings = ['AAA', 'AA', 'A', 'BBB', 'BB', 'CCC']
    currencies = ['USD', 'EUR', 'GBP', 'JPY', 'CAD']
    locations = ['US', 'EU', 'APAC']
    ssi_statuses = ['Match', 'Mismatch']
    liquidity_scores = ['High', 'Medium', 'Low']
    operation_types = ['DVP', 'FOP'] # Delivery vs Payment, Free of Payment

    # 2. Generate Base Features
    # Vectorized generation for speed
    
    # Dates: Random dates within last year
    start_date = datetime(2025, 1, 1)
    date_range = [start_date + timedelta(days=np.random.randint(0, 365)) for _ in range(num_rows)]
    trade_dates = [d.strftime("%Y-%m-%d %H:%M:%S") for d in date_range]
    days_of_week = [d.strftime("%A") for d in date_range]
    hours = [d.hour for d in date_range]

    data = {
        'Trade_ID': [fake.uuid4() for _ in range(num_rows)],
        'Trade_Date': trade_dates,
        # T+2 Settlement (Simplified, ignoring weekends for logic for now)
        'Settlement_Date': [(d + timedelta(days=2)).strftime("%Y-%m-%d") for d in date_range], 
        'Trade_Day': days_of_week, # Helper for logic
        'Trade_Hour': hours,       # Helper for logic
        'Asset_Class': np.random.choice(asset_classes, num_rows, p=[0.5, 0.2, 0.15, 0.1, 0.05]),
        'Counterparty': [fake.company() for _ in range(num_rows)],
        'Counterparty_ID': [fake.uuid4() for _ in range(num_rows)],
        'Counterparty_Rating': np.random.choice(ratings, num_rows, p=[0.15, 0.25, 0.3, 0.2, 0.08, 0.02]), # Skewed better
        'Custodian_Location': np.random.choice(locations, num_rows, p=[0.5, 0.3, 0.2]),
        'SSI_Status': np.random.choice(ssi_statuses, num_rows, p=[0.98, 0.02]), # 2% mismatch (Fatal)
        'Liquidity_Score': np.random.choice(liquidity_scores, num_rows, p=[0.6, 0.3, 0.1]),
        'Market_Volatility_Index': np.random.normal(15, 5, num_rows).round(2), # VIX, mean 15
        'Operation_Type': np.random.choice(operation_types, num_rows, p=[0.9, 0.1]),
        'Currency': np.random.choice(currencies, num_rows, p=[0.6, 0.2, 0.1, 0.05, 0.05]),
        # Log-normal distribution for amounts to simulate "fat tails" (occasional massive trades)
        'Notional_Amount_USD': np.random.lognormal(mean=14, sigma=1.5, size=num_rows).round(2) 
    }
    
    # Generate ISINs (Mock)
    data['ISIN'] = [fake.bothify(text='??##########') for _ in range(num_rows)]
    
    df = pd.DataFrame(data)
    
    # 3. Apply The "Causal Logic" (The Intelligence)
    print("Applying applying causal logic...")

    def calculate_failure_prob(row):
        prob = 0.01 # Base failure rate (1% random operational noise)
        
        # Rule 1: The "Fat Finger" Rule (SSI Mismatch)
        # If SSI is wrong, it almost certainly fails.
        if row['SSI_Status'] == 'Mismatch':
            prob += 0.90
            
        # Rule 2: The "Junk Bond" Rule (Credit Risk)
        # Risky Counterparty + Risky Asset = High Trouble
        if row['Counterparty_Rating'] == 'CCC' and row['Asset_Class'] == 'Corp Bond':
            prob += 0.30
        elif row['Counterparty_Rating'] == 'BB' and row['Asset_Class'] == 'Corp Bond': 
            prob += 0.15

        # Rule 3: The "Friday Afternoon" Rule (Operational Friction)
        # Friday after 4 PM local time (assuming UTC/simulated), non-USD trades are hard to clear.
        if row['Trade_Day'] == 'Friday' and row['Trade_Hour'] >= 16 and row['Currency'] != 'USD':
            prob += 0.15
            
        # Rule 4: The "Whale" Rule (Liquidity)
        # Huge trades (>100M) in illiquid assets.
        if row['Notional_Amount_USD'] > 100_000_000 and row['Liquidity_Score'] == 'Low':
            prob += 0.25
            
        # Rule 5: Volatility Shock
        # If VIX is super high (>30), general failure rate increases
        if row['Market_Volatility_Index'] > 30:
            prob += 0.05

        return min(prob, 1.0)

    # Apply logic row by row
    df['Failure_Prob'] = df.apply(calculate_failure_prob, axis=1)
    
    # 4. Generate Target Variable
    # Flip the weighted coin
    df['IS_FAILED'] = df.apply(lambda row: np.random.choice([1, 0], p=[row['Failure_Prob'], 1-row['Failure_Prob']]), axis=1)
    
    # Cleanup helper columns if needed, but keeping them for now is fine for EDA
    # Remove large objects if saving space is priority, but 100k is small.
    
    fail_count = df['IS_FAILED'].sum()
    print(f"Dataset Generated. Total: {num_rows}, Failures: {fail_count} ({fail_count/num_rows:.2%})")
    
    return df

if __name__ == "__main__":
    df = generate_market_data(100000)
    df.to_csv("settlement_data.csv", index=False)
    print("Saved to settlement_data.csv")
