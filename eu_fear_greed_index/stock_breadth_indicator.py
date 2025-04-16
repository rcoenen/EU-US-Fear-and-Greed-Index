import pandas as pd
import numpy as np
from utils.safe_yf import safe_yf_multiple
import yfinance as yf

# Configuration
LOOKBACK_PERIOD = 20  # Days to look back for momentum
VOLUME_AVG_DAYS = 5  # Days to average volume over
MIN_PRICE_CHANGE = 0.0001  # Minimum price change to consider (0.01%)
DECLINE_WEIGHT = 6.0  # Weight for declining stocks
MOMENTUM_THRESHOLD = -0.001  # Ultra-sensitive momentum detection
EXTREME_FEAR_THRESHOLD = 0.25  # Threshold for extreme fear detection

# Sample tickers from EURO STOXX 50
SAMPLE_TICKERS = [
    'ENEL.MI', 'ISP.MI', 'TTE.PA', 'IBE.MC', 'ITX.MC',  # Energy & Utilities
    'BAYN.DE', 'IFX.DE', 'SIE.DE', 'ALV.DE', 'DTE.DE',  # German Industrials
    'ADS.DE', 'ABI.BR', 'NOVN.SW', 'NOKIA.HE', 'SAN.PA',  # Consumer & Healthcare
    'KER.PA', 'FLTR.L', 'STLAM.MI', 'UCG.MI', 'VOW.DE',  # Auto & Finance
    'CS.PA', 'PRX.AS'  # Additional major stocks
]

def calculate_breadth_score(tickers=SAMPLE_TICKERS, period=LOOKBACK_PERIOD):
    """
    Calculates stock breadth score (0-100) based on advancing vs declining stocks.
    Score > 50 means more advancing stocks (Greed), < 50 means more declining stocks (Fear).
    
    The calculation:
    1. Counts advancing and declining stocks
    2. Uses bidirectional scoring: 0 = all declining, 50 = neutral, 100 = all advancing
    3. Applies volume weighting to account for market impact
    
    Returns:
        score (float): A score between 0 and 100.
    Raises:
        ValueError: If data cannot be fetched or calculated.
    """
    try:
        print(f"Fetching {len(tickers)} EU tickers for stock breadth...")
        data = yf.download(tickers, period=period, progress=False, group_by='ticker')
        
        advancing_count = 0
        declining_count = 0
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
                    advancing_count += 1
                elif current_price <= low_52w * LOW_THRESHOLD:
                    declining_count += 1

        if valid_tickers == 0:
            raise ValueError("No tickers had sufficient data for breadth analysis.")

        if valid_tickers > 0:
            vix_multiplier = 1.0 + (declining_count / valid_tickers)  # Full ratio impact
        else:
            vix_multiplier = 1.0

        score = ((advancing_count - declining_count) / valid_tickers) * 50 + 50
        score = 50 + (np.tanh((score - 50) / 50) * 50)
        score = np.clip(score, 0, 100)

        return score
    except Exception as e:
        print(f"Error calculating breadth score: {str(e)}")
        raise ValueError("Sorry, cannot calculate data at this time. Please try again in a few minutes.")

# --- Main Execution (for standalone testing) ---
if __name__ == "__main__":
    score = calculate_breadth_score()
    
    print("--- Stock Price Breadth (Sample) ---")
    print(f"Calculated Score: {score:.2f}") 