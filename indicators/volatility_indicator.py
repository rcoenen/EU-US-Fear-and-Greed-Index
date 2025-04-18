from typing import Dict, Any
from .base_indicator import BaseIndicator

class VolatilityIndicator(BaseIndicator):
    """
    Calculates market volatility score.
    Higher volatility = lower score (fear)
    Lower volatility = higher score (greed)
    """
    
    def __init__(self, market: str):
        """
        Initialize the volatility indicator for a specific market.
        
        Args:
            market: One of 'us', 'eu', or 'cn'
        """
        self.market = market
        self.volatility_map = {
            'us': '^VIX',  # VIX Index
            'eu': '^STOXX50E',  # EURO STOXX 50 (calculate from this)
            'cn': '000001.SS'  # Shanghai Composite (calculate from this)
        }
        
        # Define typical volatility ranges for each market
        self.volatility_ranges = {
            'us': (10, 40),  # VIX typical range
            'eu': (15, 35),  # STOXX volatility typical range
            'cn': (15, 30)   # Shanghai volatility typical range
        }
    
    def calculate(self, market_data: Dict[str, Any]) -> float:
        """
        Calculate volatility score based on market volatility.
        
        Args:
            market_data: Dictionary containing market data from the API
            
        Returns:
            A score between 0 and 100
        """
        try:
            # Get volatility data
            vol_id = self.volatility_map[self.market]
            min_vol, max_vol = self.volatility_ranges[self.market]
            
            if self.market == 'us':
                # US uses VIX directly
                vix_data = market_data.get('volatility', {}).get(vol_id, {})
                current_vol = vix_data.get('current_price', 20)
            else:
                # EU and CN calculate from their main indices
                index_data = market_data.get('volatility', {})
                current_vol = index_data.get('current_volatility', 20)
            
            # Calculate score based on volatility range
            if current_vol <= min_vol:
                score = 100  # Very low volatility = extreme greed
            elif current_vol >= max_vol:
                score = 0    # Very high volatility = extreme fear
            else:
                # Linear interpolation between thresholds
                score = 100 - ((current_vol - min_vol) / (max_vol - min_vol)) * 100
            
            return max(0, min(100, score))
            
        except Exception as e:
            print(f"Error calculating volatility score for {self.market}: {str(e)}")
            raise ValueError(f"Sorry, cannot calculate volatility data at this time. Please try again in a few minutes.") 