import pandas as pd
import numpy as np
from utils.safe_yf import safe_yf_multiple

# Configuration
LOOKBACK_PERIOD = 20  # Days to look back for momentum
VOLUME_AVG_DAYS = 5  # Days to average volume over
MIN_PRICE_CHANGE = 0.0001  # Minimum price change to consider (0.01%)
DECLINE_WEIGHT = 6.0  # Weight for declining stocks
MOMENTUM_THRESHOLD = -0.001  # Ultra-sensitive momentum detection
EXTREME_FEAR_THRESHOLD = 0.25  # Threshold for extreme fear detection

# Sample tickers from S&P 500
SAMPLE_TICKERS = [
    'AAPL', 'MSFT', 'AMZN', 'GOOGL', 'META',  # Tech Giants
    'JPM', 'BAC', 'WFC', 'GS', 'MS',  # Financials
    'JNJ', 'PFE', 'UNH', 'MRK', 'ABBV',  # Healthcare
    'XOM', 'CVX', 'COP', 'SLB', 'EOG',  # Energy
    'PG', 'KO', 'PEP', 'MCD', 'WMT'  # Consumer Staples
]

def calculate_breadth_score():
    """
    Calculate the stock breadth score based on price momentum and volume analysis
    of major US stocks.
    """
    try:
        # Fetch data for all tickers
        print(f"Fetching {len(SAMPLE_TICKERS)} US tickers for stock breadth...")
        data = safe_yf_multiple(SAMPLE_TICKERS, period='1mo', interval='1d')
        
        if data is None or data.empty:
            raise ValueError("Failed to fetch data for US tickers")
        
        # Initialize counters
        advancing = 0
        declining = 0
        momentum_score = 0
        volume_score = 0
        valid_tickers = 0
        
        # Process each ticker
        for ticker in SAMPLE_TICKERS:
            try:
                if ticker not in data:
                    print(f"Warning: No data available for {ticker}")
                    continue
                    
                df = data[ticker]
                if df.empty or len(df) < LOOKBACK_PERIOD:
                    print(f"Warning: Insufficient data for {ticker}")
                    continue
                
                # Calculate price change and momentum
                latest = df.iloc[-1]
                prev = df.iloc[-LOOKBACK_PERIOD]
                
                price_change = float(latest['Close'] - prev['Close']) / prev['Close']
                momentum = float(latest['Close'] - df['Close'].rolling(window=LOOKBACK_PERIOD).mean().iloc[-1]) / df['Close'].rolling(window=LOOKBACK_PERIOD).mean().iloc[-1]
                
                # Calculate volume metrics
                volume = float(latest['Volume'])
                volume_avg = float(df['Volume'].rolling(window=VOLUME_AVG_DAYS).mean().iloc[-1])
                
                # Skip if any value is NaN
                if pd.isna(price_change) or pd.isna(momentum) or pd.isna(volume) or pd.isna(volume_avg):
                    print(f"Warning: NaN values detected for {ticker}")
                    continue
                
                # Count advancing/declining stocks
                if abs(price_change) >= MIN_PRICE_CHANGE:
                    if price_change > 0:
                        advancing += 1
                    else:
                        declining += 1
                
                # Calculate momentum contribution
                if momentum < MOMENTUM_THRESHOLD:
                    momentum_score += 1.8  # Increased weight for downward momentum
                
                # Calculate volume contribution
                if volume > volume_avg:
                    if price_change < 0:
                        volume_score += 1.5  # Increased weight for high volume on declines
                    else:
                        volume_score += 0.3  # Reduced impact of advancing volume
                
                valid_tickers += 1
                
            except Exception as e:
                print(f"Warning: Could not process breadth for {ticker}: {str(e)}")
                continue
        
        if valid_tickers == 0:
            raise ValueError("No tickers had sufficient data for breadth analysis.")
        
        # Calculate final scores
        if (advancing + declining) == 0:
            raise ZeroDivisionError("No advancing or declining stocks to calculate breadth ratio.")
        
        breadth_ratio = declining / (advancing + declining)
        momentum_ratio = momentum_score / valid_tickers
        volume_ratio = volume_score / valid_tickers
        
        # Combine scores with weights
        final_score = (
            breadth_ratio * 0.4 +  # Price movement breadth
            momentum_ratio * 0.3 +  # Momentum strength
            volume_ratio * 0.3     # Volume confirmation
        ) * 100
        
        # Apply extreme fear threshold
        if final_score < EXTREME_FEAR_THRESHOLD * 100:
            final_score *= 0.8  # Further reduce score in extreme fear
        
        return final_score
        
    except Exception as e:
        print(f"Error calculating breadth score: {str(e)}")
        raise ValueError("Sorry, cannot calculate data at this time. Please try again in a few minutes.")

# --- Main Execution (for standalone testing) ---
if __name__ == "__main__":
    score = calculate_breadth_score()
    
    print("--- US Stock Price Breadth (Sample) ---")
    print(f"Calculated Score: {score:.2f}") 