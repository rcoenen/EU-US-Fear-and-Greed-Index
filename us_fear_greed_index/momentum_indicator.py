import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Configuration
STOCK_INDEX = "^GSPC" # S&P 500
MOVING_AVG_DAYS = 125
DATA_PERIOD = "1y"

def calculate_momentum_score(ticker=STOCK_INDEX, period=DATA_PERIOD, ma_days=MOVING_AVG_DAYS):
    """
    Calculates the market momentum score (0-100) for the S&P 500.
    Score < 50 indicates price below MA (Fear), > 50 indicates price above MA (Greed).
    Raises ValueError if data cannot be fetched or calculated.
    Returns:
        score (float): A score between 0 and 100.
    """
    # Fetch Data
    try:
        data = yf.download(ticker, period=period, progress=False, auto_adjust=False)['Close']
    except Exception as e:
        raise ValueError(f"Failed to download yfinance data for {ticker}: {e}")
    if data.empty:
        raise ValueError(f"No historical data found for {ticker}.")
         
    # Calculate Moving Average
    ma = data.rolling(ma_days, min_periods=ma_days // 2).mean().dropna()
    if ma.empty:
        raise ValueError(f"Could not calculate {ma_days}-day MA for {ticker} (insufficient data).")

    # Get latest values
    try:
        latest_close = float(data.iloc[-1])
        latest_ma = float(ma.iloc[-1])
    except (IndexError, ValueError, TypeError) as e:
        raise ValueError(f"Could not extract latest close/MA values for {ticker}: {e}")

    # Calculate score based on deviation
    if latest_ma <= 0:
        print(f"Warning: Invalid moving average ({latest_ma:.2f}) for {ticker}. Returning neutral score.")
        return 50.0

    deviation = (latest_close - latest_ma) / latest_ma
    max_dev_scale = 0.10 # 10% deviation = full Fear/Greed
    score = 50 + (deviation / max_dev_scale) * 50
    score = np.clip(score, 0, 100)

    print(f"Momentum ({ticker}): Close={latest_close:.2f}, MA={latest_ma:.2f}, Score={score:.2f}")
    return score

# --- Main Execution (for standalone testing & plotting) ---
if __name__ == "__main__":
    score = calculate_momentum_score()
    
    print("--- US Momentum Score Test ---")
    print(f"Calculated Score: {score:.2f}") 