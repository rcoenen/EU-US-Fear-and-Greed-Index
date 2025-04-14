import yfinance as yf
import pandas as pd
import numpy as np

# Configuration
VIX_TICKER = "^VIX"
HISTORICAL_PERIOD = "1y" # Look back 1 year for percentile calculation

def calculate_volatility_signal():
    """Calculates the US volatility signal based on the percentile rank of the current VIX
    level compared to its 1-year history.
    A higher percentile rank (VIX is high relative to history) indicates Fear (lower score).
    A lower percentile rank (VIX is low relative to history) indicates Greed (higher score).
    Raises ValueError if data cannot be fetched or calculated.

    Returns:
        signal (str): 'Fear', 'Greed', or 'Neutral'.
        score (float): Calculated score (0-100) based on inverted percentile rank.
                     Returns 50 on critical error.
    """
    print(f"Fetching 1-year VIX data for {VIX_TICKER}...")
    try:
        # Fetch 1 year of historical closing prices
        vix_data = yf.download(VIX_TICKER, period=HISTORICAL_PERIOD, progress=False)['Close']
    except Exception as e:
        raise ValueError(f"Failed to download yfinance data for {VIX_TICKER}: {e}")

    if vix_data.empty or len(vix_data) < 20: # Need a reasonable amount of data
        raise ValueError(f"Insufficient historical data ({len(vix_data)} points) found for {VIX_TICKER} over {HISTORICAL_PERIOD}.")

    # Get the latest VIX value
    try:
        latest_vix = float(vix_data.iloc[-1])
        if pd.isna(latest_vix):
             raise ValueError(f"Latest VIX value is NaN for {VIX_TICKER}.")
    except (IndexError, TypeError, ValueError) as e:
        raise ValueError(f"Could not extract latest VIX value: {e}")

    # Calculate the percentile rank of the latest VIX value
    # percentile = (number of values strictly less than latest_vix) / (total number of values)
    try:
        # Exclude the latest value itself when calculating the rank against history if needed,
        # but .mean() handles Series comparison well.
        percentile = (vix_data < latest_vix).mean()
        percentile = float(percentile) # Explicitly cast percentile to float
    except Exception as e:
        raise ValueError(f"Could not calculate percentile for {VIX_TICKER}: {e}")

    # Score is the inverted percentile (1 - percentile)
    # High VIX -> High percentile -> Low score (Fear)
    # Low VIX -> Low percentile -> High score (Greed)
    score = (1.0 - percentile) * 100.0
    score = float(score) # Explicitly cast to float
    score = np.clip(score, 0, 100) # Ensure score is within 0-100 bounds

    # Determine signal string based on score
    signal = "Fear" if score < 45 else ("Greed" if score > 55 else "Neutral")

    print(f"US Volatility ({VIX_TICKER}): Latest={latest_vix:.2f}, Percentile Rank vs {HISTORICAL_PERIOD}={percentile:.2%}, Score={score:.2f}")
    return signal, score

# Keep main for testing
if __name__ == "__main__":
    try:
        signal, score = calculate_volatility_signal()
        print(f"\n--- US Volatility Indicator Test ({VIX_TICKER} - Percentile Method) ---")
        print(f"Signal: {signal}, Score: {score:.2f}")
    except ValueError as e:
        print(f"Error calculating US Volatility: {e}")
        print("Setting score to 50 (Neutral) due to error.")
        signal = "Neutral"
        score = 50.0 