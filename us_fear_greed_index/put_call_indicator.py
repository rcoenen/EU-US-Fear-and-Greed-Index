import yfinance as yf
import pandas as pd
import numpy as np

# Configuration
VIX_TICKER = "^VIX"
DATA_PERIOD = "5d" # Only need recent data to get the latest value

# Thresholds for VIX as a proxy for Put/Call sentiment
# High VIX implies fear (high demand for puts relative to calls)
# Low VIX implies complacency/greed (low demand for puts relative to calls)
FEAR_THRESHOLD = 20 
GREED_THRESHOLD = 15 

def calculate_put_call_proxy_signal(ticker=VIX_TICKER, period=DATA_PERIOD):
    """
    Calculates a sentiment signal based on the absolute level of VIX,
    acting as a proxy for Put/Call ratio extremes.
    Returns:
        signal (str): 'Fear', 'Greed', or 'Neutral' based on VIX thresholds.
        latest_vix (float): The latest VIX closing value.
    """
    try:
        # Fetch recent VIX data
        data = yf.download(ticker, period=period, progress=False, auto_adjust=False)
        if data.empty or 'Close' not in data.columns:
            print(f"Error: Could not download 'Close' data for {ticker} (Put/Call Proxy).")
            return "Neutral", None

        # Use .item() to get scalar value
        try:
            latest_vix = data['Close'].iloc[-1].item()
        except (IndexError, AttributeError, ValueError):
            print(f"Error: Could not extract scalar VIX value for {ticker} (Put/Call Proxy).")
            return "Neutral", None
        
        if pd.isna(latest_vix):
            print(f"Warning: Latest VIX is NaN for {ticker}. Setting Put/Call Proxy signal to Neutral.")
            return "Neutral", None
        
        # Signal logic based on absolute VIX level thresholds
        if latest_vix > FEAR_THRESHOLD:
            signal = "Fear"
        elif latest_vix < GREED_THRESHOLD:
            signal = "Greed"
        else:
            signal = "Neutral" 
        
        return signal, latest_vix

    except Exception as e:
        print(f"Error calculating Put/Call Proxy signal for {ticker}: {e}")
        return "Neutral", None

# --- Main Execution (for standalone testing) ---
if __name__ == "__main__":
    signal, vix_value = calculate_put_call_proxy_signal()
    
    print("--- US Put/Call Proxy (using VIX Level) ---")
    if vix_value is not None:
        print(f"Latest VIX: {vix_value:.2f}")
        print(f"Fear Threshold: > {FEAR_THRESHOLD}")
        print(f"Greed Threshold: < {GREED_THRESHOLD}")
        print(f"Signal: {signal}")
    else:
        print("Could not retrieve VIX data.") 