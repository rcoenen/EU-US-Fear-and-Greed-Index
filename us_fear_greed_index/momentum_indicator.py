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
    try:
        # Fetch Data using safe_yf
        data = safe_yf_download(ticker, period=period, auto_adjust=False)['Close']
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
        latest_close = float(data.iloc[-1])
        latest_ma = float(ma.iloc[-1])
        latest_vol = float(volatility.iloc[-1])

        # Calculate score
        score = 50 + ((latest_close - latest_ma) / latest_ma) * 50
        score = max(0, min(100, score))  # Ensure score is within 0-100

        return score
    except Exception as e:
        print(f"Error calculating momentum score: {str(e)}")
        raise ValueError("Sorry, cannot calculate data at this time. Please try again in a few minutes.")

# --- Main Execution (for standalone testing & plotting) ---
if __name__ == "__main__":
    score = calculate_momentum_score()
    
    print("--- US Momentum Score Test ---")
    print(f"Calculated Score: {score:.2f}") 