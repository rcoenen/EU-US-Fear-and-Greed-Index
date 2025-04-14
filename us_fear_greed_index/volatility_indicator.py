import yfinance as yf
import pandas as pd
import numpy as np

# Configuration
VIX_TICKER = "^VIX"
DATA_PERIOD = "1y" # Lookback for historical context/MA
MA_DAYS = 50 # Moving average period
# Thresholds could also be used, e.g.:
# FEAR_THRESHOLD = 20
# GREED_THRESHOLD = 15 

def calculate_volatility_signal(ticker=VIX_TICKER, period=DATA_PERIOD, ma_days=MA_DAYS):
    """
    Calculates the volatility signal based on VIX data.
    Returns:
        signal (str): 'Fear' if VIX is high/rising, 'Greed' if low/falling.
        latest_vix (float): The latest VIX closing value.
    """
    try:
        # Fetch VIX data
        data = yf.download(ticker, period=period, progress=False, auto_adjust=False)
        if data.empty or 'Close' not in data.columns:
            print(f"Error: Could not download 'Close' data for {ticker}.")
            return "Neutral", None

        # Create a clean DataFrame
        df = data[['Close']].copy()
        
        # Calculate Moving Average
        df[f'{ma_days}d_ma'] = df['Close'].rolling(ma_days, min_periods=1).mean()

        # Use .item() to get scalar values
        try:
            latest_vix = df['Close'].iloc[-1].item()
            latest_ma = df[f'{ma_days}d_ma'].iloc[-1].item()
        except (IndexError, AttributeError, ValueError):
            print(f"Error: Could not extract scalar VIX/MA values for {ticker}.")
            # Try returning Neutral but still provide VIX if possible
            try: latest_vix_fallback = df['Close'].iloc[-1].item() 
            except: latest_vix_fallback = None
            return "Neutral", latest_vix_fallback
        
        if pd.isna(latest_vix) or pd.isna(latest_ma):
            print(f"Warning: Latest VIX or MA is NaN for {ticker}. Setting signal to Neutral.")
            return "Neutral", latest_vix # Return Neutral but still provide VIX if available
        
        # Signal logic: Compare VIX to its moving average
        # High VIX relative to recent average suggests Fear
        signal = "Fear" if latest_vix > latest_ma else "Greed"

        # Alternative threshold logic:
        # if latest_vix > FEAR_THRESHOLD:
        #     signal = "Fear"
        # elif latest_vix < GREED_THRESHOLD:
        #     signal = "Greed"
        # else:
        #     signal = "Neutral" 
        
        return signal, latest_vix

    except Exception as e:
        print(f"Error calculating volatility signal for {ticker}: {e}")
        return "Neutral", None

# --- Main Execution (for standalone testing) ---
if __name__ == "__main__":
    signal, vix_value = calculate_volatility_signal()
    
    print("--- US Market Volatility (VIX) ---")
    if vix_value is not None:
        print(f"Latest VIX: {vix_value:.2f}")
        print(f"Signal: {signal}")
    else:
        print("Could not retrieve VIX data.") 