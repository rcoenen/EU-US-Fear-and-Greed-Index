from typing import Dict, Any, Tuple
from utils.api_client import get_us_market_data
from indicators.momentum_indicator import MomentumIndicator
from indicators.volatility_indicator import VolatilityIndicator
from indicators.safe_haven_indicator import SafeHavenIndicator
from indicators.junk_bond_indicator import JunkBondIndicator
from indicators.rsi_indicator import RSIIndicator
from indicators.ma_deviation_indicator import MADeviationIndicator

def get_us_index() -> Tuple[float, Dict[str, str]]:
    """
    Calculate the US Fear and Greed Index based on multiple market indicators.
    
    Returns:
        A tuple containing:
        - The final index score (0-100)
        - A dictionary of individual indicator results
    """
    try:
        # Fetch market data
        market_data = get_us_market_data()
        
        # Initialize results dictionary
        results = {}
        
        # Initialize indicators
        momentum = MomentumIndicator('us')
        volatility = VolatilityIndicator('us')
        safe_haven = SafeHavenIndicator('us')
        junk_bond = JunkBondIndicator('us')
        rsi = RSIIndicator('us')
        ma_deviation = MADeviationIndicator('us')
        
        # Calculate individual indicators
        momentum_score = momentum.calculate(market_data)
        results["Market Momentum"] = f"Score: {momentum_score:.2f}"
        
        volatility_score = volatility.calculate(market_data)
        results["Price Volatility"] = f"Score: {volatility_score:.2f}"
        
        safe_haven_score = safe_haven.calculate(market_data)
        results["Safe Haven Demand"] = f"Score: {safe_haven_score:.2f}"
        
        junk_bond_score = junk_bond.calculate(market_data)
        results["Bond Spreads"] = f"Score: {junk_bond_score:.2f}"
        
        rsi_score = rsi.calculate(market_data)
        results["RSI"] = f"Score: {rsi_score:.2f}"
        
        ma_deviation_score = ma_deviation.calculate(market_data)
        results["MA Deviation"] = f"Score: {ma_deviation_score:.2f}"
        
        # Calculate final score (equal weights for all indicators)
        final_score = (
            momentum_score +
            volatility_score +
            safe_haven_score +
            junk_bond_score +
            rsi_score +
            ma_deviation_score
        ) / 6
        
        return final_score, results
        
    except Exception as e:
        print(f"Error calculating US Fear and Greed Index: {str(e)}")
        raise ValueError("Sorry, cannot calculate US Fear and Greed Index at this time. Please try again in a few minutes.")

def interpret_score(score):
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

# --- Main Execution ---
if __name__ == "__main__":
    print("--- US Fear & Greed Index Calculator ---")
    
    final_score, results = get_us_index()
    interpretation = interpret_score(final_score)
    
    print("\n--------------------------------------------")
    print(f"Final US Index Score: {final_score:.2f} / 100")
    print(f"Interpretation: {interpretation}")
    print("--------------------------------------------")
    # print("Individual Indicator Results:")
    # for name, signal in results.items():
    #     print(f"  {name}: {signal}") 