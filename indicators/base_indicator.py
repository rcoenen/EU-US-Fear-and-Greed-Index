from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseIndicator(ABC):
    """
    Base class for all fear and greed indicators.
    Each indicator should implement the calculate method to return a score between 0 and 100.
    """
    
    @abstractmethod
    def calculate(self, market_data: Dict[str, Any]) -> float:
        """
        Calculate the indicator score based on market data.
        
        Args:
            market_data: Dictionary containing market data from the API
            
        Returns:
            A score between 0 and 100, where:
            - 0-25: Extreme Fear
            - 25-45: Fear
            - 45-55: Neutral
            - 55-75: Greed
            - 75-100: Extreme Greed
        """
        pass
    
    def normalize_score(self, raw_score: float, min_val: float, max_val: float) -> float:
        """
        Normalize a raw score to the 0-100 range.
        
        Args:
            raw_score: The raw score to normalize
            min_val: Minimum expected value
            max_val: Maximum expected value
            
        Returns:
            Normalized score between 0 and 100
        """
        # Clip the raw score to the expected range
        clipped_score = max(min_val, min(max_val, raw_score))
        
        # Normalize to 0-100 range
        normalized = ((clipped_score - min_val) / (max_val - min_val)) * 100
        
        # Ensure final score is within 0-100
        return max(0, min(100, normalized)) 