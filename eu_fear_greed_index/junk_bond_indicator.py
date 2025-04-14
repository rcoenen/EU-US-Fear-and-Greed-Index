import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Configuration
HIGH_YIELD_ETF = "IHYG.L" # iShares € High Yield Corp Bond UCITS ETF
INVESTMENT_GRADE_ETF = "IEAC.L" # iShares € Corp Bond UCITS ETF
PERIOD = "1mo" # Lookback period for comparison
LOOKBACK_DAYS = 20 # Lookback period (approx 1 month trading days)

def calculate_junk_bond_score(hy_ticker=HIGH_YIELD_ETF, ig_ticker=INVESTMENT_GRADE_ETF, lookback=LOOKBACK_DAYS):
    """Calculates the junk bond demand score comparing high-yield vs investment-grade.
    Score > 50 means HY outperforms (Greed), < 50 means IG outperforms (Fear).
    Raises ValueError if data is insufficient.
    Returns:
        score (float): A score between 0 and 100.
    """
    try:
        # Download data
        hy_bonds_raw = yf.download(hy_ticker, period=PERIOD, progress=False, auto_adjust=False)
        ig_bonds_raw = yf.download(ig_ticker, period=PERIOD, progress=False, auto_adjust=False)

        if hy_bonds_raw.empty or ig_bonds_raw.empty or 'Close' not in hy_bonds_raw or 'Close' not in ig_bonds_raw:
            print(f"Error: Could not download Close data for {hy_ticker} or {ig_ticker}.")
            return 0.0

        # Select 'Close' prices and rename
        hy_bonds = hy_bonds_raw[['Close']].rename(columns={'Close': 'HY'})
        ig_bonds = ig_bonds_raw[['Close']].rename(columns={'Close': 'IG'})

        # Align using merge on the Date index
        combined = pd.merge(hy_bonds, ig_bonds, left_index=True, right_index=True, how='inner')

        print("\n--- Debug: Junk Bond Indicator ---") # DEBUG
        print(f"Tickers: {hy_ticker} vs {ig_ticker}") # DEBUG
        print("Combined DataFrame `combined` head after merge:") # DEBUG
        print(combined.head()) # DEBUG
        print(f"Shape: {combined.shape}") # DEBUG
        print("-----------------------------------") # DEBUG

        if combined.empty or len(combined) < 2:
            print("Error: Not enough overlapping data points after alignment (merge).")
            return 0.0
            
        # Explicitly get scalar start/end values using .item()
        try:
            hy_start = combined['HY'].iloc[0].item()
            hy_end = combined['HY'].iloc[-1].item()
            ig_start = combined['IG'].iloc[0].item()
            ig_end = combined['IG'].iloc[-1].item()
        except IndexError:
             print("Error: Could not get start/end values from combined bond data (IndexError).")
             return 0.0
        except AttributeError:
             print("Warning: .item() failed, attempting direct access for bond start/end values.")
             hy_start = combined['HY'].iloc[0]
             hy_end = combined['HY'].iloc[-1]
             ig_start = combined['IG'].iloc[0]
             ig_end = combined['IG'].iloc[-1]

        # Check for non-numeric types
        if not all(isinstance(x, (int, float)) for x in [hy_start, hy_end, ig_start, ig_end]):
            print("Error: Non-numeric values found after extracting bond start/end prices.")
            return 0.0
        
        # Calculate percentage returns
        hy_return = (hy_end / hy_start - 1) * 100 if hy_start != 0 else 0
        ig_return = (ig_end / ig_start - 1) * 100 if ig_start != 0 else 0

        # Determine score (higher junk bond return suggests more risk appetite)
        score = (hy_return - ig_return) / 100 * 50 + 50
        
        return score

    except Exception as e:
        print(f"Error calculating junk bond score: {e}")
        return 0.0

# --- Main Execution (for standalone testing) ---
if __name__ == "__main__":
    score = calculate_junk_bond_score()
    
    print("--- Junk Bond Demand ---")
    print(f"Period: {PERIOD}")
    print(f"High Yield ETF ({HIGH_YIELD_ETF}) Return: {score:.2f}%")
    print(f"Inv Grade ETF ({INVESTMENT_GRADE_ETF}) Return: {score:.2f}%")
    print(f"Score: {score:.2f}%") 