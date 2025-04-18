import numpy as np
from typing import Dict, Any

def calculate_stock_breadth(market_data: Dict[str, Any]) -> float:
    """
    Calculate the stock breadth indicator for the Chinese market.
    This indicator measures the breadth of market participation.
    
    Args:
        market_data: Dictionary containing market data from the API
        
    Returns:
        A score between 0 and 100
    """
    try:
        # Get relevant data
        indices = market_data.get('indices', {})
        tickers = market_data.get('tickers', {})
        
        # Track advancing and declining stocks
        advancing = 0
        declining = 0
        total_volume = 0
        price_changes = []
        
        # Process major indices
        major_indices = ['000001.SS', '000300.SS', '^HSI']
        for index in major_indices:
            if index in indices:
                index_data = indices[index]
                price_change = index_data.get('price_change_pct', 0)
                volume = index_data.get('volume', 0)
                
                if price_change > 0:
                    advancing += 1
                elif price_change < 0:
                    declining += 1
                    
                price_changes.append(price_change)
                total_volume += volume
        
        # Process major stocks
        major_stocks = ['0700.HK', '1211.HK', '600036.SS', '601318.SS', '601398.SS']
        for stock in major_stocks:
            if stock in tickers:
                stock_data = tickers[stock]
                price_change = stock_data.get('price_change_pct', 0)
                volume = stock_data.get('volume', 0)
                
                if price_change > 0:
                    advancing += 1
                elif price_change < 0:
                    declining += 1
                    
                price_changes.append(price_change)
                total_volume += volume
        
        # Calculate base score from advance/decline ratio
        total_issues = advancing + declining
        if total_issues == 0:
            return 50.0  # Neutral if no data
            
        base_score = (advancing / total_issues) * 100
        
        # Adjust score based on price momentum
        avg_price_change = np.mean(price_changes) if price_changes else 0
        momentum_adjustment = min(15, max(-15, avg_price_change))
        
        # Adjust score based on volume
        volume_adjustment = min(5, max(-5, (total_volume / len(price_changes)) / 1000000))
        
        # Calculate final score
        final_score = base_score + momentum_adjustment + volume_adjustment
        final_score = min(100, max(0, final_score))
        
        return float(final_score)
        
    except Exception as e:
        print(f"Error calculating CN stock breadth: {str(e)}")
        return 50.0  # Return neutral score on error 