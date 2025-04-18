import os
import sys
import numpy as np
from typing import Tuple, Dict, Any

# Add the parent directory to the path to import utils
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from utils.api_client import get_cn_market_data
from indicators.momentum_indicator import MomentumIndicator
from indicators.volatility_indicator import VolatilityIndicator
from indicators.safe_haven_indicator import SafeHavenIndicator
from indicators.junk_bond_indicator import JunkBondIndicator
from indicators.rsi_indicator import RSIIndicator
from indicators.ma_deviation_indicator import MADeviationIndicator

def interpret_score(score: float) -> str:
    """
    Interpret the fear and greed index score for the Chinese market.
    
    Args:
        score: The calculated index score (0-100)
        
    Returns:
        A string interpretation of the score
    """
    if score >= 75:
        return "Extreme Greed"
    elif score >= 55:
        return "Greed"
    elif score >= 45:
        return "Neutral"
    elif score >= 25:
        return "Fear"
    else:
        return "Extreme Fear"

def get_cn_index() -> Tuple[float, Dict[str, str]]:
    """
    Calculate the Chinese Fear and Greed Index based on multiple market indicators.
    
    Returns:
        A tuple containing:
        - The final index score (0-100)
        - A dictionary of individual indicator results
    """
    try:
        # Fetch market data
        market_data = get_cn_market_data()
        
        # Initialize results dictionary
        results = {}
        
        # Initialize indicators
        momentum = MomentumIndicator('cn')
        volatility = VolatilityIndicator('cn')
        safe_haven = SafeHavenIndicator('cn')
        junk_bond = JunkBondIndicator('cn')
        rsi = RSIIndicator('cn')
        ma_deviation = MADeviationIndicator('cn')
        
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
        print(f"Error calculating Chinese Fear and Greed Index: {str(e)}")
        raise ValueError("Sorry, cannot calculate Chinese Fear and Greed Index at this time. Please try again in a few minutes.")

def get_cn_index_old() -> Tuple[float, Dict[str, str]]:
    """
    Calculate the Chinese Fear and Greed Index based on multiple market indicators.
    
    Returns:
        A tuple containing:
        - The final index score (0-100)
        - A dictionary of individual indicator results
    """
    try:
        # Fetch market data
        market_data = get_cn_market_data()
        
        # Initialize results dictionary
        results = {}
        
        # Calculate individual indicators
        # Note: These indicator functions will be implemented in separate files
        from stock_strength_indicator import calculate_stock_strength
        from momentum_indicator import calculate_momentum
        from volatility_indicator import calculate_volatility
        from safe_haven_indicator import calculate_safe_haven
        from stock_breadth_indicator import calculate_stock_breadth
        from junk_bond_indicator import calculate_junk_bond
        
        # Stock Strength (16.67%)
        stock_strength_score = calculate_stock_strength(market_data)
        results["Stock Strength"] = f"Score: {stock_strength_score:.2f}"
        
        # Momentum (16.67%) - renamed to Market Momentum for consistency
        momentum_score = calculate_momentum(market_data)
        results["Market Momentum"] = f"Score: {momentum_score:.2f}"
        
        # Volatility (16.67%)
        volatility_score = calculate_volatility(market_data)
        results["Volatility"] = f"Score: {volatility_score:.2f}"
        
        # Safe Haven (16.67%) - renamed to Safe Haven Demand for consistency
        safe_haven_score = calculate_safe_haven(market_data)
        results["Safe Haven Demand"] = f"Score: {safe_haven_score:.2f}"
        
        # Stock Breadth (16.67%)
        stock_breadth_score = calculate_stock_breadth(market_data)
        results["Stock Breadth"] = f"Score: {stock_breadth_score:.2f}"
        
        # Junk Bond Demand (16.67%) - added for consistency with US and EU
        junk_bond_score = calculate_junk_bond(market_data)
        results["Junk Bond Demand"] = f"Score: {junk_bond_score:.2f}"
        
        # Calculate final score (weighted average)
        weights = {
            "Stock Strength": 1/6,
            "Market Momentum": 1/6,
            "Volatility": 1/6,
            "Safe Haven Demand": 1/6,
            "Stock Breadth": 1/6,
            "Junk Bond Demand": 1/6
        }
        
        final_score = (
            stock_strength_score * weights["Stock Strength"] +
            momentum_score * weights["Market Momentum"] +
            volatility_score * weights["Volatility"] +
            safe_haven_score * weights["Safe Haven Demand"] +
            stock_breadth_score * weights["Stock Breadth"] +
            junk_bond_score * weights["Junk Bond Demand"]
        )
        
        # Ensure score is within 0-100 range
        final_score = max(0, min(100, final_score))
        
        return final_score, results
        
    except Exception as e:
        print(f"Error calculating CN Fear and Greed Index: {str(e)}")
        raise 