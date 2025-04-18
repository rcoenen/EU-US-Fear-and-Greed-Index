import numpy as np
from typing import Dict, Any

def calculate_momentum(market_data: Dict[str, Any]) -> float:
    """
    Calculate the momentum indicator for the Chinese market.
    This indicator measures the strength and direction of price movements.
    
    Args:
        market_data: Dictionary containing market data from the API
        
    Returns:
        A score between 0 and 100
    """
    try:
        # Get relevant data
        indices = market_data.get('indices', {})
        tickers = market_data.get('tickers', {})
        
        # Calculate momentum scores for major indices
        index_momentums = []
        
        # Shanghai Composite (000001.SS)
        if '000001.SS' in indices:
            shanghai = indices['000001.SS']
            momentum = shanghai.get('momentum', 0)
            rsi = shanghai.get('rsi', 50)
            # Convert momentum to score (assuming momentum ranges from -20 to 20)
            score = min(100, max(0, 50 + (momentum * 2.5)))
            # Adjust score based on RSI
            if rsi < 30:  # Oversold
                score = min(100, score + 10)
            elif rsi > 70:  # Overbought
                score = max(0, score - 10)
            index_momentums.append(score)
        
        # CSI 300 (000300.SS)
        if '000300.SS' in indices:
            csi300 = indices['000300.SS']
            momentum = csi300.get('momentum', 0)
            rsi = csi300.get('rsi', 50)
            score = min(100, max(0, 50 + (momentum * 2.5)))
            if rsi < 30:
                score = min(100, score + 10)
            elif rsi > 70:
                score = max(0, score - 10)
            index_momentums.append(score)
        
        # Hang Seng Index (^HSI)
        if '^HSI' in indices:
            hsi = indices['^HSI']
            momentum = hsi.get('momentum', 0)
            rsi = hsi.get('rsi', 50)
            score = min(100, max(0, 50 + (momentum * 2.5)))
            if rsi < 30:
                score = min(100, score + 10)
            elif rsi > 70:
                score = max(0, score - 10)
            index_momentums.append(score)
        
        # Calculate momentum scores for major stocks
        stock_momentums = []
        major_stocks = ['0700.HK', '1211.HK', '600036.SS', '601318.SS', '601398.SS']
        
        for stock in major_stocks:
            if stock in tickers:
                stock_data = tickers[stock]
                momentum = stock_data.get('momentum', 0)
                rsi = stock_data.get('rsi', 50)
                score = min(100, max(0, 50 + (momentum * 2.5)))
                if rsi < 30:
                    score = min(100, score + 10)
                elif rsi > 70:
                    score = max(0, score - 10)
                stock_momentums.append(score)
        
        # Combine scores with weights
        if index_momentums and stock_momentums:
            # Weight indices more heavily (60%) than individual stocks (40%)
            index_score = sum(index_momentums) / len(index_momentums)
            stock_score = sum(stock_momentums) / len(stock_momentums)
            final_score = (index_score * 0.6) + (stock_score * 0.4)
        elif index_momentums:
            final_score = sum(index_momentums) / len(index_momentums)
        elif stock_momentums:
            final_score = sum(stock_momentums) / len(stock_momentums)
        else:
            raise ValueError("No valid data available for momentum calculation")
        
        return final_score
        
    except Exception as e:
        print(f"Error calculating momentum score: {str(e)}")
        raise ValueError("Sorry, cannot calculate data at this time. Please try again in a few minutes.") 