import pandas as pd
import yfinance as yf
from datetime import date, timedelta, datetime
import numpy as np

# Configuration
VOLATILITY_PROXY_TICKER = "VGK"  # Europe ETF proxy for volatility
HISTORICAL_PERIOD = "1y"    # Look back 1 year for percentile calculation
ROLLING_WINDOW_STD = 30     # Window for calculating rolling volatility

# Define volatility thresholds (annualized)
LOW_VOL_THRESHOLD = 0.15  # 15% annualized vol - equivalent to VIX at 15
HIGH_VOL_THRESHOLD = 0.30 # 30% annualized vol - equivalent to VIX at 30

def calculate_eu_volatility_indicator():
    """Calculates the EU volatility indicator score using VGK as a proxy.
    The calculation is designed to be more comparable with VIX:
    - Converts daily volatility to annualized
    - Uses similar thresholds to VIX (15-30 range)
    - Combines both absolute levels and relative percentiles
    
    Score interpretation:
    - Score > 75: Very low volatility (Extreme Greed)
    - Score 55-75: Below average volatility (Greed)
    - Score 45-55: Normal volatility (Neutral)
    - Score 25-45: Above average volatility (Fear)
    - Score < 25: Very high volatility (Extreme Fear)

    Returns:
        float: Calculated score (0-100)
    Raises:
         ValueError: If data cannot be fetched or calculated.
    """
    print(f"Calculating EU volatility using {VOLATILITY_PROXY_TICKER} proxy...")
    try:
        # Fetch 1 year of historical closing prices for the proxy
        data = yf.download(VOLATILITY_PROXY_TICKER, period=HISTORICAL_PERIOD, progress=False)['Close']
    except Exception as e:
        raise ValueError(f"Failed to download yfinance data for {VOLATILITY_PROXY_TICKER}: {e}")

    if data.empty or len(data) < ROLLING_WINDOW_STD + 5:
        raise ValueError(f"Insufficient historical data ({len(data)} points) found for {VOLATILITY_PROXY_TICKER} over {HISTORICAL_PERIOD}.")

    # Calculate daily returns
    returns = data.pct_change().dropna()
    if returns.empty:
        raise ValueError(f"Could not calculate returns for {VOLATILITY_PROXY_TICKER} (not enough data).")

    # Calculate the rolling volatility over the historical period
    try:
        rolling_vol = returns.rolling(window=ROLLING_WINDOW_STD).std().dropna()
        # Convert to annualized volatility (multiply by sqrt(252) trading days)
        rolling_vol = rolling_vol * np.sqrt(252)
    except Exception as e:
         raise ValueError(f"Could not calculate rolling volatility for {VOLATILITY_PROXY_TICKER}: {e}")

    if rolling_vol.empty or len(rolling_vol) < 2:
        raise ValueError(f"Insufficient rolling volatility data calculated for {VOLATILITY_PROXY_TICKER}.")

    # Get the latest calculated rolling volatility value
    try:
        latest_rolling_vol = float(rolling_vol.iloc[-1].iloc[0])  # Use .iloc[0] to get scalar value
        if pd.isna(latest_rolling_vol):
             raise ValueError(f"Latest rolling volatility value is NaN for {VOLATILITY_PROXY_TICKER}.")
    except (IndexError, TypeError, ValueError) as e:
        raise ValueError(f"Could not extract latest rolling volatility value: {e}")

    # Calculate the percentile rank of the latest rolling volatility
    try:
        percentile = (rolling_vol < latest_rolling_vol).mean()
        percentile = float(percentile.iloc[0])  # Use .iloc[0] to get scalar value
    except Exception as e:
        raise ValueError(f"Could not calculate percentile for {VOLATILITY_PROXY_TICKER} rolling volatility: {e}")

    # Calculate score using both absolute levels and relative percentile
    # 1. Score based on absolute levels (like VIX)
    if latest_rolling_vol <= LOW_VOL_THRESHOLD:
        abs_score = 100  # Very low vol -> Extreme greed
    elif latest_rolling_vol >= HIGH_VOL_THRESHOLD:
        abs_score = 0    # Very high vol -> Extreme fear
    else:
        # Linear interpolation between thresholds
        abs_score = 100 - ((latest_rolling_vol - LOW_VOL_THRESHOLD) / 
                          (HIGH_VOL_THRESHOLD - LOW_VOL_THRESHOLD)) * 100

    # 2. Score based on percentile (historical comparison)
    pct_score = (1.0 - percentile) * 100.0

    # 3. Combine both scores (60% weight on absolute levels, 40% on percentile)
    score = 0.6 * abs_score + 0.4 * pct_score
    score = np.clip(score, 0, 100)

    print(f"EU Volatility ({VOLATILITY_PROXY_TICKER} {ROLLING_WINDOW_STD}d annualized vol): Latest={latest_rolling_vol:.1%}, "
          f"Percentile={percentile:.0%}, Abs Score={abs_score:.1f}, Pct Score={pct_score:.1f}, Final Score={score:.2f}")
    return score

# Keep main for testing
if __name__ == "__main__":
    try:
        volatility_score = calculate_eu_volatility_indicator()
        print(f"\n--- EU Volatility Indicator Test ---")
        print(f"Calculated EU Volatility Indicator Score: {volatility_score:.2f}")
    except ValueError as e:
        print(f"Error calculating EU Volatility: {e}")