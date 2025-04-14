import yfinance as yf
import pandas as pd
import numpy as np

# Configuration
# Use the same sample tickers as stock_strength_indicator.py
SAMPLE_TICKERS = [
    "NESN.SW", "ASML.AS", "MC.PA", "ROG.SW", "OR.PA", "LIN.DE", 
    "SAP.DE", "SIE.DE", "AIR.PA", "TTE.PA", "IDEXY", "SAN.PA", 
    "DTE.DE", "CS.PA", "BAYN.DE", "MDT", "EL.PA", "PHIA.AS",
    "BNP.PA", "ADS.DE" # Added Adidas to make it 20
] 
LOOKBACK_PERIOD = "90d" # For volume average calculation (Changed from 3mo)
VOLUME_AVG_DAYS = 50 # 50-day average volume
PRICE_CHANGE_PERIOD = 1 # Check price change over 1 day

def calculate_breadth_score(tickers=SAMPLE_TICKERS, period=LOOKBACK_PERIOD, 
                                     avg_days=VOLUME_AVG_DAYS, price_period=PRICE_CHANGE_PERIOD):
    """
    Calculates stock price breadth based on advancing/declining volume for a sample.
    Score > 50 means Adv Vol > Dec Vol (Greed), < 50 means Dec Vol > Adv Vol (Fear).
    Uses total volume of advancing vs declining stocks.
    Raises ValueError if data is insufficient.
    Returns:
        score (float): A score between 0 and 100.
    """
    print(f"Fetching {len(tickers)} tickers for stock breadth...")
    # Calculate required download period (add buffer)
    required_days = max(90, avg_days + price_period + 5) # Use 90 days or calculated, whichever >
    download_period = f"{required_days}d"
    try:
        data = yf.download(tickers, period=download_period, progress=False, group_by='ticker')
    except Exception as e:
        raise ValueError(f"Failed to download yfinance data for breadth tickers: {e}")

    total_advancing_volume = 0.0
    total_declining_volume = 0.0
    valid_tickers = 0

    for ticker in tickers:
        if ticker not in data or data[ticker].empty or 'Close' not in data[ticker] or 'Volume' not in data[ticker]:
            # print(f"Warning: No or incomplete data for {ticker} in breadth calc.")
            continue

        # Create DataFrame for this ticker
        df_ticker = data[ticker][['Close', 'Volume']].copy().dropna()
        if len(df_ticker) < avg_days + price_period:
            # print(f"Skipping {ticker}: Insufficient data points ({len(df_ticker)}) for breadth calc.")
            continue

        valid_tickers += 1
        try:
            # Calculate required metrics
            df_ticker['Volume_Avg'] = df_ticker['Volume'].rolling(window=avg_days).mean()
            df_ticker['Price_Change'] = df_ticker['Close'].diff(periods=price_period)
            df_ticker.dropna(inplace=True) # Drop NaNs created by rolling/diff
            if df_ticker.empty:
                # print(f"Skipping {ticker}: Empty dataframe after calculations.")
                continue
            
            latest = df_ticker.iloc[-1]

            # Accumulate volume based on price change sign
            price_change = float(latest['Price_Change'])
            volume = float(latest['Volume'])
            
            if price_change > 0:
                total_advancing_volume += volume
            elif price_change < 0:
                total_declining_volume += volume
        except (IndexError, ValueError, TypeError, KeyError) as e:
            print(f"Warning: Could not process breadth for {ticker}: {e}")
            continue # Skip ticker on error

    if valid_tickers == 0:
        raise ValueError("No tickers had sufficient data for breadth analysis.")

    print(f"Breadth: Analyzed {valid_tickers} tickers. Total Advancing Vol: {total_advancing_volume:,.0f}, Total Declining Vol: {total_declining_volume:,.0f}")

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

# --- Main Execution (for standalone testing) ---
if __name__ == "__main__":
    score = calculate_breadth_score()
    
    print("--- Stock Price Breadth (Sample) ---")
    print(f"Calculated Score: {score:.2f}") 