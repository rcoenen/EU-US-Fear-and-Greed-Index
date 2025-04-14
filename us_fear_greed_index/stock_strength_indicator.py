import yfinance as yf
import pandas as pd
import traceback

# Configuration
# Sample of large-cap US stocks (Mix of S&P 500 / Nasdaq)
# Ideally, fetch a larger, more representative sample (e.g., S&P 100 or 500)
SAMPLE_TICKERS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B", "JPM", "JNJ",
    "V", "UNH", "XOM", "WMT", "PG", "MA", "HD", "CVX", "MRK", "LLY", "PEP", "BAC",
    "KO", "PFE", "CSCO", "TMO", "ABBV", "MCD", "COST", "CRM"
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
        print(f"Fetching {len(tickers)} US tickers for stock strength...")
        # Use auto_adjust=False to get consistent 'Close' column name
        data = yf.download(tickers, period=period, progress=False, auto_adjust=False)
        
        if data.empty or 'Close' not in data.columns:
            print("Error: Could not download sufficient stock data.")
            return "Neutral", 0, 0

        close_prices = data['Close'] # Should be a DataFrame with tickers as columns
        if close_prices.empty:
             print("Error: Closing price data is empty.")
             return "Neutral", 0, 0

        high_count = 0
        low_count = 0
        valid_tickers = 0

        # Iterate through each ticker column
        for ticker in tickers: # Iterate through the requested list to handle potential download failures
            if ticker not in close_prices.columns:
                # print(f"Skipping {ticker}: Data not downloaded.")
                continue
                
            ticker_series = close_prices[ticker].dropna()
            if len(ticker_series) < 200: # Ensure roughly 1 year of data
                # print(f"Skipping {ticker}: Insufficient data ({len(ticker_series)} points)")
                continue 
                
            valid_tickers += 1
            try:
                current_price = ticker_series.iloc[-1].item() # Use .item()
                high_52w = ticker_series.max().item()
                low_52w = ticker_series.min().item()
            except (IndexError, AttributeError, ValueError):
                 print(f"Warning: Could not get scalar price/high/low for {ticker}. Skipping.")
                 continue # Skip this ticker if we can't get scalar values

            # Check if near high
            if current_price >= high_52w * (1 - threshold):
                high_count += 1
            
            # Check if near low
            if current_price <= low_52w * (1 + threshold):
                low_count += 1
        
        if valid_tickers == 0:
            print("Error: No tickers had sufficient data for strength analysis.")
            return "Neutral", 0, 0

        print(f"Analyzed {valid_tickers} US tickers for strength.")
        # Determine signal
        if high_count > low_count:
            signal = "Greed"
        elif low_count > high_count:
            signal = "Fear"
        else:
            signal = "Neutral"
            
        return signal, high_count, low_count

    except Exception as e:
        print(f"Error calculating US stock strength signal: {e}")
        traceback.print_exc()
        return "Neutral", 0, 0

# --- Main Execution (for standalone testing) ---
if __name__ == "__main__":
    signal, highs, lows = calculate_stock_strength_signal()
    
    print("--- US Stock Price Strength (Sample) ---")
    print(f"Using {len(SAMPLE_TICKERS)} sample tickers.")
    print(f"Lookback: {LOOKBACK_PERIOD}")
    print(f"Stocks near 52w High: {highs}")
    print(f"Stocks near 52w Low: {lows}")
    print(f"Signal: {signal}") 