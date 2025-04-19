import os
import sys
import numpy as np
from typing import Tuple, Dict, Any

# Add the parent directory to the path to import utils
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from utils.api_client import get_cn_market_data
# Remove local indicator imports
# from indicators.momentum_indicator import MomentumIndicator
# from indicators.volatility_indicator import VolatilityIndicator
# from indicators.safe_haven_indicator import SafeHavenIndicator
# from indicators.junk_bond_indicator import JunkBondIndicator
# from indicators.rsi_indicator import RSIIndicator
# from indicators.ma_deviation_indicator import MADeviationIndicator

def interpret_score(score: float) -> str:
    """
    Interpret the fear and greed index score for the Chinese market.
    
    Args:
        score: The calculated index score (0-100)
        
    Returns:
        A string interpretation of the score
    """
    # Adjusted interpretation ranges to match US/EU convention
    if score < 25:
        return "Extreme Fear"
    elif score < 45:
        return "Fear"
    elif score <= 55:
        return "Neutral"
    elif score <= 75:
        return "Greed"
    else:
        return "Extreme Greed"

def get_cn_index() -> Tuple[float, Dict[str, str]]:
    """
    Get the Chinese Fear and Greed Index based on the pre-calculated final score from the API.
    
    Returns:
        A tuple containing:
        - The final index score (0-100) directly from the API's 'Final Index' key.
        - A dictionary of individual indicator results from the API (for reporting).
    """
    try:
        # Fetch market data which includes pre-calculated indicators
        market_data = get_cn_market_data()
        
        # Check if the 'indicators' key exists
        if 'indicators' not in market_data:
            raise ValueError("API response missing 'indicators' key for CN market.")
            
        api_indicators = market_data['indicators']
        
        # --- Get the PRE-CALCULATED Final Score from API --- 
        if 'Final Index' not in api_indicators or 'score' not in api_indicators['Final Index']:
             raise ValueError("API response missing 'Final Index' score for CN market.")
        final_score = api_indicators['Final Index']['score']
        # --- End Final Score Fetch --- 
        
        # Define expected indicator names (matching keys in API response)
        # We still need these to populate the results dictionary for the test harness output
        indicator_map = {
            "Momentum": "Momentum",
            "Volatility": "Volatility",
            "Safe Haven Demand": "Safe Haven Demand",
            "Junk Bond Demand": "Junk Bond Demand",
            "RSI": "RSI",
            "Market Trend": "Market Trend" # Corresponds to MA Deviation locally
        }

        results = {}
        # Populate results dictionary from API indicators (for reporting)
        for local_name, api_name in indicator_map.items():
            if api_name not in api_indicators:
                # If an individual indicator is missing, report it as N/A but don't error
                 # Use default score 50 only if the key is truly absent, otherwise report N/A
                 print(f"Warning: API response missing '{api_name}' indicator for CN market reporting.")
                 results[local_name] = "Score: N/A"
            else:
                 score_val = api_indicators[api_name]
                 results[local_name] = f"Score: {score_val:.2f}"

        # Return the pre-calculated final score and the individual results dict
        return final_score, results
        
    except Exception as e:
        print(f"Error calculating Chinese Fear and Greed Index using API data: {str(e)}")
        # Reraise with a user-friendly message or the original error
        raise ValueError(f"Sorry, cannot calculate Chinese Fear and Greed Index at this time. Issue processing API data: {str(e)}")

# Remove the old calculation function
# def get_cn_index_old(): ... 

# --- Main Execution (Optional) ---
if __name__ == "__main__":
    print("--- Chinese Fear & Greed Index Calculator (using API data) ---")
    
    try:
        final_score, results = get_cn_index()
        interpretation = interpret_score(final_score)
        
        print("\n--------------------------------------------")
        print(f"Final CN Index Score: {final_score:.2f} / 100")
        print(f"Interpretation: {interpretation}")
        print("--------------------------------------------")
        print("Individual Indicator Results (from API):")
        for name, signal in results.items():
            print(f"  {name}: {signal.split(': ')[-1]}") 
            
    except ValueError as e:
        print(f"\n❌ ERROR: {e}")
    except Exception as e:
        import traceback
        print("\n❌ UNEXPECTED ERROR:")
        traceback.print_exc() 