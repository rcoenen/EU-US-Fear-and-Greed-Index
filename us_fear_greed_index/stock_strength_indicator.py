import yfinance as yf
import pandas as pd
import numpy as np

# Configuration
# Sample of large-cap US stocks (Mix of S&P 500 / Nasdaq)
# Ideally, fetch a larger, more representative sample (e.g., S&P 100 or 500)
SAMPLE_TICKERS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B", "JPM", "JNJ",
    "V", "UNH", "XOM", "WMT", "PG", "MA", "HD", "CVX", "MRK", "LLY", "PEP", "BAC",
    "KO", "PFE", "CSCO", "TMO", "ABBV", "MCD", "COST", "CRM"
] 
LOOKBACK_PERIOD = "1y"  # For 52-week high/low
HIGH_THRESHOLD = 0.95  # within 5% of 52-week high
LOW_THRESHOLD = 1.05   # within 5% of 52-week low

def calculate_strength_score(tickers=SAMPLE_TICKERS, period=LOOKBACK_PERIOD):
    """
    Calculates stock price strength score (0-100) based on relative position to 52-week range.
    Uses bidirectional scoring to account for both highs and lows.
    Score > 50 means more strength (Greed), < 50 means more weakness (Fear).
    
    The calculation:
    1. Counts stocks near 52-week highs and lows
    2. Uses bidirectional scoring: 0 = all lows, 50 = neutral, 100 = all highs
    3. Applies volume weighting to account for market impact
    
    Returns:
        score (float): A score between 0 and 100.
    Raises:
        ValueError: If data cannot be fetched or calculated.
    """
    try:
        print(f"Fetching {len(tickers)} US tickers for stock strength...")
        data = yf.download(tickers, period=period, progress=False, group_by='ticker')
        
        high_count = 0
        low_count = 0
        total_volume = 0.0
        valid_tickers = 0

        for ticker in tickers:
            if ticker not in data or data[ticker].empty or 'Close' not in data[ticker] or 'Volume' not in data[ticker]:
                continue

            df_ticker = data[ticker][['Close', 'Volume']].copy().dropna()
            if len(df_ticker) < 50:  # Require at least 50 days of data
                continue

            latest = df_ticker.iloc[-1]
            current_price = float(latest['Close'])
            volume = float(latest['Volume'])

            high_52w = float(df_ticker['Close'].max())
            low_52w = float(df_ticker['Close'].min())

            if high_52w > 0 and low_52w > 0:  # Avoid division by zero
                total_volume += volume
                valid_tickers += 1

                if current_price >= high_52w * HIGH_THRESHOLD:
                    high_count += 1
                elif current_price <= low_52w * LOW_THRESHOLD:
                    low_count += 1

        if valid_tickers == 0:
            raise ValueError("No tickers had sufficient data for strength analysis.")

        score = ((high_count - low_count) / valid_tickers) * 50 + 50
        score = 50 + (np.tanh((score - 50) / 50) * 50)
        score = np.clip(score, 0, 100)

        return score
    except Exception as e:
        print(f"Error calculating strength score: {str(e)}")
        raise ValueError("Sorry, cannot calculate data at this time. Please try again in a few minutes.")

# --- Main Execution (for standalone testing) ---
if __name__ == "__main__":
    score = calculate_strength_score()
    
    print("--- US Stock Price Strength (Sample) ---")
    print(f"Using {len(SAMPLE_TICKERS)} sample tickers.")
    print(f"Lookback: {LOOKBACK_PERIOD}")
    print(f"Calculated Score: {score:.2f}") 