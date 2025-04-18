import numpy as np
from typing import Dict, Any

def calculate_stock_strength(market_data: Dict[str, Any]) -> float:
    """
    Calculate the stock strength indicator for the Chinese market.
    This indicator measures the overall strength of major Chinese stocks and indices.
    
    Args:
        market_data: Dictionary containing market data from the API
        
    Returns:
        A score between 0 and 100
    """
    try:
        # Get relevant data
        indices = market_data.get('indices', {})
        tickers = market_data.get('tickers', {})
        
        # Calculate scores for major indices
        index_scores = []
        
        # Shanghai Composite (000001.SS)
        if '000001.SS' in indices:
            shanghai = indices['000001.SS']
            current_price = shanghai['current_price']
            ma_50 = shanghai['ma_50']
            ma_200 = shanghai['ma_200']
            
            # Score based on position relative to moving averages
            if current_price > ma_50 and ma_50 > ma_200:
                index_scores.append(100)  # Strong uptrend
            elif current_price > ma_50:
                index_scores.append(75)   # Short-term uptrend
            elif current_price > ma_200:
                index_scores.append(50)   # Long-term uptrend
            else:
                index_scores.append(25)   # Downtrend
        
        # CSI 300 (000300.SS)
        if '000300.SS' in indices:
            csi300 = indices['000300.SS']
            current_price = csi300['current_price']
            ma_50 = csi300['ma_50']
            ma_200 = csi300['ma_200']
            
            if current_price > ma_50 and ma_50 > ma_200:
                index_scores.append(100)
            elif current_price > ma_50:
                index_scores.append(75)
            elif current_price > ma_200:
                index_scores.append(50)
            else:
                index_scores.append(25)
        
        # Hang Seng Index (^HSI)
        if '^HSI' in indices:
            hsi = indices['^HSI']
            current_price = hsi['current_price']
            ma_50 = hsi['ma_50']
            ma_200 = hsi['ma_200']
            
            if current_price > ma_50 and ma_50 > ma_200:
                index_scores.append(100)
            elif current_price > ma_50:
                index_scores.append(75)
            elif current_price > ma_200:
                index_scores.append(50)
            else:
                index_scores.append(25)
        
        # Calculate scores for major stocks
        stock_scores = []
        major_stocks = ['0700.HK', '1211.HK', '600036.SS', '601318.SS', '601398.SS']
        
        for stock in major_stocks:
            if stock in tickers:
                stock_data = tickers[stock]
                current_price = stock_data['current_price']
                ma_50 = stock_data['ma_50']
                ma_200 = stock_data['ma_200']
                
                if current_price > ma_50 and ma_50 > ma_200:
                    stock_scores.append(100)
                elif current_price > ma_50:
                    stock_scores.append(75)
                elif current_price > ma_200:
                    stock_scores.append(50)
                else:
                    stock_scores.append(25)
        
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
        print(f"Error calculating CN stock strength: {str(e)}")
        return 50.0  # Return neutral score on error 