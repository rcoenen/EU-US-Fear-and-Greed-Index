import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from utils.safe_yf import safe_yf_download

# Configuration
STOCK_INDEX = "^GSPC" # S&P 500
MOVING_AVG_DAYS = 90  # Reduced from 125 to 90 days for more responsiveness
DATA_PERIOD = "1y"
VOLATILITY_WINDOW = 30  # Days for volatility calculation

def calculate_momentum_score(ticker=STOCK_INDEX, period=DATA_PERIOD, ma_days=MOVING_AVG_DAYS):
    """
    Calculates the market momentum score (0-100) for the S&P 500.
    Score < 50 indicates price below MA (Fear), > 50 indicates price above MA (Greed).
    Includes volatility adjustment to account for different market characteristics.
    Raises ValueError if data cannot be fetched or calculated.
    Returns:
        score (float): A score between 0 and 100.
    """
    # Fetch Data using safe_yf
    try:
        data = safe_yf_download(ticker, period=period, auto_adjust=False)['Close']
    except Exception as e:
        raise ValueError(f"Failed to download yfinance data for {ticker}: {e}")
    if data.empty:
        raise ValueError(f"No historical data found for {ticker}.")
         
    # Calculate Moving Average
    ma = data.rolling(ma_days, min_periods=ma_days // 2).mean().dropna()
    if ma.empty:
        raise ValueError(f"Could not calculate {ma_days}-day MA for {ticker} (insufficient data).")

    # Calculate Volatility
    returns = data.pct_change().dropna()
    volatility = returns.rolling(window=VOLATILITY_WINDOW).std().dropna()
    if volatility.empty:
        raise ValueError(f"Could not calculate volatility for {ticker}.")

    # Get latest values
    try:
        latest_close = float(data.iloc[-1].iloc[0])  # Use .iloc[0] to get scalar value
        latest_ma = float(ma.iloc[-1].iloc[0])  # Use .iloc[0] to get scalar value
        latest_vol = float(volatility.iloc[-1].iloc[0])  # Use .iloc[0] to get scalar value
    except (IndexError, ValueError, TypeError) as e:
        raise ValueError(f"Could not extract latest values for {ticker}: {e}")

    # Calculate score based on deviation
    if latest_ma <= 0:
        print(f"Warning: Invalid moving average ({latest_ma:.2f}) for {ticker}. Returning neutral score.")
        return 50.0

    # Calculate raw deviation
    deviation = (latest_close - latest_ma) / latest_ma
    
    # Adjust for volatility - more aggressive fear detection
    # Higher volatility means we need a larger deviation to indicate the same level of momentum
    vol_adjustment = 1.0 / (1.0 + latest_vol * 1.5)  # Increased volatility impact by 50%
    
    # Scale deviation to 0-100 with volatility adjustment
    max_dev_scale = 0.08  # Reduced from 0.10 to 0.08 for more sensitive fear detection
    score = 50 + (deviation / (max_dev_scale * vol_adjustment)) * 50
    
    # Add extra fear bias for negative momentum
    if deviation < 0:
        score = score * 0.9  # Reduce score by 10% for negative momentum
    
    score = np.clip(score, 0, 100)  # Clamp between 0 and 100

    print(f"Momentum ({ticker}): Close={latest_close:.2f}, MA={latest_ma:.2f}, Vol={latest_vol:.2%}, Score={score:.2f}")
    return score

# --- Main Execution (for standalone testing & plotting) ---
if __name__ == "__main__":
    score = calculate_momentum_score()
    
    print("--- US Momentum Score Test ---")
    print(f"Calculated Score: {score:.2f}") 