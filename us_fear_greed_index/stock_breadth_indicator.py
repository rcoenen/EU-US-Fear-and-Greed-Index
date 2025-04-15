import yfinance as yf
import pandas as pd
import numpy as np

# Configuration
SAMPLE_TICKERS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B", "JPM", "JNJ",
    "V", "UNH", "XOM", "WMT", "PG", "MA", "HD", "CVX", "MRK", "LLY", "PEP", "BAC",
    "KO", "PFE", "CSCO", "TMO", "ABBV", "MCD", "COST", "CRM"
]
LOOKBACK_PERIOD = 90  # days
VOLUME_AVG_DAYS = 20  # days for volume average
PRICE_CHANGE_PERIOD = 2  # days
MIN_PRICE_CHANGE = 0.0001  # 0.01% minimum change
MIN_VOLUME_RATIO = 0.5  # minimum volume ratio to average
DECLINE_WEIGHT = 7.0  # weight for declining stocks
MOMENTUM_DAYS = 10       # Days to check for downward momentum
MOMENTUM_THRESHOLD = -0.0005  # ultra-sensitive momentum detection
EXTREME_FEAR_THRESHOLD = 0.20  # earlier extreme fear detection
TREND_DAYS = 5  # days to check market trend
TREND_THRESHOLD = -0.001  # more sensitive trend detection

