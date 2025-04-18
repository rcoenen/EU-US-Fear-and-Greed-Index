from typing import Dict, Any
from .base_indicator import BaseIndicator

class MADeviationIndicator(BaseIndicator):
    """
    Calculates moving average deviation score.
    Higher deviation above MA = higher score (greed)
    Higher deviation below MA = lower score (fear)
    """
    
    def __init__(self, market: str):
        """
        Initialize the MA deviation indicator for a specific market.
        
        Args:
            market: One of 'us', 'eu', or 'cn'
        """
        self.market = market
        self.index_map = {
            'us': '^GSPC',  # S&P 500
            'eu': '^STOXX50E',  # EURO STOXX 50
            'cn': '000001.SS'  # Shanghai Composite
        }
    
    def calculate(self, market_data: Dict[str, Any]) -> float:
        """
        Calculate MA deviation score based on the difference between current price and 50-day moving average.
        
        Args:
            market_data: Dictionary containing market data from the API
            
        Returns:
            A score between 0 and 100
            
        Raises:
            ValueError: If required index data, current_price, or ma_50 is missing, or if ma_50 is zero.
        """
        try:
            # Get the main index for this market
            index_id = self.index_map[self.market]
            indices_data = market_data.get('indices', {})
            
            # For EU market, also check the 'index' section if 'indices' is empty
            if self.market == 'eu' and not indices_data:
                indices_data = market_data.get('index', {})
                
            if index_id not in indices_data:
                raise ValueError(f"Index data missing for {index_id} in market data")
                
            index_data = indices_data[index_id]
            
            # Get current price and MA values - raise error if missing
            if 'current_price' not in index_data:
                raise ValueError(f"'current_price' key missing for index {index_id}")
            current_price = index_data['current_price']
            
            if 'ma_50' not in index_data:
                 raise ValueError(f"'ma_50' key missing for index {index_id}")
            ma_50 = index_data['ma_50']
            
            # Calculate percentage deviation - raise error if MA is 0
            if ma_50 == 0:
                raise ValueError(f"MA50 is zero for index {index_id}, cannot calculate deviation")
                
            deviation = ((current_price - ma_50) / ma_50) * 100
            
            # Convert deviation to score
            if deviation <= -10:  # Extreme fear
                return 0.0
            elif deviation >= 10:  # Extreme greed
                return 100.0
            else:
                # Linear interpolation between -10% and 10%
                return 50.0 + (deviation * 5)
            
        except KeyError as e:
            # Re-raise key errors as ValueErrors for consistency
            raise ValueError(f"Missing expected key in market data: {e}")
        except Exception as e:
            # Re-raise other exceptions
            # print(f"Unexpected error calculating MA deviation score for {self.market}: {str(e)}")
            raise e 