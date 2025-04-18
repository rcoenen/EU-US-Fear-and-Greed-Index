from typing import Dict, Any
from .base_indicator import BaseIndicator

class MomentumIndicator(BaseIndicator):
    """
    Calculates market momentum based on price movements and RSI.
    Higher momentum = higher score (greed)
    Lower momentum = lower score (fear)
    """
    
    def __init__(self, market: str):
        """
        Initialize the momentum indicator for a specific market.
        
        Args:
            market: One of 'us', 'eu', or 'cn'
        """
        self.market = market
        self.index_map = {
            'us': '^GSPC',  # S&P 500
            'eu': '^STOXX50E',  # EURO STOXX 50
            'cn': '000300.SS'  # CSI 300
        }
    
    def calculate(self, market_data: Dict[str, Any]) -> float:
        """
        Calculate momentum score based on index price movements and RSI.
        
        Args:
            market_data: Dictionary containing market data from the API
            
        Returns:
            A score between 0 and 100
            
        Raises:
            ValueError: If required index data, momentum, or RSI is missing.
        """
        try:
            # Get the main index for this market
            index_id = self.index_map[self.market]
            
            # Get index data from the appropriate section
            if self.market == 'us':
                indices_data = market_data.get('indices', {})
            else:  # eu and cn markets
                indices_data = market_data.get('index', {})
            
            if not indices_data or index_id not in indices_data:
                raise ValueError(f"Index data missing for {index_id} in market data")
            
            index_data = indices_data[index_id]
            
            # Get momentum and RSI values - raise error if missing
            if 'momentum' not in index_data:
                raise ValueError(f"'momentum' key missing for index {index_id}")
            momentum = index_data['momentum']
            
            if 'rsi' not in index_data:
                raise ValueError(f"'rsi' key missing for index {index_id}")
            rsi = index_data['rsi']
            
            # Convert momentum to score (assuming momentum ranges from -20 to 20)
            score = 50 + (momentum * 2.5)
            
            # Adjust score based on RSI
            if rsi < 30:  # Oversold
                score = min(100, score + 10)
            elif rsi > 70:  # Overbought
                score = max(0, score - 10)
            
            # Ensure score is within bounds
            return max(0, min(100, score))
            
        except KeyError as e:
            # Re-raise key errors as ValueErrors for consistency
            raise ValueError(f"Missing expected key in market data: {e}")
        except Exception as e:
            # Re-raise other exceptions, potentially wrapping them
            # print(f"Unexpected error calculating momentum score for {self.market}: {str(e)}")
            raise e # Re-raise the original exception 