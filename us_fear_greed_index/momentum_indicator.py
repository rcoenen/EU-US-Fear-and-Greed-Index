import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from utils.safe_yf import safe_yf_download
import yfinance as yf

# Configuration
STOCK_INDEX = "^GSPC" # S&P 500
MOVING_AVG_DAYS = 90  # Reduced from 125 to 90 days for more responsiveness
DATA_PERIOD = "1y"
VOLATILITY_WINDOW = 30  # Days for volatility calculation

def calculate_momentum_score():
    """Calculate momentum score based on S&P 500 price and volatility."""
    try:
        # Fetch S&P 500 data (1 year to ensure enough history for 125-day MA)
        data = yf.download("^GSPC", period="1y", interval="1d")['Close']
        
        if len(data) < 125:
            raise ValueError("Insufficient data for 125-day moving average")
        
        # Calculate 125-day moving average
        ma = data.rolling(window=125).mean()
        
        # Calculate volatility (standard deviation of returns)
        returns = data.pct_change()
        volatility = returns.rolling(window=20).std() * np.sqrt(252)  # Annualize
        
        # Get latest values
        latest_close = float(data.iloc[-1].iloc[0])
        latest_ma = float(ma.iloc[-1].iloc[0])
        latest_vol = float(volatility.iloc[-1].iloc[0])
        
        # Calculate percentage difference from MA
        pct_diff = (latest_close - latest_ma) / latest_ma * 100
        
        # Calculate score based on difference from MA and volatility
        base_score = 50 + (pct_diff * 2)  # Each 1% difference moves score by 2 points
        
        # Adjust for volatility (higher volatility reduces the score)
        vol_adjustment = latest_vol * 50  # Scale volatility to 0-50 range
        final_score = base_score - vol_adjustment
        
        # Ensure score is within bounds and convert to float
        final_score = float(np.clip(final_score, 0, 100))
        
        print(f"Momentum (^GSPC): Close={latest_close:.2f}, MA={latest_ma:.2f}, Vol={latest_vol:.2%}, Score={final_score:.2f}")
        
        return final_score
        
    except Exception as e:
        print(f"Error calculating momentum score: {str(e)}")
        raise ValueError("Sorry, cannot calculate data at this time. Please try again in a few minutes.")

# --- Main Execution (for standalone testing & plotting) ---
if __name__ == "__main__":
    score = calculate_momentum_score()
    
    print("--- US Momentum Score Test ---")
    print(f"Calculated Score: {score:.2f}") 