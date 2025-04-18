import numpy as np
import pandas as pd
import logging
import os
from typing import Dict, Any, Optional, Tuple
from utils.api_client import get_cn_market_data, get_eu_market_data, get_us_market_data

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define constants for sentiment categories
EXTREME_FEAR_UPPER = 25.0
FEAR_UPPER = 45.0
NEUTRAL_UPPER = 55.0
GREED_UPPER = 75.0
# Above GREED_UPPER is Extreme Greed

def interpret_score(score: float) -> str:
    """Convert a numerical score to a sentiment category"""
    if score <= EXTREME_FEAR_UPPER:
        return "Extreme Fear"
    elif score <= FEAR_UPPER:
        return "Fear"
    elif score <= NEUTRAL_UPPER:
        return "Neutral"
    elif score <= GREED_UPPER:
        return "Greed"
    else:
        return "Extreme Greed"

def calculate_indices() -> Dict[str, Dict[str, Any]]:
    """Calculate fear and greed indices for all markets"""
    try:
        # Fetch market data for all regions
        cn_data = get_cn_market_data()
        eu_data = get_eu_market_data()
        us_data = get_us_market_data()
        
        # Calculate indices
        cn_index = calculate_cn_index(cn_data)
        eu_index = calculate_eu_index(eu_data)
        us_index = calculate_us_index(us_data)
        
        return {
            "cn": cn_index,
            "eu": eu_index,
            "us": us_index
        }
    except Exception as e:
        logger.error(f"Error calculating indices: {e}", exc_info=True)
        return {}

