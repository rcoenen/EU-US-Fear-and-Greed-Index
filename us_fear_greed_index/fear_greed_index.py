import pandas as pd

# Import functions from our US indicator modules
from momentum_indicator import calculate_momentum_signal
from volatility_indicator import calculate_volatility_signal
from safe_haven_indicator import calculate_safe_haven_signal
from junk_bond_indicator import calculate_junk_bond_signal
from stock_strength_indicator import calculate_stock_strength_signal
from stock_breadth_indicator import calculate_stock_breadth_signal
from put_call_indicator import calculate_put_call_proxy_signal

# --- Configuration ---
# Define how signals map to numerical scores (0=Extreme Fear, 50=Neutral, 100=Extreme Greed)
SCORE_MAP = {
    "Fear": 0,
    "Neutral": 50,
    "Greed": 100
}
# Define weights for each indicator (equal weight for 7 indicators)
INDICATOR_WEIGHTS = {
    "Momentum": 1/7,
    "Strength": 1/7,
    "Breadth": 1/7,
    "Put/Call Proxy": 1/7,
    "Volatility": 1/7,
    "Safe Haven": 1/7,
    "Junk Bond": 1/7
}

def get_final_index():
    """Calculates the final US Fear & Greed Index value."""
    indicator_results = {}
    
    print("Calculating US indicators...")
    
    # 1. Market Momentum (S&P 500)
    mom_signal, _, _, _ = calculate_momentum_signal()
    indicator_results["Momentum"] = mom_signal
    print(f"- Momentum: {mom_signal}")

    # 2. Stock Price Strength (Sample)
    str_signal, highs, lows = calculate_stock_strength_signal()
    indicator_results["Strength"] = str_signal
    print(f"- Strength: {str_signal} (Highs: {highs}, Lows: {lows})")

    # 3. Stock Price Breadth (Sample)
    brd_signal, adv_vol, dec_vol = calculate_stock_breadth_signal()
    indicator_results["Breadth"] = brd_signal
    print(f"- Breadth: {brd_signal} (Adv Vol: {adv_vol}, Dec Vol: {dec_vol})")

    # 4. Put/Call Ratio Proxy (VIX Level)
    pc_signal, pc_vix = calculate_put_call_proxy_signal()
    indicator_results["Put/Call Proxy"] = pc_signal
    print(f"- Put/Call Proxy: {pc_signal} (VIX: {pc_vix:.2f})" if pc_vix is not None else f"- Put/Call Proxy: {pc_signal}")
    
    # 5. Market Volatility (VIX vs MA)
    vol_signal, vol_vix = calculate_volatility_signal()
    indicator_results["Volatility"] = vol_signal
    print(f"- Volatility: {vol_signal} (VIX: {vol_vix:.2f})" if vol_vix is not None else f"- Volatility: {vol_signal}")

    # 6. Safe Haven Demand (Stocks vs Bonds)
    sh_signal, stock_ret, bond_ret = calculate_safe_haven_signal()
    indicator_results["Safe Haven"] = sh_signal
    print(f"- Safe Haven: {sh_signal} (Stock: {stock_ret:.2f}%, Bond: {bond_ret:.2f}%)")

    # 7. Junk Bond Demand
    jb_signal, hy_ret, ig_ret = calculate_junk_bond_signal()
    indicator_results["Junk Bond"] = jb_signal
    print(f"- Junk Bond: {jb_signal} (HY: {hy_ret:.2f}%, IG: {ig_ret:.2f}%)")

    # Calculate final score
    total_score = 0
    total_weight = 0
    valid_indicators = 0
    print("\nCalculating US Index Score:")
    for name, signal in indicator_results.items():
        score = SCORE_MAP.get(signal, 50) # Default to Neutral score if unexpected signal
        weight = INDICATOR_WEIGHTS.get(name, 0)
        # Only include indicators that didn't return "Neutral" due to an error (usually)
        # or if they naturally returned Neutral based on data
        # We also check if the weight is defined
        if weight > 0:
            valid_indicators += 1
            total_score += score * weight
            total_weight += weight # Sum actual weights used
            print(f"  - {name}: {signal} -> Score: {score}, Weight: {weight:.3f}")
        else:
             print(f"  - {name}: {signal} -> Skipped (Weight 0 or undefined)")

    # Normalize score based on the sum of weights actually used
    if total_weight > 0:
        # Simple average based on weights used
        final_index_value = total_score / total_weight 
    elif valid_indicators > 0:
        # Fallback: simple average if weights somehow sum to 0 but signals exist
        final_index_value = total_score / valid_indicators 
    else:
        final_index_value = 50 # Default to Neutral if no indicators worked

    return final_index_value, indicator_results

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
    
    final_score, results = get_final_index()
    interpretation = interpret_score(final_score)
    
    print("\n--------------------------------------------")
    print(f"Final US Index Score: {final_score:.2f} / 100")
    print(f"Interpretation: {interpretation}")
    print("--------------------------------------------")
    # print("Individual Indicator Results:")
    # for name, signal in results.items():
    #     print(f"  {name}: {signal}") 