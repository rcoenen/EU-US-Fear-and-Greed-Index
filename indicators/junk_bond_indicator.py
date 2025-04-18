from typing import Dict, Any
from .base_indicator import BaseIndicator

class JunkBondIndicator(BaseIndicator):
    """
    Calculates junk bond demand based on high-yield vs investment-grade bond spreads.
    Higher spreads = lower score (fear)
    Lower spreads = higher score (greed)
    """
    
    def __init__(self, market: str):
        """
        Initialize the junk bond indicator for a specific market.
        
        Args:
            market: One of 'us', 'eu', or 'cn'
        """
        self.market = market
        
        # Define typical spread ranges for each market based on historical data
        self.spread_ranges = {
            'us': (20, 35),    # US spreads typically 20-35%
            'eu': (20, 35),    # EU spreads typically 20-35%
            'cn': (5, 15)      # CN spreads typically 5-15%
        }
    
    def calculate(self, market_data: Dict[str, Any]) -> float:
        """
        Calculate junk bond demand score based on bond spreads.
        
        Args:
            market_data: Dictionary containing market data from the API
            
        Returns:
            A score between 0 and 100
            
        Raises:
            ValueError: If bond_spreads data is missing.
        """
        try:
            # Get bond spreads data from the root level
            bond_spreads = market_data.get('bond_spreads', {})
            if not bond_spreads:
                raise ValueError(f"Bond spreads data missing for {self.market}")
            
            # Verify the bond spreads data is for the correct market
            if bond_spreads.get('market') != self.market:
                raise ValueError(f"Bond spreads data market mismatch: expected {self.market}, got {bond_spreads.get('market')}")
            
            # Get the credit spread directly from the API response
            spread = bond_spreads.get('credit_spread')
            if spread is None:
                raise ValueError(f"Credit spread missing in bond spreads data for {self.market}")
            
            # Get market-specific spread range
            min_spread, max_spread = self.spread_ranges[self.market]
            
            # Ensure spread is within a reasonable extended range before calculating score
            # Extend range slightly to avoid division by zero and handle extremes
            extended_min = min_spread - 2  # Allow slightly tighter spreads
            extended_max = max_spread + 3  # Allow slightly wider spreads
            
            # Clip spread to the extended range
            spread = max(extended_min, min(extended_max, spread))

            # Linear interpolation: map spread range to score range (lower spread = higher score)
            # Score 100 at extended_min, Score 0 at extended_max
            if extended_max == extended_min:
                 # This should not happen with current ranges, but check anyway
                raise ValueError(f"Invalid spread range for {self.market}: min={min_spread}, max={max_spread}")
            
            # Calculate the score inversely proportional to the spread
            score = 100 * (extended_max - spread) / (extended_max - extended_min)

            return max(0, min(100, score))
            
        except KeyError as e:
            # Re-raise key errors as ValueErrors
            raise ValueError(f"Missing expected key in market data: {e}")
        except Exception as e:
            # Re-raise other exceptions
            raise e 