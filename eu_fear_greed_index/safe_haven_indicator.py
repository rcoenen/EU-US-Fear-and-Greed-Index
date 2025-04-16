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
    Uses sigmoid scaling for smoother handling of extreme values.
    
    Returns:
        score (float): A score between 5 and 95.
    Raises:
        ValueError: If data is insufficient.
    """
    try:
        # Download data
        stocks_raw = yf.download(stock_ticker, period=f"{lookback}d", progress=False, auto_adjust=False)
        bonds_raw = yf.download(bond_ticker, period=f"{lookback}d", progress=False, auto_adjust=False)

        if stocks_raw.empty or bonds_raw.empty or 'Close' not in stocks_raw or 'Close' not in bonds_raw:
            print(f"Error: Could not download Close data for {stock_ticker} or {bond_ticker}.")
            raise ValueError("Failed to download stock or bond data")

        # Select 'Close' prices and rename columns
        stocks = stocks_raw[['Close']].rename(columns={'Close': 'Stock'})
        bonds = bonds_raw[['Close']].rename(columns={'Close': 'Bond'})
        
        # Align using merge on the Date index
        combined = pd.merge(stocks, bonds, left_index=True, right_index=True, how='inner')
        
        print("\n--- Debug: Safe Haven Indicator ---")
        print(f"Tickers: {stock_ticker} vs {bond_ticker}")
        print("Combined DataFrame `combined` head after merge:")
        print(combined.head())
        print(f"Shape: {combined.shape}")
        print("-----------------------------------")

        if combined.empty or len(combined) < 2:
            raise ValueError("Not enough overlapping data points after alignment")
            
        # Explicitly get scalar start/end values using .item()
        try:
            stock_start = combined['Stock'].iloc[0].item()
            stock_end = combined['Stock'].iloc[-1].item()
            bond_start = combined['Bond'].iloc[0].item()
            bond_end = combined['Bond'].iloc[-1].item()
        except (IndexError, AttributeError):
            # Fallback if .item() fails
            stock_start = float(combined['Stock'].iloc[0])
            stock_end = float(combined['Stock'].iloc[-1])
            bond_start = float(combined['Bond'].iloc[0])
            bond_end = float(combined['Bond'].iloc[-1])

        # Check for non-numeric types
        if not all(isinstance(x, (int, float)) for x in [stock_start, stock_end, bond_start, bond_end]):
            raise ValueError("Non-numeric values found in price data")

        # Calculate percentage returns
        stock_return = (stock_end / stock_start - 1) * 100 if stock_start != 0 else 0
        bond_return = (bond_end / bond_start - 1) * 100 if bond_start != 0 else 0

        # Calculate score using sigmoid scaling for smoother handling of extreme values
        max_diff_scale = 5.0  # 5% difference for scaling (same as US)
        difference = stock_return - bond_return
        
        # Sigmoid transformation
        normalized_diff = difference / max_diff_scale
        sigmoid = 1 / (1 + np.exp(-normalized_diff))
        score = sigmoid * 100
        
        # Ensure score stays within reasonable bounds (5-95)
        score = max(5, min(95, score))

        print(f"Safe Haven: Stock Ret={stock_return:.2f}%, Bond Ret={bond_return:.2f}%, Diff={difference:.2f}%, Score={score:.2f}")
        return score

    except Exception as e:
        print(f"Error calculating safe haven score: {e}")
        raise ValueError(f"Error calculating EU safe haven score: {str(e)}")

# --- Main Execution (for standalone testing) ---
if __name__ == "__main__":
    score = calculate_safe_haven_score()
    
    print("--- Safe Haven Demand ---")
    print(f"Lookback period: {LOOKBACK_DAYS} days")
    print(f"Score: {score:.2f}") 