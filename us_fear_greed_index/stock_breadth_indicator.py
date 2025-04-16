import pandas as pd
import numpy as np
from utils.api_client import get_us_market_data

# Configuration
LOOKBACK_PERIOD = 20  # Days to look back for momentum
VOLUME_AVG_DAYS = 5  # Days to average volume over
MIN_PRICE_CHANGE = 0.0001  # Minimum price change to consider (0.01%)
DECLINE_WEIGHT = 6.0  # Weight for declining stocks
MOMENTUM_THRESHOLD = -0.001  # Ultra-sensitive momentum detection
EXTREME_FEAR_THRESHOLD = 0.25  # Threshold for extreme fear detection

# Sample ETFs to use for market breadth
SAMPLE_ETFS = [
    'XLK',  # Technology
    'XLF',  # Financials
    'XLV',  # Healthcare
    'XLE',  # Energy
    'XLP',  # Consumer Staples
    'XLY',  # Consumer Discretionary
    'XLI',  # Industrials
    'XLB',  # Materials
    'XLRE', # Real Estate
    'XLU'   # Utilities
]

# We'll use indices for additional data points
SAMPLE_INDICES = [
    '^GSPC',  # S&P 500
    '^DJI',   # Dow Jones
    '^IXIC',  # Nasdaq
    '^RUT'    # Russell 2000
]

def calculate_breadth_score():
    """
    Calculate the stock breadth score based on price momentum and volume analysis
    of major US market sectors and indices.
    """
    try:
        # Fetch data from API
        print(f"\nDebug - Stock Breadth: Starting calculation with {len(SAMPLE_ETFS)} ETFs and {len(SAMPLE_INDICES)} indices")
        market_data = get_us_market_data()
        
        # Get ETF data
        etf_data = market_data.get("sector_etfs", {})
        indices_data = market_data.get("indices", {})
        
        if not etf_data and not indices_data:
            print("Debug - Stock Breadth: No ETF or index data available")
            raise ValueError("Failed to fetch data for US market sectors")
            
        # Initialize counters
        advancing = 0
        declining = 0
        momentum_score = 0
        volume_score = 0
        valid_tickers = 0
        total_price_change = 0
        
        # Process each ETF
        for etf in SAMPLE_ETFS:
            try:
                if etf not in etf_data:
                    print(f"Debug - Stock Breadth: No data for {etf}")
                    continue
                    
                data = etf_data[etf]
                
                # Extract key metrics
                current_price = data.get("current_price")
                ma_200 = data.get("ma_200")
                volume = data.get("volume", 0)
                momentum_value = data.get("momentum", 0) / 100  # Convert from percentage to decimal
                rsi = data.get("rsi", 50)
                
                # Skip if missing essential data
                if not current_price or not ma_200 or volume <= 0:
                    print(f"Debug - Stock Breadth: Insufficient data for {etf}")
                    continue
                
                # Use momentum as price change
                price_change = momentum_value
                total_price_change += price_change
                
                # Calculate momentum using price vs MA
                momentum = (current_price - ma_200) / ma_200
                
                # Assume average volume is equal to current volume (simplified)
                latest_volume = volume
                volume_avg = volume
                
                # Count advancing/declining sectors
                if abs(price_change) >= MIN_PRICE_CHANGE:
                    if price_change > 0:
                        advancing += 1
                        print(f"Debug - Stock Breadth: {etf} advancing with {price_change:.2%} change")
                    else:
                        declining += 1
                        print(f"Debug - Stock Breadth: {etf} declining with {price_change:.2%} change")
                else:
                    print(f"Debug - Stock Breadth: {etf} unchanged (change below threshold: {price_change:.2%})")
                
                # Calculate momentum contribution
                if momentum < MOMENTUM_THRESHOLD:
                    momentum_score += 1.8
                
                # Calculate volume contribution using RSI
                if rsi < 40:  # Oversold condition with volume
                    volume_score += 1.5
                elif rsi > 60:  # Overbought condition with volume
                    volume_score += 0.3
                
                valid_tickers += 1
                
            except Exception as e:
                print(f"Debug - Stock Breadth: Error processing {etf}: {str(e)}")
                continue
        
        # Process each index
        for index in SAMPLE_INDICES:
            try:
                if index not in indices_data:
                    print(f"Debug - Stock Breadth: No data for {index}")
                    continue
                    
                data = indices_data[index]
                
                # Extract key metrics
                momentum_value = data.get("momentum", 0) / 100  # Convert from percentage to decimal
                
                # Skip if missing essential data
                if momentum_value == 0:
                    print(f"Debug - Stock Breadth: Insufficient data for {index}")
                    continue
                
                # Use momentum as price change
                price_change = momentum_value
                total_price_change += price_change
                
                # Count advancing/declining indices
                if abs(price_change) >= MIN_PRICE_CHANGE:
                    if price_change > 0:
                        advancing += 1
                        print(f"Debug - Stock Breadth: {index} advancing with {price_change:.2%} change")
                    else:
                        declining += 1
                        print(f"Debug - Stock Breadth: {index} declining with {price_change:.2%} change")
                else:
                    print(f"Debug - Stock Breadth: {index} unchanged (change below threshold: {price_change:.2%})")
                
                valid_tickers += 1
                
            except Exception as e:
                print(f"Debug - Stock Breadth: Error processing {index}: {str(e)}")
                continue
        
        print(f"\nDebug - Stock Breadth Summary:")
        print(f"Valid Tickers: {valid_tickers}")
        print(f"Advancing: {advancing}")
        print(f"Declining: {declining}")
        print(f"Average Price Change: {(total_price_change/valid_tickers):.2%}")
        
        if valid_tickers == 0:
            raise ValueError("No tickers had sufficient data for breadth analysis.")
        
        if (advancing + declining) == 0:
            print("Debug - Stock Breadth: No advancing or declining stocks found")
            # Use sigmoid of average price change instead of 0
            normalized_change = total_price_change / (valid_tickers * 0.05)  # Scale by 5%
            sigmoid = 1 / (1 + np.exp(-normalized_change))
            score = sigmoid * 100
            score = max(5, min(95, score))
            return score
        
        # Calculate base score using sigmoid for smoother scaling
        ratio = advancing / (advancing + declining)
        normalized_ratio = (ratio - 0.5) * 4  # Scale difference from 0.5 to make sigmoid more sensitive
        sigmoid = 1 / (1 + np.exp(-normalized_ratio))
        base_score = sigmoid * 100
        
        # Apply momentum and volume adjustments with reduced impact
        momentum_adjustment = (momentum_score / valid_tickers) * 10  # Reduced from 20
        volume_adjustment = (volume_score / valid_tickers) * 7.5     # Reduced from 15
        
        # Combine scores with adjustments
        final_score = base_score - momentum_adjustment - volume_adjustment
        
        # Ensure score is within bounds but avoid extremes
        final_score = max(5, min(95, final_score))
        
        print(f"Debug - Stock Breadth: Final Score Components:")
        print(f"Base Score: {base_score:.2f}")
        print(f"Momentum Adjustment: -{momentum_adjustment:.2f}")
        print(f"Volume Adjustment: -{volume_adjustment:.2f}")
        print(f"Final Score: {final_score:.2f}")
        
        return final_score
        
    except Exception as e:
        print(f"Error calculating breadth score: {str(e)}")
        raise ValueError("Sorry, cannot calculate data at this time. Please try again in a few minutes.")

# --- Main Execution (for standalone testing) ---
if __name__ == "__main__":
    score = calculate_breadth_score()
    
    print("--- US Stock Price Breadth (Sample) ---")
    print(f"Calculated Score: {score:.2f}") 