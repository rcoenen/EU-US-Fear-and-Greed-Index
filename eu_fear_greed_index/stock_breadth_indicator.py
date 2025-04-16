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

# Add missing constants at the top
HIGH_THRESHOLD = 0.95  # 95% of 52-week high
LOW_THRESHOLD = 1.05   # 105% of 52-week low

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
    1. Analyzes price changes for each stock
    2. Counts advancing and declining stocks
    3. Applies momentum and volume adjustments
    4. Uses sigmoid scaling for smoother handling of extreme values
    
    Returns:
        score (float): A score between 0 and 100.
    Raises:
        ValueError: If data cannot be fetched or calculated.
    """
    try:
        print(f"Fetching {len(tickers)} EU tickers for stock breadth...")
        # Fetch 60 days of data to ensure we have enough history
        data = yf.download(tickers, period="60d", progress=False, group_by='ticker')
        
        advancing_count = 0
        declining_count = 0
        total_volume = 0.0
        valid_tickers = 0
        total_price_change = 0.0

        print("\nDebug - Stock Breadth: Starting calculation with", len(tickers), "tickers")
        
        for ticker in tickers:
            try:
                # Check if ticker exists in the data
                if ticker not in data.columns.levels[0]:
                    print(f"Warning: No data available for {ticker}")
                    continue

                # Extract Close and Volume data for the ticker
                close_data = data[ticker]['Close'].dropna()
                volume_data = data[ticker]['Volume'].dropna()

                if len(close_data) < 20:  # Require at least 20 days of data
                    print(f"Warning: Insufficient data for {ticker}")
                    continue

                # Calculate price change
                start_price = close_data.iloc[0]
                end_price = close_data.iloc[-1]
                price_change = (end_price - start_price) / start_price

                # Calculate average volume
                avg_volume = volume_data.iloc[-VOLUME_AVG_DAYS:].mean()

                if abs(price_change) >= MIN_PRICE_CHANGE:
                    total_volume += avg_volume
                    valid_tickers += 1
                    total_price_change += price_change

                    if price_change > 0:
                        advancing_count += 1
                        print(f"Debug - Stock Breadth: {ticker} advancing with {price_change:.2%} change")
                    else:
                        declining_count += 1
                        print(f"Debug - Stock Breadth: {ticker} declining with {price_change:.2%} change")

            except Exception as e:
                print(f"Warning: Error processing {ticker}: {str(e)}")
                continue

        if valid_tickers == 0:
            raise ValueError("No tickers had sufficient data for breadth analysis.")

        print("\nDebug - Stock Breadth Summary:")
        print(f"Valid Tickers: {valid_tickers}")
        print(f"Advancing: {advancing_count}")
        print(f"Declining: {declining_count}")
        print(f"Average Price Change: {total_price_change/valid_tickers:.2%}")

        # Calculate base score
        base_score = (advancing_count - declining_count) / valid_tickers * 50 + 50

        # Apply momentum adjustment
        momentum = total_price_change / valid_tickers
        momentum_adjustment = momentum * 100 if abs(momentum) > MOMENTUM_THRESHOLD else 0

        # Apply volume weighting
        volume_weight = 1.0
        if total_volume > 0:
            volume_weight = 1.0 + (declining_count / valid_tickers) * 0.5

        print("\nDebug - Stock Breadth: Final Score Components:")
        print(f"Base Score: {base_score:.2f}")
        print(f"Momentum Adjustment: {momentum_adjustment:.2f}")
        print(f"Volume Adjustment: {volume_weight:.2f}")

        # Calculate final score with sigmoid scaling
        final_score = base_score + momentum_adjustment
        final_score = final_score * volume_weight

        # Apply sigmoid transformation for smoother scaling
        normalized_score = (final_score - 50) / 50
        sigmoid = 1 / (1 + np.exp(-normalized_score))
        final_score = sigmoid * 100

        # Ensure score stays within reasonable bounds (5-95)
        final_score = max(5, min(95, final_score))

        return final_score

    except Exception as e:
        print(f"Error calculating breadth score: {str(e)}")
        raise ValueError("Sorry, cannot calculate data at this time. Please try again in a few minutes.")

# --- Main Execution (for standalone testing) ---
if __name__ == "__main__":
    score = calculate_breadth_score()
    
    print("--- Stock Price Breadth (Sample) ---")
    print(f"Calculated Score: {score:.2f}") 