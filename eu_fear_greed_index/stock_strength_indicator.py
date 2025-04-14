import yfinance as yf
import pandas as pd
import numpy as np

# Configuration
# Sample of large-cap European stocks (STOXX Europe 600 components)
# Ideally, fetch the full list or a larger, more representative sample
SAMPLE_TICKERS = [
    "NESN.SW", "ASML.AS", "MC.PA", "ROG.SW", "OR.PA", "LIN.DE", 
    "SAP.DE", "SIE.DE", "AIR.PA", "TTE.PA", "IDEXY", "SAN.PA", 
    "DTE.DE", "CS.PA", "BAYN.DE", "MDT", "EL.PA", # Replaced AXA.PA with CS.PA
    "PHIA.AS", "BNP.PA", "ADS.DE" # Added Adidas to make it 20
] 
LOOKBACK_PERIOD = "1y" # For 52-week high/low
HIGH_LOW_THRESHOLD = 0.05 # Within 5% of 52-week high/low

def calculate_strength_score(tickers=SAMPLE_TICKERS, period=LOOKBACK_PERIOD, threshold=HIGH_LOW_THRESHOLD):
    """
    Calculates stock price strength score (0-100) based on 52-week highs vs lows.
    Score > 50 means more highs (Greed), < 50 means more lows (Fear).
    Raises ValueError if data cannot be fetched or calculated.
    Returns:
        score (float): A score between 0 and 100.
    """
    print(f"Fetching {len(tickers)} tickers for stock strength...")
    try:
        data = yf.download(tickers, period=period, progress=False, group_by='ticker')
    except Exception as e:
        raise ValueError(f"Failed to download yfinance data for strength tickers: {e}")
        
    high_count = 0
    low_count = 0
    valid_tickers = 0

    for ticker in tickers:
        if ticker not in data or data[ticker].empty or 'Close' not in data[ticker]:
            # print(f"Warning: No or incomplete data for {ticker} in strength calc.")
            continue
        
        ticker_series = data[ticker]['Close'].dropna()
        if len(ticker_series) < 200: # Ensure enough data for a 52-week period approx
            # print(f"Skipping {ticker}: Insufficient data points ({len(ticker_series)}) for strength calc.")
            continue 
            
        valid_tickers += 1
        try:
            current_price = float(ticker_series.iloc[-1])
            high_52w = float(ticker_series.max())
            low_52w = float(ticker_series.min())
        except (IndexError, ValueError, TypeError) as e:
             print(f"Warning: Could not extract price points for {ticker}: {e}")
             continue # Skip this ticker

        # Check if near high
        if high_52w > 0 and current_price >= high_52w * (1 - threshold):
            high_count += 1
        
        # Check if near low
        if low_52w > 0 and current_price <= low_52w * (1 + threshold):
            low_count += 1
    
    if valid_tickers == 0:
        raise ValueError("No tickers had sufficient data for strength analysis.")

    print(f"Strength: Analyzed {valid_tickers} tickers. Highs: {high_count}, Lows: {low_count}")
    
    # Calculate score based on ratio
    total_relevant = high_count + low_count
    if total_relevant == 0:
        score = 50.0 # Neutral if no stocks are near high or low
    else:
        # Ratio = (Highs - Lows) / (Highs + Lows), ranges from -1 to 1
        ratio = (high_count - low_count) / total_relevant
        # Scale ratio to 0-100 (where -1 maps to 0, 0 maps to 50, 1 maps to 100)
        score = 50 + (ratio * 50)
        
    score = np.clip(score, 0, 100)
    print(f"Strength Score: {score:.2f}")
    return score

# --- Main Execution (for standalone testing) ---
if __name__ == "__main__":
    score = calculate_strength_score()
    
    print("--- Stock Price Strength (Sample) ---")
    print(f"Calculated Score: {score:.2f}") 