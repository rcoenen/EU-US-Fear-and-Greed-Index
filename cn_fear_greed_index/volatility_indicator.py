import numpy as np
from typing import Dict, Any

def calculate_volatility(market_data: Dict[str, Any]) -> float:
    """
    Calculate the volatility indicator for the Chinese market.
    This indicator measures market volatility and uncertainty using a percentile-based approach
    that's comparable to the US VIX methodology.
    
    Higher volatility = lower score (more fear)
    Lower volatility = higher score (more greed)
    
    Args:
        market_data: Dictionary containing market data from the API
        
    Returns:
        A score between 0 and 100
    """
    try:
        # Get relevant data
        volatility_data = market_data.get('volatility_data', {})
        indices = market_data.get('indices', {})
        
        # First, check if we have historical volatility percentile data
        # This would be comparable to the US VIX percentile approach
        if 'CN_VOL_INDEX' in volatility_data and 'percentile' in volatility_data['CN_VOL_INDEX']:
            # Direct percentile data available
            percentile = volatility_data['CN_VOL_INDEX']['percentile']
            # Convert to score (invert percentile)
            # High volatility (high percentile) = low score (fear)
            score = 100 - (percentile * 100)
            print(f"CN Volatility (direct percentile): {percentile:.2%}, Score={score:.2f}")
            return float(score)
        
        # If no percentile data directly available, check for current and historical volatility
        if 'CN_VOL_INDEX' in volatility_data:
            vol_index = volatility_data['CN_VOL_INDEX']
            current_vol = vol_index.get('current', 20)
            historical_data = vol_index.get('historical', [])
            
            if historical_data:
                # Calculate percentile rank among historical data
                values_below = sum(1 for val in historical_data if val < current_vol)
                percentile = values_below / len(historical_data)
                score = 100 - (percentile * 100)
                print(f"CN Volatility (calculated percentile): {percentile:.2%}, Score={score:.2f}")
                return float(score)
        
        # Fallback to using index data if no direct volatility data is available
        index_volatilities = []
        primary_indices = ['000001.SS', '000300.SS', '^HSI']
        
        for idx_name in primary_indices:
            if idx_name in indices:
                idx_data = indices[idx_name]
                # Get volatility value, defaulting to historical median if not available
                volatility = idx_data.get('volatility', 20)
                
                # Convert raw volatility to score
                # Instead of a linear conversion, use a more comparable approach to US VIX
                # Based on typical ranges: 15% (low) to 30% (high) annualized volatility
                if volatility <= 15:
                    score = 100  # Very low volatility (extreme greed)
                elif volatility >= 30:
                    score = 0    # Very high volatility (extreme fear)
                else:
                    # Linear interpolation between thresholds (15-30 range)
                    score = 100 - ((volatility - 15) / (30 - 15)) * 100
                
                index_volatilities.append(score)
        
        # If we have volatility scores from indices, use weighted average
        if index_volatilities:
            final_score = np.mean(index_volatilities)
            print(f"CN Volatility (from indices): Score={final_score:.2f}")
            return float(final_score)
        
        # Default to neutral if no data available
        return 50.0
        
    except Exception as e:
        print(f"Error calculating CN volatility: {str(e)}")
        return 50.0  # Return neutral score on error 