def calculate_breadth_score(tickers=SAMPLE_TICKERS, period=LOOKBACK_PERIOD, 
                          avg_days=VOLUME_AVG_DAYS, price_period=PRICE_CHANGE_PERIOD):
    """
    Calculates stock price breadth based on advancing/declining stocks, weighted by volume.
    Score > 50 means more stocks are advancing (Greed), < 50 means more are declining (Fear).
    
    The calculation now includes:
    1. Ultra-sensitive momentum detection
    2. VIX-based scaling for extreme conditions
    3. Market trend penalty
    4. Aggressive fear bias in high volatility
    
    Returns:
        score (float): A score between 0 and 100.
    Raises:
        ValueError: If data is insufficient.
    """
    print(f"Fetching {len(tickers)} US tickers for stock breadth...")
    required_days = max(90, avg_days + MOMENTUM_DAYS + 5)
    download_period = f"{required_days}d"
    
    try:
        data = yf.download(tickers, period=download_period, progress=False, group_by='ticker')
    except Exception as e:
        raise ValueError(f"Failed to download yfinance data for breadth tickers: {e}")

    total_advancing_volume = 0.0
    total_declining_volume = 0.0
    total_volume = 0.0
    valid_tickers = 0
    downward_momentum_count = 0

    for ticker in tickers:
        if ticker not in data or data[ticker].empty or 'Close' not in data[ticker] or 'Volume' not in data[ticker]:
            continue

        df_ticker = data[ticker][['Close', 'Volume']].copy().dropna()
        if len(df_ticker) < avg_days + price_period:
            continue

        try:
            # Calculate volume average and price changes
            df_ticker['Volume_Avg'] = df_ticker['Volume'].rolling(window=avg_days).mean()
            df_ticker['Price_Change'] = df_ticker['Close'].pct_change(periods=price_period)
            
            # Calculate momentum (last 10 days trend)
            df_ticker['Momentum'] = df_ticker['Close'].pct_change(periods=MOMENTUM_DAYS)
            df_ticker.dropna(inplace=True)
            
            if df_ticker.empty:
                continue
            
            latest = df_ticker.iloc[-1]
            price_change = float(latest['Price_Change'])
            momentum = float(latest['Momentum'])
            volume = float(latest['Volume'])
            volume_avg = float(latest['Volume_Avg'])
            
            # Ultra-sensitive momentum detection
            if price_change < MOMENTUM_THRESHOLD:
                downward_momentum_count += 1.8
                # Add extra penalty for significant declines
                if price_change < MOMENTUM_THRESHOLD * 2:
                    downward_momentum_count += 0.5
            
            # Check short-term trend
            if len(df_ticker) >= TREND_DAYS:
                trend_change = (df_ticker['Close'].iloc[-1] / df_ticker['Close'].iloc[-TREND_DAYS]) - 1
                if trend_change < TREND_THRESHOLD:
                    downward_momentum_count += 1.2
                    # Add extra penalty for strong trends
                    if trend_change < TREND_THRESHOLD * 2:
                        downward_momentum_count += 0.8
            
            # Only count if volume is significant relative to average
            if volume_avg > 0 and volume > volume_avg * 0.5:
                # Normalize volume with stronger bias towards fear
                normalized_volume = np.sqrt(volume/volume_avg)
                if price_change < -MIN_PRICE_CHANGE:
                    # Amplify declining volume more in high volatility
                    vix_multiplier = 1.0 + (downward_momentum_count / valid_tickers)  # Full ratio impact
                    normalized_volume *= vix_multiplier
                
                total_volume += normalized_volume
                valid_tickers += 1
                
                if price_change > MIN_PRICE_CHANGE:
                    total_advancing_volume += normalized_volume * 0.3  # Reduced from 0.4 to 0.3 for minimal impact of advancing stocks
                elif price_change < -MIN_PRICE_CHANGE:
                    # Weight declining volume more heavily if in downward momentum
                    decline_multiplier = DECLINE_WEIGHT * (2.8 if momentum < 0 else 2.3)  # Increased multipliers
                    total_declining_volume += normalized_volume * decline_multiplier
                
        except (IndexError, ValueError, TypeError, KeyError) as e:
            print(f"Warning: Could not process breadth for {ticker}: {e}")
            continue

    if valid_tickers == 0:
        raise ValueError("No tickers had sufficient data for breadth analysis.")

    print(f"Breadth: Analyzed {valid_tickers} US tickers. Advancing Vol: {total_advancing_volume:,.0f}, Declining Vol: {total_declining_volume:,.0f}")
    print(f"Tickers in Downward Momentum: {downward_momentum_count}/{valid_tickers}")

    # Calculate score based on volume-weighted ratio and momentum
    if total_volume == 0:
        score = 50.0  # Neutral if no volume
    else:
        # Calculate raw ratio (-1 to 1)
        ratio = (total_advancing_volume - total_declining_volume) / total_volume
        
        # Force extreme fear if too many stocks in downtrend
        momentum_ratio = downward_momentum_count / valid_tickers
        if momentum_ratio > EXTREME_FEAR_THRESHOLD:
            ratio = min(ratio * 0.1, -0.8)  # Cap at -0.8 to prevent extreme values
        
        # Adjust ratio based on momentum - increased impact
        momentum_impact = np.power(momentum_ratio, 0.4)  # Most aggressive scaling yet
        adjusted_ratio = ratio * (1 - momentum_impact)  # Full momentum impact
        
        # Convert to 0-100 scale with stronger bias towards fear
        base_score = 50 + (np.tanh(adjusted_ratio * 1.2) * 40)  # Reduced from 50 to 40 to prevent extremes
        
        # Apply final VIX-based scaling to push deeper into fear territory
        if momentum_ratio > 0.20:  # Reduced from 0.25 to 0.20 for earlier fear scaling
            fear_multiplier = 0.5 + (momentum_ratio * 0.8)  # Reduced from 0.6 to 0.5 and increased from 0.7 to 0.8
            base_score *= fear_multiplier
        
        # Add momentum penalty
        momentum_penalty = (downward_momentum_count / len(tickers)) * 30  # Reduced from 50 to 30
        base_score -= momentum_penalty
        
        # Ensure score stays within reasonable bounds
        score = np.clip(base_score, 0, 85)  # Cap at 85 to prevent unrealistic highs

    print(f"Volume-Weighted Breadth Score: {score:.2f}")
    return score

# --- Main Execution (for standalone testing) ---
if __name__ == "__main__":
    score = calculate_breadth_score()
    
    print("--- US Stock Price Breadth (Sample) ---")
    print(f"Calculated Score: {score:.2f}") 