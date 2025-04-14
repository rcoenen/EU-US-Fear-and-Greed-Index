import yfinance as yf
import pandas as pd

# Configuration
# Sample of large-cap European stocks (STOXX Europe 600 components)
# Ideally, fetch the full list or a larger, more representative sample
SAMPLE_TICKERS = [
    "NESN.SW", "ASML.AS", "MC.PA", "ROG.SW", "OR.PA", "LIN.DE", 
    "SAP.DE", "SIE.DE", "AIR.PA", "TTE.PA", "IDEXY", "SAN.PA", 
    "DTE.DE", "AXA.PA", "BAYN.DE", "MDT", "EL.PA", "CS.PA", # Added a few more
    "PHIA.AS", "BNP.PA" 
] 
LOOKBACK_PERIOD = "1y" # For 52-week high/low
HIGH_LOW_THRESHOLD = 0.05 # Within 5% of 52-week high/low

def calculate_stock_strength_signal(tickers=SAMPLE_TICKERS, period=LOOKBACK_PERIOD, threshold=HIGH_LOW_THRESHOLD):
    """
    Calculates stock price strength based on 52-week highs vs lows for a sample.
    Returns:
        signal (str): 'Greed' if more highs, 'Fear' if more lows.
        high_count (int): Number of stocks near 52w high.
        low_count (int): Number of stocks near 52w low.
    """
    try:
        print(f"Fetching {len(tickers)} tickers for stock strength...")
        data = yf.download(tickers, period=period, progress=False)
        
        if data.empty or 'Close' not in data:
            print("Error: Could not download sufficient stock data.")
            return "Neutral", 0, 0

        close_prices = data['Close']
        if close_prices.empty:
             print("Error: Closing price data is empty.")
             return "Neutral", 0, 0

        high_count = 0
        low_count = 0
        valid_tickers = 0

        # Iterate through each ticker column
        for ticker in close_prices.columns:
            ticker_series = close_prices[ticker].dropna()
            if len(ticker_series) < 200: # Ensure enough data for a 52-week period
                # print(f"Skipping {ticker}: Insufficient data ({len(ticker_series)} points)")
                continue 
                
            valid_tickers += 1
            current_price = ticker_series.iloc[-1]
            high_52w = ticker_series.max()
            low_52w = ticker_series.min()

            # Check if near high
            if current_price >= high_52w * (1 - threshold):
                high_count += 1
            
            # Check if near low
            if current_price <= low_52w * (1 + threshold):
                low_count += 1
        
        if valid_tickers == 0:
            print("Error: No tickers had sufficient data for analysis.")
            return "Neutral", 0, 0

        print(f"Analyzed {valid_tickers} tickers.")
        # Determine signal
        if high_count > low_count:
            signal = "Greed"
        elif low_count > high_count:
            signal = "Fear"
        else:
            signal = "Neutral"
            
        return signal, high_count, low_count

    except Exception as e:
        print(f"Error calculating stock strength signal: {e}")
        # print traceback
        import traceback
        traceback.print_exc()
        return "Neutral", 0, 0

# --- Main Execution (for standalone testing) ---
if __name__ == "__main__":
    signal, highs, lows = calculate_stock_strength_signal()
    
    print("--- Stock Price Strength (Sample) ---")
    print(f"Lookback: {LOOKBACK_PERIOD}")
    print(f"Stocks near 52w High: {highs}")
    print(f"Stocks near 52w Low: {lows}")
    print(f"Signal: {signal}") 