import pandas as pd

df = pd.read_csv("settlement_data.csv")
print(f"Total Rows: {len(df)}")
print(f"Failure Rate: {df['IS_FAILED'].mean():.4f}")

# Check Rules
print("\n--- Rule Verification ---")

# 1. SSI Mismatch
mismatch_fail = df[df['SSI_Status'] == 'Mismatch']['IS_FAILED'].mean()
print(f"SSI Mismatch Failure Rate (Target ~95%): {mismatch_fail:.2%}")

# 2. Junk Bond (CCC + Corp Bond)
junk_bond = df[(df['Counterparty_Rating'] == 'CCC') & (df['Asset_Class'] == 'Corp Bond')]
junk_fail = junk_bond['IS_FAILED'].mean()
print(f"Junk Bond Failure Rate (Target > 30%): {junk_fail:.2%}")

# 3. Whale Rule
whale = df[(df['Notional_Amount_USD'] > 100_000_000) & (df['Liquidity_Score'] == 'Low')]
whale_fail = whale['IS_FAILED'].mean()
print(f"Whale Trade Failure Rate: {whale_fail:.2%}")

