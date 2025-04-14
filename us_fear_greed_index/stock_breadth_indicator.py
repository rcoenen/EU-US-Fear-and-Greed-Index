import yfinance as yf
import pandas as pd
import numpy as np
import traceback

# Configuration
# Use the same sample US tickers as stock_strength_indicator.py
SAMPLE_TICKERS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B", "JPM", "JNJ",
    "V", "UNH", "XOM", "WMT", "PG", "MA", "HD", "CVX", "MRK", "LLY", "PEP", "BAC",
    "KO", "PFE", "CSCO", "TMO", "ABBV", "MCD", "COST", "CRM"
]
LOOKBACK_PERIOD = "90d" # For volume average calculation
VOLUME_AVG_DAYS = 50 # 50-day average volume
PRICE_CHANGE_PERIOD = 1 # Check price change over 1 day

def calculate_breadth_score(tickers=SAMPLE_TICKERS, period=LOOKBACK_PERIOD, 
                                     avg_days=VOLUME_AVG_DAYS, price_period=PRICE_CHANGE_PERIOD):
    """
    Calculates stock price breadth based on advancing/declining volume for a sample.
    Returns:
        score (float): Numerical score between 0 and 100.
    """
    try:
        print(f"Fetching {len(tickers)} US tickers for stock breadth...")
        # Need more than avg_days history. Ensure period is in days for comparison.
        try:
            lookback_td = pd.to_timedelta(period)
        except ValueError:
             print(f"Warning: Invalid lookback period format '{period}'. Defaulting to 90 days.")
             lookback_td = pd.to_timedelta("90d")

        # Calculate required download period (add buffer for rolling calculations)
        required_days = max(lookback_td.days, avg_days + price_period + 5) # Add buffer
        download_period = f"{required_days}d"
        
        # Use auto_adjust=False for separate Close/Volume
        data = yf.download(tickers, period=download_period, progress=False, auto_adjust=False)
        
        if data.empty or 'Close' not in data.columns or 'Volume' not in data.columns:
            print("Error: Could not download sufficient stock data (Close/Volume).")
            raise ValueError("No tickers had sufficient data for breadth analysis.")

        close_prices = data['Close']
        volumes = data['Volume']
        
        if close_prices.empty or volumes.empty:
             print("Error: Closing price or volume data is empty.")
             raise ValueError("No tickers had sufficient data for breadth analysis.")

        total_advancing_volume = 0.0
        total_declining_volume = 0.0
        valid_tickers = 0

        # Iterate through each ticker
        for ticker in tickers: # Iterate requested tickers
            if ticker not in close_prices.columns or ticker not in volumes.columns:
                 # print(f"Skipping {ticker}: Close or Volume data missing.")
                 continue # Skip if data is missing for this ticker
                 
            ticker_close = close_prices[ticker].dropna()
            ticker_volume = volumes[ticker].dropna()
            
            # Align data (inner join on index)
            aligned_data = pd.concat([ticker_close, ticker_volume], axis=1, keys=['Close', 'Volume']).dropna()
            
            if len(aligned_data) < avg_days + price_period:
                # print(f"Skipping {ticker}: Insufficient aligned data points ({len(aligned_data)})")
                continue
            
            valid_tickers += 1
            
            # Calculate volume average
            aligned_data['Volume_Avg'] = aligned_data['Volume'].rolling(window=avg_days, min_periods=1).mean()
            
            # Calculate price change
            aligned_data['Price_Change'] = aligned_data['Close'].diff(periods=price_period)
            
            # Get latest data point (ensure it exists)
            if aligned_data.empty:
                continue
            latest = aligned_data.iloc[-1]

            # Check conditions (handle potential NaNs)
            if pd.isna(latest['Volume']) or pd.isna(latest['Volume_Avg']) or pd.isna(latest['Price_Change']):
                continue # Skip if key data is missing for the latest point
                
            # Accumulate volume based on price change sign
            price_change = float(latest['Price_Change'])
            volume = float(latest['Volume'])
            
            if price_change > 0:
                total_advancing_volume += volume
            elif price_change < 0:
                total_declining_volume += volume
        
        if valid_tickers == 0:
            raise ValueError("No tickers had sufficient data for breadth analysis.")
            
        print(f"Breadth: Analyzed {valid_tickers} US tickers. Total Advancing Vol: {total_advancing_volume:,.0f}, Total Declining Vol: {total_declining_volume:,.0f}")

        # Calculate score based on ratio
        total_volume = total_advancing_volume + total_declining_volume
        if total_volume == 0:
            score = 50.0 # Neutral if no significant volume movement
        else:
            # Ratio = (Adv - Dec) / (Adv + Dec), ranges -1 to 1
            ratio = (total_advancing_volume - total_declining_volume) / total_volume
            # Scale ratio to 0-100
            score = 50 + (ratio * 50)

        score = np.clip(score, 0, 100)
        print(f"Volume-Weighted Breadth Score: {score:.2f}")
        return score

    except Exception as e:
        print(f"Error calculating US stock breadth signal: {e}")
        traceback.print_exc()
        raise ValueError("Error calculating US stock breadth signal.")

# --- Main Execution (for standalone testing) ---
if __name__ == "__main__":
    score = calculate_breadth_score()
    
    print("--- US Stock Price Breadth (Sample) ---")
    print(f"Using {len(SAMPLE_TICKERS)} sample tickers.")
    print(f"Period: {LOOKBACK_PERIOD}, Volume Avg Days: {VOLUME_AVG_DAYS}")
    print(f"Calculated Score: {score:.2f}") 