def calculate_cn_index(market_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate Chinese fear and greed index"""
    try:
        logger.info("Calculating CN index...")
        
        # Calculate components
        momentum = calculate_cn_momentum(market_data)
        volatility = calculate_cn_volatility(market_data)
        rsi = calculate_cn_rsi(market_data)
        safe_haven = calculate_cn_safe_haven(market_data)
        market_trend = calculate_cn_market_trend(market_data)
        junk_bond = calculate_cn_junk_bond(market_data)
        
        # Store components
        components = {
            "Market Momentum": momentum,
            "Volatility": volatility,
            "RSI": rsi,
            "Safe Haven Demand": safe_haven,
            "Market Trend": market_trend,
            "Junk Bond Demand": junk_bond
        }
        
        # Calculate final score with equal weights for each component
        component_values = list(components.values())
        score = np.mean(component_values)
        
        # Interpret the score
        interpretation = interpret_score(score)
        
        logger.info(f"CN index calculated: {score:.1f} ({interpretation})")
        
        return {
            "score": float(score),
            "interpretation": interpretation,
            "components": components
        }
    except Exception as e:
        logger.error(f"Error calculating CN index: {e}", exc_info=True)
        return {"score": 50.0, "interpretation": "Neutral", "components": {}}

def calculate_eu_index(market_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate European fear and greed index"""
    try:
        logger.info("Calculating EU index...")
        
        # Calculate components
        momentum = calculate_eu_momentum(market_data)
        volatility = calculate_eu_volatility(market_data)
        rsi = calculate_eu_rsi(market_data)
        safe_haven = calculate_eu_safe_haven(market_data)
        market_trend = calculate_eu_market_trend(market_data)
        junk_bond = calculate_eu_junk_bond(market_data)
        
        # Store components
        components = {
            "Market Momentum": momentum,
            "Volatility": volatility,
            "RSI": rsi,
            "Safe Haven Demand": safe_haven,
            "Market Trend": market_trend,
            "Junk Bond Demand": junk_bond
        }
        
        # Calculate final score with equal weights for each component
        component_values = list(components.values())
        score = np.mean(component_values)
        
        # Interpret the score
        interpretation = interpret_score(score)
        
        logger.info(f"EU index calculated: {score:.1f} ({interpretation})")
        
        return {
            "score": float(score),
            "interpretation": interpretation,
            "components": components
        }
    except Exception as e:
        logger.error(f"Error calculating EU index: {e}", exc_info=True)
        return {"score": 50.0, "interpretation": "Neutral", "components": {}}

def calculate_us_index(market_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate US fear and greed index"""
    try:
        logger.info("Calculating US index...")
        
        # Calculate components
        momentum = calculate_us_momentum(market_data)
        volatility = calculate_us_volatility(market_data)
        rsi = calculate_us_rsi(market_data)
        safe_haven = calculate_us_safe_haven(market_data)
        market_trend = calculate_us_market_trend(market_data)
        junk_bond = calculate_us_junk_bond(market_data)
        
        # Store components
        components = {
            "Market Momentum": momentum,
            "Volatility": volatility,
            "RSI": rsi,
            "Safe Haven Demand": safe_haven,
            "Market Trend": market_trend,
            "Junk Bond Demand": junk_bond
        }
        
        # Calculate final score with equal weights for each component
        component_values = list(components.values())
        score = np.mean(component_values)
        
        # Interpret the score
        interpretation = interpret_score(score)
        
        logger.info(f"US index calculated: {score:.1f} ({interpretation})")
        
        return {
            "score": float(score),
            "interpretation": interpretation,
            "components": components
        }
    except Exception as e:
        logger.error(f"Error calculating US index: {e}", exc_info=True)
        return {"score": 50.0, "interpretation": "Neutral", "components": {}}

# ---------- CHINESE MARKET COMPONENT CALCULATIONS ----------

def calculate_cn_momentum(market_data: Dict[str, Any]) -> float:
    """Calculate market momentum component for Chinese market"""
    try:
        # Get data for Shanghai Composite and CSI 300
        shanghai = market_data.get("indices", {}).get("SSEC", {})
        csi300 = market_data.get("indices", {}).get("CSI300", {})
        
        # Calculate momentum based on 125-day price change
        shanghai_change = shanghai.get("price_change_125d", 0.0)
        csi300_change = csi300.get("price_change_125d", 0.0)
        
        # Average the changes
        avg_change = (shanghai_change + csi300_change) / 2
        
        # Convert to 0-100 score (normalize between -10% and +10%)
        score = 50 + (avg_change * 500)  # 1% change = 5 points
        
        # Clamp to 0-100 range
        return max(0, min(100, score))
    except Exception as e:
        logger.error(f"Error calculating CN momentum: {e}")
        return 50.0

def calculate_cn_volatility(market_data: Dict[str, Any]) -> float:
    """Calculate volatility component for Chinese market"""
    try:
        # Use volatility indicator
        volatility = market_data.get("volatility", {}).get("value", 50.0)
        
        # Convert to 0-100 score (invert since high volatility = fear)
        score = 100 - volatility
        
        return max(0, min(100, score))
    except Exception as e:
        logger.error(f"Error calculating CN volatility: {e}")
        return 50.0

def calculate_cn_rsi(market_data: Dict[str, Any]) -> float:
    """Calculate RSI component for Chinese market"""
    try:
        # Get RSI values from major indices
        shanghai_rsi = market_data.get("indices", {}).get("SSEC", {}).get("rsi", 50.0)
        csi300_rsi = market_data.get("indices", {}).get("CSI300", {}).get("rsi", 50.0)
        
        # Average the RSI values
        avg_rsi = (shanghai_rsi + csi300_rsi) / 2
        
        # Convert RSI (0-100) to fear-greed score (0-100)
        # RSI under 30 is oversold (fear), over 70 is overbought (greed)
        if avg_rsi <= 30:
            score = avg_rsi * (25/30)  # Map 0-30 to 0-25 (extreme fear to fear)
        elif avg_rsi <= 50:
            score = 25 + ((avg_rsi - 30) * (20/20))  # Map 30-50 to 25-45 (fear to neutral)
        elif avg_rsi <= 70:
            score = 55 + ((avg_rsi - 50) * (20/20))  # Map 50-70 to 55-75 (neutral to greed)
        else:
            score = 75 + ((avg_rsi - 70) * (25/30))  # Map 70-100 to 75-100 (greed to extreme greed)
        
        return max(0, min(100, score))
    except Exception as e:
        logger.error(f"Error calculating CN RSI: {e}")
        return 50.0

def calculate_cn_safe_haven(market_data: Dict[str, Any]) -> float:
    """Calculate safe haven demand component for Chinese market"""
    try:
        # Get safe haven data (gold and treasury bonds)
        gold_change = market_data.get("safe_haven", {}).get("gold_price_change", 0.0)
        bond_yield_change = market_data.get("safe_haven", {}).get("treasury_yield_change", 0.0)
        
        # Invert the bond yield change (negative change = higher demand = greed)
        bond_demand = -bond_yield_change
        
        # Combine (positive gold change and negative yield change both indicate safe haven demand)
        safe_haven_demand = (gold_change + bond_demand) / 2
        
        # Convert to 0-100 score (normalize between -1% and +1%)
        score = 50 + (safe_haven_demand * 50)  # 1% change = 50 points
        
        # High demand for safe havens indicates fear (invert the score)
        score = 100 - score
        
        return max(0, min(100, score))
    except Exception as e:
        logger.error(f"Error calculating CN safe haven: {e}")
        return 50.0

def calculate_cn_market_trend(market_data: Dict[str, Any]) -> float:
    """Calculate market trend component for Chinese market"""
    try:
        # Get moving averages for Shanghai Composite and CSI 300
        shanghai = market_data.get("indices", {}).get("SSEC", {})
        csi300 = market_data.get("indices", {}).get("CSI300", {})
        
        # Calculate the difference between current price and 200-day MA
        shanghai_price = shanghai.get("price", 0.0)
        shanghai_ma200 = shanghai.get("ma_200", 0.0)
        shanghai_diff = (shanghai_price / shanghai_ma200 - 1) * 100 if shanghai_ma200 > 0 else 0
        
        csi300_price = csi300.get("price", 0.0)
        csi300_ma200 = csi300.get("ma_200", 0.0)
        csi300_diff = (csi300_price / csi300_ma200 - 1) * 100 if csi300_ma200 > 0 else 0
        
        # Average the differences
        avg_diff = (shanghai_diff + csi300_diff) / 2
        
        # Convert to 0-100 score (normalize between -10% and +10%)
        score = 50 + (avg_diff * 5)  # 1% above/below MA = 5 points
        
        return max(0, min(100, score))
    except Exception as e:
        logger.error(f"Error calculating CN market trend: {e}")
        return 50.0

def calculate_cn_junk_bond(market_data: Dict[str, Any]) -> float:
    """Calculate junk bond demand component for Chinese market"""
    try:
        # Use high-yield corporate bond spreads
        bond_spread = market_data.get("junk_bonds", {}).get("high_yield_spread", 5.0)
        
        # Map spread to score (higher spread = fear, lower spread = greed)
        # Average spread is around 5%, range typically 3-10%
        if bond_spread <= 3:
            score = 85  # Extreme greed (very tight spreads)
        elif bond_spread <= 4:
            score = 70  # Greed
        elif bond_spread <= 6:
            score = 50  # Neutral
        elif bond_spread <= 8:
            score = 30  # Fear
        else:
            score = 15  # Extreme fear (very wide spreads)
        
        return score
    except Exception as e:
        logger.error(f"Error calculating CN junk bond: {e}")
        return 50.0

# ---------- EUROPEAN MARKET COMPONENT CALCULATIONS ----------

def calculate_eu_momentum(market_data: Dict[str, Any]) -> float:
    """Calculate market momentum component for European market"""
    try:
        # Get data for STOXX50E
        stoxx50 = market_data.get("index", {})
        
        # Calculate momentum based on 125-day price change
        price_change = stoxx50.get("price_change_125d", 0.0)
        
        # Convert to 0-100 score (normalize between -10% and +10%)
        score = 50 + (price_change * 500)  # 1% change = 5 points
        
        # Clamp to 0-100 range
        return max(0, min(100, score))
    except Exception as e:
        logger.error(f"Error calculating EU momentum: {e}")
        return 50.0

def calculate_eu_volatility(market_data: Dict[str, Any]) -> float:
    """Calculate volatility component for European market"""
    try:
        # Use VSTOXX or equivalent volatility indicator
        volatility = market_data.get("volatility", {}).get("value", 20.0)
        
        # Map volatility to score (higher volatility = fear)
        # Typical VSTOXX range is 10-40
        vstoxx_range = (10, 40)
        
        # Invert and normalize
        if volatility <= vstoxx_range[0]:
            score = 90  # Very low volatility = extreme greed
        elif volatility >= vstoxx_range[1]:
            score = 10  # Very high volatility = extreme fear
        else:
            # Linear mapping from range to 10-90
            normalized = 1 - ((volatility - vstoxx_range[0]) / (vstoxx_range[1] - vstoxx_range[0]))
            score = 10 + (normalized * 80)
        
        return max(0, min(100, score))
    except Exception as e:
        logger.error(f"Error calculating EU volatility: {e}")
        return 50.0

def calculate_eu_rsi(market_data: Dict[str, Any]) -> float:
    """Calculate RSI component for European market"""
    try:
        # Get RSI value for STOXX50E
        rsi = market_data.get("index", {}).get("rsi", 50.0)
        
        # Convert RSI (0-100) to fear-greed score (0-100)
        # RSI under 30 is oversold (fear), over 70 is overbought (greed)
        if rsi <= 30:
            score = rsi * (25/30)  # Map 0-30 to 0-25 (extreme fear to fear)
        elif rsi <= 50:
            score = 25 + ((rsi - 30) * (20/20))  # Map 30-50 to 25-45 (fear to neutral)
        elif rsi <= 70:
            score = 55 + ((rsi - 50) * (20/20))  # Map 50-70 to 55-75 (neutral to greed)
        else:
            score = 75 + ((rsi - 70) * (25/30))  # Map 70-100 to 75-100 (greed to extreme greed)
        
        return max(0, min(100, score))
    except Exception as e:
        logger.error(f"Error calculating EU RSI: {e}")
        return 50.0

def calculate_eu_safe_haven(market_data: Dict[str, Any]) -> float:
    """Calculate safe haven demand component for European market"""
    try:
        # Get Bund yield change and EUR/USD change
        bund_yield_change = market_data.get("safe_haven", {}).get("bund_yield_change", 0.0)
        eur_usd_change = market_data.get("safe_haven", {}).get("eur_usd_change", 0.0)
        
        # Invert the bond yield change (negative change = higher demand = fear)
        bond_demand = -bund_yield_change
        
        # Positive EUR/USD change indicates strength in EUR (risk-on)
        currency_factor = eur_usd_change
        
        # Combine (negative yield change and negative currency change both indicate safe haven demand)
        safe_haven_demand = (bond_demand - currency_factor) / 2
        
        # Convert to 0-100 score (normalize between -1% and +1%)
        score = 50 + (safe_haven_demand * 50)  # 1% change = 50 points
        
        # High demand for safe havens indicates fear (invert the score)
        score = 100 - score
        
        return max(0, min(100, score))
    except Exception as e:
        logger.error(f"Error calculating EU safe haven: {e}")
        return 50.0

def calculate_eu_market_trend(market_data: Dict[str, Any]) -> float:
    """Calculate market trend component for European market"""
    try:
        # Get moving averages for STOXX50E
        stoxx50 = market_data.get("index", {})
        
        # Calculate the difference between current price and 200-day MA
        price = stoxx50.get("price", 0.0)
        ma200 = stoxx50.get("ma_200", 0.0)
        
        if ma200 > 0:
            price_diff = (price / ma200 - 1) * 100
        else:
            price_diff = 0
        
        # Convert to 0-100 score (normalize between -10% and +10%)
        score = 50 + (price_diff * 5)  # 1% above/below MA = 5 points
        
        return max(0, min(100, score))
    except Exception as e:
        logger.error(f"Error calculating EU market trend: {e}")
        return 50.0

def calculate_eu_junk_bond(market_data: Dict[str, Any]) -> float:
    """Calculate junk bond demand component for European market"""
    try:
        # Use spread between high-yield and investment-grade bonds
        bond_spread = market_data.get("junk_bonds", {}).get("high_yield_spread", 3.5)
        
        # Map spread to score (higher spread = fear, lower spread = greed)
        # European spreads tend to be tighter, typical range 2-7%
        if bond_spread <= 2:
            score = 85  # Extreme greed (very tight spreads)
        elif bond_spread <= 3:
            score = 70  # Greed
        elif bond_spread <= 4:
            score = 50  # Neutral
        elif bond_spread <= 5.5:
            score = 30  # Fear
        else:
            score = 15  # Extreme fear (very wide spreads)
        
        return score
    except Exception as e:
        logger.error(f"Error calculating EU junk bond: {e}")
        return 50.0

# ---------- US MARKET COMPONENT CALCULATIONS ----------

def calculate_us_momentum(market_data: Dict[str, Any]) -> float:
    """Calculate market momentum component for US market"""
    try:
        # Get data for S&P 500
        sp500 = market_data.get("indices", {}).get("SPX", {})
        
        # Calculate momentum based on 125-day price change
        price_change = sp500.get("price_change_125d", 0.0)
        
        # Convert to 0-100 score (normalize between -10% and +10%)
        score = 50 + (price_change * 500)  # 1% change = 5 points
        
        # Clamp to 0-100 range
        return max(0, min(100, score))
    except Exception as e:
        logger.error(f"Error calculating US momentum: {e}")
        return 50.0

def calculate_us_volatility(market_data: Dict[str, Any]) -> float:
    """Calculate volatility component for US market"""
    try:
        # Get VIX value
        vix = market_data.get("volatility", {}).get("VIX", 20.0)
        
        # Map VIX to score (higher VIX = fear)
        # Typical VIX range is 10-40
        vix_range = (10, 40)
        
        # Invert and normalize
        if vix <= vix_range[0]:
            score = 90  # Very low volatility = extreme greed
        elif vix >= vix_range[1]:
            score = 10  # Very high volatility = extreme fear
        else:
            # Linear mapping from range to 10-90
            normalized = 1 - ((vix - vix_range[0]) / (vix_range[1] - vix_range[0]))
            score = 10 + (normalized * 80)
        
        return max(0, min(100, score))
    except Exception as e:
        logger.error(f"Error calculating US volatility: {e}")
        return 50.0

def calculate_us_rsi(market_data: Dict[str, Any]) -> float:
    """Calculate RSI component for US market"""
    try:
        # Get RSI value for S&P 500
        rsi = market_data.get("indices", {}).get("SPX", {}).get("rsi", 50.0)
        
        # Convert RSI (0-100) to fear-greed score (0-100)
        # RSI under 30 is oversold (fear), over 70 is overbought (greed)
        if rsi <= 30:
            score = rsi * (25/30)  # Map 0-30 to 0-25 (extreme fear to fear)
        elif rsi <= 50:
            score = 25 + ((rsi - 30) * (20/20))  # Map 30-50 to 25-45 (fear to neutral)
        elif rsi <= 70:
            score = 55 + ((rsi - 50) * (20/20))  # Map 50-70 to 55-75 (neutral to greed)
        else:
            score = 75 + ((rsi - 70) * (25/30))  # Map 70-100 to 75-100 (greed to extreme greed)
        
        return max(0, min(100, score))
    except Exception as e:
        logger.error(f"Error calculating US RSI: {e}")
        return 50.0

def calculate_us_safe_haven(market_data: Dict[str, Any]) -> float:
    """Calculate safe haven demand component for US market"""
    try:
        # Get Treasury yield and gold price changes
        treasury_yield_change = market_data.get("safe_haven", {}).get("treasury_yield_change", 0.0)
        gold_change = market_data.get("safe_haven", {}).get("gold_price_change", 0.0)
        
        # Invert the bond yield change (negative change = higher demand = fear)
        bond_demand = -treasury_yield_change
        
        # Combine (positive gold change and negative yield change both indicate safe haven demand)
        safe_haven_demand = (gold_change + bond_demand) / 2
        
        # Convert to 0-100 score (normalize between -1% and +1%)
        score = 50 + (safe_haven_demand * 50)  # 1% change = 50 points
        
        # High demand for safe havens indicates fear (invert the score)
        score = 100 - score
        
        return max(0, min(100, score))
    except Exception as e:
        logger.error(f"Error calculating US safe haven: {e}")
        return 50.0

def calculate_us_market_trend(market_data: Dict[str, Any]) -> float:
    """Calculate market trend component for US market"""
    try:
        # Get moving averages for S&P 500
        sp500 = market_data.get("indices", {}).get("SPX", {})
        
        # Calculate the difference between current price and 200-day MA
        price = sp500.get("price", 0.0)
        ma200 = sp500.get("ma_200", 0.0)
        
        if ma200 > 0:
            price_diff = (price / ma200 - 1) * 100
        else:
            price_diff = 0
        
        # Convert to 0-100 score (normalize between -10% and +10%)
        score = 50 + (price_diff * 5)  # 1% above/below MA = 5 points
        
        return max(0, min(100, score))
    except Exception as e:
        logger.error(f"Error calculating US market trend: {e}")
        return 50.0

def calculate_us_junk_bond(market_data: Dict[str, Any]) -> float:
    """Calculate junk bond demand component for US market"""
    try:
        # Use spread between high-yield and investment-grade bonds
        bond_spread = market_data.get("junk_bonds", {}).get("high_yield_spread", 4.0)
        
        # Map spread to score (higher spread = fear, lower spread = greed)
        # US spreads typical range 3-8%
        if bond_spread <= 3:
            score = 85  # Extreme greed (very tight spreads)
        elif bond_spread <= 4:
            score = 70  # Greed
        elif bond_spread <= 5:
            score = 50  # Neutral
        elif bond_spread <= 6.5:
            score = 30  # Fear
        else:
            score = 15  # Extreme fear (very wide spreads)
        
        return score
    except Exception as e:
        logger.error(f"Error calculating US junk bond: {e}")
        return 50.0 