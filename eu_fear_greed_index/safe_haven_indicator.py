import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Configuration
STOCK_TICKER = "^STOXX50E" # Euro Stoxx 50
BOND_TICKER = "EXHB.DE"  # iShares Euro Government Bond 7-10yr UCITS ETF (Acc)
LOOKBACK_DAYS = 20 # Lookback period (approx 1 month trading days)

def calculate_safe_haven_score(stock_ticker=STOCK_TICKER, bond_ticker=BOND_TICKER, lookback=LOOKBACK_DAYS):
    """Calculates the safe haven demand score based on stock vs bond performance.
    Score > 50 means stocks outperform (Greed), < 50 means bonds outperform (Fear).
    Raises ValueError if data is insufficient.
    Returns:
        score (float): A score between 0 and 100.
    """
    try:
        # Download data
        stocks_raw = yf.download(stock_ticker, period=f"{lookback}d", progress=False, auto_adjust=False)
        bonds_raw = yf.download(bond_ticker, period=f"{lookback}d", progress=False, auto_adjust=False)

        if stocks_raw.empty or bonds_raw.empty or 'Close' not in stocks_raw or 'Close' not in bonds_raw:
            print(f"Error: Could not download Close data for {stock_ticker} or {bond_ticker}.")
            return 0.0

        # Select 'Close' prices and rename columns
        stocks = stocks_raw[['Close']].rename(columns={'Close': 'Stock'})
        bonds = bonds_raw[['Close']].rename(columns={'Close': 'Bond'})
        
        # Align using merge on the Date index
        combined = pd.merge(stocks, bonds, left_index=True, right_index=True, how='inner') # Inner merge ensures dates exist in both
        
        print("\n--- Debug: Safe Haven Indicator ---") # DEBUG
        print(f"Tickers: {stock_ticker} vs {bond_ticker}") # DEBUG
        print("Combined DataFrame `combined` head after merge:") # DEBUG
        print(combined.head()) # DEBUG
        print(f"Shape: {combined.shape}") # DEBUG
        print("-----------------------------------") # DEBUG

        if combined.empty or len(combined) < 2:
            print("Error: Not enough overlapping data points after alignment (merge).")
            return 0.0
            
        # Explicitly get scalar start/end values using .item()
        try:
            stock_start = combined['Stock'].iloc[0].item()
            stock_end = combined['Stock'].iloc[-1].item()
            bond_start = combined['Bond'].iloc[0].item()
            bond_end = combined['Bond'].iloc[-1].item()
        except IndexError:
             print("Error: Could not get start/end values from combined data (IndexError).")
             return 0.0
        except AttributeError:
             # Fallback if .item() fails (data might already be scalar?)
             print("Warning: .item() failed, attempting direct access for start/end values.")
             stock_start = combined['Stock'].iloc[0]
             stock_end = combined['Stock'].iloc[-1]
             bond_start = combined['Bond'].iloc[0]
             bond_end = combined['Bond'].iloc[-1]

        # Check for non-numeric types just in case
        if not all(isinstance(x, (int, float)) for x in [stock_start, stock_end, bond_start, bond_end]):
            print("Error: Non-numeric values found after extracting start/end prices.")
            return 0.0

        # Calculate percentage returns over the aligned period
        stock_return = (stock_end / stock_start - 1) * 100 if stock_start != 0 else 0
        bond_return = (bond_end / bond_start - 1) * 100 if bond_start != 0 else 0

        # Calculate score
        score = (stock_return - bond_return) / 100 * 50 + 50
        
        return score

    except Exception as e:
        print(f"Error calculating safe haven score: {e}")
        return 0.0

# --- Main Execution (for standalone testing) ---
if __name__ == "__main__":
    score = calculate_safe_haven_score()
    
    print("--- Safe Haven Demand ---")
    print(f"Lookback period: {LOOKBACK_DAYS} days")
    print(f"Score: {score:.2f}") 