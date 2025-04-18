import numpy as np
from typing import Dict, Any

def calculate_safe_haven(market_data: Dict[str, Any]) -> float:
    """
    Calculate the safe haven indicator for the Chinese market.
    This indicator measures the demand for safe haven assets.
    
    Args:
        market_data: Dictionary containing market data from the API
        
    Returns:
        A score between 0 and 100
    """
    try:
        # Get relevant data
        indices = market_data.get('indices', {})
        tickers = market_data.get('tickers', {})
        
        # Calculate safe haven scores for major indices
        index_scores = []
        
        # Shanghai Composite (000001.SS)
        if '000001.SS' in indices:
            shanghai = indices['000001.SS']
            # Use relative strength and volume as indicators
            relative_strength = shanghai.get('relative_strength', 0)
            volume = shanghai.get('volume', 0)
            # Higher relative strength and volume indicate more fear
            score = min(100, max(0, (relative_strength + volume) / 2))
            index_scores.append(score)
        
        # CSI 300 (000300.SS)
        if '000300.SS' in indices:
            csi300 = indices['000300.SS']
            relative_strength = csi300.get('relative_strength', 0)
            volume = csi300.get('volume', 0)
            score = min(100, max(0, (relative_strength + volume) / 2))
            index_scores.append(score)
        
        # Hang Seng Index (^HSI)
        if '^HSI' in indices:
            hsi = indices['^HSI']
            relative_strength = hsi.get('relative_strength', 0)
            volume = hsi.get('volume', 0)
            score = min(100, max(0, (relative_strength + volume) / 2))
            index_scores.append(score)
        
        # Calculate safe haven scores for major stocks
        stock_scores = []
        major_stocks = ['0700.HK', '1211.HK', '600036.SS', '601318.SS', '601398.SS']
        
        for stock in major_stocks:
            if stock in tickers:
                stock_data = tickers[stock]
                relative_strength = stock_data.get('relative_strength', 0)
                volume = stock_data.get('volume', 0)
                score = min(100, max(0, (relative_strength + volume) / 2))
                stock_scores.append(score)
        
        # Combine scores with weights
        if not index_scores and not stock_scores:
            return 50.0  # Neutral if no data available
        
        # Weight indices more heavily than individual stocks
        index_weight = 0.6
        stock_weight = 0.4
        
        index_avg = np.mean(index_scores) if index_scores else 50.0
        stock_avg = np.mean(stock_scores) if stock_scores else 50.0
        
        final_score = (index_avg * index_weight) + (stock_avg * stock_weight)
        
        return float(final_score)
        
    except Exception as e:
        print(f"Error calculating CN safe haven: {str(e)}")
        return 50.0  # Return neutral score on error 