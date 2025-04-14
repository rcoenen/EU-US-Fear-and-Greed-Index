import pandas as pd
import yfinance as yf # Re-add yfinance
from datetime import date, timedelta, datetime # Keep datetime
import numpy as np # Add numpy import
# import vstoxx_scraper # Remove scraper import

# Configuration
# VSTOXX_TICKER = "^V2TX" # No longer needed
VOLATILITY_PROXY_TICKER = "VGK" # Europe ETF proxy
HISTORICAL_PERIOD = "1y"    # Look back 1 year for percentile calculation
ROLLING_WINDOW_STD = 30     # Window for calculating rolling volatility

def calculate_eu_volatility_indicator():
    """Calculates the EU volatility indicator score based on the percentile rank
    of the current rolling volatility (using VGK proxy) compared to its 1-year history.
    A higher percentile rank (volatility is high relative to history) indicates Fear (lower score).
    A lower percentile rank (volatility is low relative to history) indicates Greed (higher score).
    Raises ValueError if data cannot be fetched or calculated.

    Returns:
        float: Calculated score (0-100) based on inverted percentile rank.
               Returns 50 on critical error.
    """
    print(f"Fetching 1-year proxy data for {VOLATILITY_PROXY_TICKER} for EU volatility percentile...")
    try:
        # Fetch 1 year of historical closing prices for the proxy
        data = yf.download(VOLATILITY_PROXY_TICKER, period=HISTORICAL_PERIOD, progress=False)['Close']
    except Exception as e:
        raise ValueError(f"Failed to download yfinance data for {VOLATILITY_PROXY_TICKER}: {e}")

    if data.empty or len(data) < ROLLING_WINDOW_STD + 5: # Need enough for rolling window + some history
        raise ValueError(f"Insufficient historical data ({len(data)} points) found for {VOLATILITY_PROXY_TICKER} over {HISTORICAL_PERIOD}.")

    # Calculate daily returns
    returns = data.pct_change().dropna()
    if returns.empty:
        raise ValueError(f"Could not calculate returns for {VOLATILITY_PROXY_TICKER} (not enough data).")

    # Calculate the rolling volatility over the historical period
    try:
        rolling_vol = returns.rolling(window=ROLLING_WINDOW_STD).std().dropna()
    except Exception as e:
         raise ValueError(f"Could not calculate rolling volatility for {VOLATILITY_PROXY_TICKER}: {e}")

    if rolling_vol.empty or len(rolling_vol) < 2: # Need at least two points to compare
        raise ValueError(f"Insufficient rolling volatility data calculated for {VOLATILITY_PROXY_TICKER}.")

    # Get the latest calculated rolling volatility value
    try:
        latest_rolling_vol = float(rolling_vol.iloc[-1])
        if pd.isna(latest_rolling_vol):
             raise ValueError(f"Latest rolling volatility value is NaN for {VOLATILITY_PROXY_TICKER}.")
    except (IndexError, TypeError, ValueError) as e:
        raise ValueError(f"Could not extract latest rolling volatility value: {e}")

    # Calculate the percentile rank of the latest rolling volatility
    try:
        percentile = (rolling_vol < latest_rolling_vol).mean()
        percentile = float(percentile) # Explicitly cast percentile to float
    except Exception as e:
        raise ValueError(f"Could not calculate percentile for {VOLATILITY_PROXY_TICKER} rolling volatility: {e}")

    # Score is the inverted percentile (1 - percentile)
    # High Vol -> High percentile -> Low score (Fear)
    # Low Vol -> Low percentile -> High score (Greed)
    score = (1.0 - percentile) * 100.0
    score = float(score) # Explicitly cast to float
    score = np.clip(score, 0, 100) # Ensure score is within 0-100 bounds

    # Determine signal string based on score (optional, but good for clarity if used elsewhere)
    signal = "Fear" if score < 45 else ("Greed" if score > 55 else "Neutral")

    print(f"EU Volatility Proxy ({VOLATILITY_PROXY_TICKER} {ROLLING_WINDOW_STD}d vol): Latest={latest_rolling_vol:.4f}, Percentile Rank vs {HISTORICAL_PERIOD}={percentile:.2%}, Score={score:.2f}")
    return score

# Keep main for testing
if __name__ == "__main__":
    try:
        volatility_score = calculate_eu_volatility_indicator()
        print(f"\n--- EU Volatility Indicator Test ({VOLATILITY_PROXY_TICKER} - Percentile Method) ---")
        print(f"Calculated EU Volatility Indicator Score: {volatility_score:.2f}")
    except ValueError as e:
        print(f"Error calculating EU Volatility: {e}")
        print("Setting score to 50 (Neutral) due to error.")
        volatility_score = 50.0

# Removed the main execution block that previously loaded from CSV and printed stats. 
# Removed the main execution block that previously loaded from CSV and printed stats. 
# Removed the main execution block that previously loaded from CSV and printed stats. 