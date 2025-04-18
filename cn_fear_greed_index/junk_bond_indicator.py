import numpy as np
from typing import Dict, Any

def calculate_junk_bond(market_data: Dict[str, Any]) -> float:
    """
    Calculate the junk bond demand indicator for the Chinese market.
    This indicator measures the appetite for high-yield vs. investment-grade bonds.
    
    A higher score indicates investors are taking more risk (greed),
    while a lower score indicates flight to safety (fear).
    
    Args:
        market_data: Dictionary containing market data from the API
        
    Returns:
        A score between 0 and 100
    """
    try:
        # Get relevant data
        bonds = market_data.get('bonds', {})
        
        # Check for high yield and investment grade bond data
        # Typical Chinese high yield bonds vs investment grade bonds
        hy_bond_id = 'CNYH'  # Chinese High Yield Bond index identifier
        ig_bond_id = 'CNYC'  # Chinese Investment Grade Bond index identifier
        
        if hy_bond_id in bonds and ig_bond_id in bonds:
            hy_bond = bonds[hy_bond_id]
            ig_bond = bonds[ig_bond_id]
            
            # Get the price change percentages
            hy_change = hy_bond.get('price_change_pct', 0)
            ig_change = ig_bond.get('price_change_pct', 0)
            
            # Calculate the spread between high yield and investment grade returns
            # Positive spread (HY outperforming IG) indicates risk appetite (greed)
            # Negative spread (IG outperforming HY) indicates risk aversion (fear)
            spread = hy_change - ig_change
            
            # Convert spread to score (0-100)
            # Typically, spreads range from -5% to +5% in normal markets
            # Map this range to 0-100 score
            score = 50 + (spread * 10)  # 10x multiplier to scale the spread
            
            # Ensure score is within bounds
            score = min(100, max(0, score))
            
            print(f"Junk Bond: HY Ret={hy_change:.2%}, IG Ret={ig_change:.2%}, Score={score:.2f}")
            return float(score)
        else:
            # If we don't have the specific Chinese bond data, estimate based on
            # US/global bond trends from market_data if available
            global_bonds = market_data.get('global_bonds', {})
            if 'HYG' in global_bonds and 'LQD' in global_bonds:
                # Use US ETFs as proxy if CN-specific data not available
                hyg = global_bonds['HYG']
                lqd = global_bonds['LQD']
                
                hy_change = hyg.get('price_change_pct', 0)
                ig_change = lqd.get('price_change_pct', 0)
                
                spread = hy_change - ig_change
                score = 50 + (spread * 10)
                score = min(100, max(0, score))
                
                print(f"Junk Bond (using global proxies): HY Ret={hy_change:.2%}, IG Ret={ig_change:.2%}, Score={score:.2f}")
                return float(score)
            
            # If all else fails, use a neutral score
            return 50.0
        
    except Exception as e:
        print(f"Error calculating CN junk bond demand: {str(e)}")
        return 50.0  # Return neutral score on error 