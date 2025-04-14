import pandas as pd

# Import functions from our indicator modules
from momentum_indicator import calculate_momentum_signal
from .volatility_indicator import load_vstoxx_data # Now fetches data using yfinance
from safe_haven_indicator import calculate_safe_haven_signal
from junk_bond_indicator import calculate_junk_bond_signal
from stock_strength_indicator import calculate_stock_strength_signal
from stock_breadth_indicator import calculate_stock_breadth_signal

# --- Configuration ---
# VSTOXX_CSV_PATH = "VSTOXX.csv" # Removed CSV path constant
# Define how signals map to numerical scores (0=Extreme Fear, 50=Neutral, 100=Extreme Greed)
SCORE_MAP = {
    "Fear": 0,
    "Neutral": 50,
    "Greed": 100
}
# Define weights for each indicator (equal weight for now)
# Ensure the order matches the `indicators` list below
INDICATOR_WEIGHTS = {
    "Momentum": 1/6,
    "Volatility": 1/6,
    "Safe Haven": 1/6,
    "Junk Bond": 1/6,
    "Strength": 1/6,
    "Breadth": 1/6
}

def calculate_volatility_signal():
    """Calculates the volatility signal based on VSTOXX data fetched via yfinance."""
    vstoxx_data = load_vstoxx_data()
    if vstoxx_data is None or len(vstoxx_data) < 252: # Need 1 year for avg
        print("Warning: Could not calculate VSTOXX signal (data fetch failed or insufficient).")
        return "Neutral", None # Return Neutral if data is unavailable/failed
    
    # Simple signal: Compare latest close to 1-year average
    one_year_avg = vstoxx_data['Close'].rolling(window=252).mean().iloc[-1]
    latest_close = vstoxx_data['Close'].iloc[-1]
    
    # Higher volatility -> Fear
    signal = "Fear" if latest_close > one_year_avg else "Greed"
    return signal, latest_close

def get_final_index():
    """Calculates the final Fear & Greed Index value."""
    indicator_results = {}
    
    print("Calculating indicators...")
    
    # 1. Market Momentum
    mom_signal, _, _, _ = calculate_momentum_signal()
    indicator_results["Momentum"] = mom_signal
    print(f"- Momentum: {mom_signal}")

    # 2. Volatility
    vol_signal, vol_value = calculate_volatility_signal()
    indicator_results["Volatility"] = vol_signal
    print(f"- Volatility (VSTOXX): {vol_signal} (Value: {vol_value:.2f})" if vol_value else f"- Volatility (VSTOXX): {vol_signal}")

    # 3. Safe Haven Demand
    sh_signal, stock_ret, bond_ret = calculate_safe_haven_signal()
    indicator_results["Safe Haven"] = sh_signal
    print(f"- Safe Haven: {sh_signal} (Stock: {stock_ret:.2f}%, Bond: {bond_ret:.2f}%)")

    # 4. Junk Bond Demand
    jb_signal, hy_ret, ig_ret = calculate_junk_bond_signal()
    indicator_results["Junk Bond"] = jb_signal
    print(f"- Junk Bond: {jb_signal} (HY: {hy_ret:.2f}%, IG: {ig_ret:.2f}%)")

    # 5. Stock Price Strength
    str_signal, highs, lows = calculate_stock_strength_signal()
    indicator_results["Strength"] = str_signal
    print(f"- Strength: {str_signal} (Highs: {highs}, Lows: {lows})")

    # 6. Stock Price Breadth
    brd_signal, adv_vol, dec_vol = calculate_stock_breadth_signal()
    indicator_results["Breadth"] = brd_signal
    print(f"- Breadth: {brd_signal} (Adv Vol: {adv_vol}, Dec Vol: {dec_vol})")

    # Calculate final score
    total_score = 0
    total_weight = 0
    print("\nCalculating Index Score:")
    for name, signal in indicator_results.items():
        score = SCORE_MAP.get(signal, 50) # Default to Neutral score if unexpected signal
        weight = INDICATOR_WEIGHTS.get(name, 0)
        if weight > 0: # Only include indicators with weight
            total_score += score * weight
            total_weight += weight
            print(f"  - {name}: {signal} -> Score: {score}, Weight: {weight:.2f}")
        else:
             print(f"  - {name}: {signal} -> Skipped (Weight 0 or undefined)")

    # Normalize score in case total weight is not exactly 1 (e.g., if an indicator failed)
    if total_weight > 0:
        final_index_value = total_score / total_weight
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
    print("--- European Fear & Greed Index Calculator ---")
    
    final_score, results = get_final_index()
    interpretation = interpret_score(final_score)
    
    print("\n--------------------------------------------")
    print(f"Final Index Score: {final_score:.2f} / 100")
    print(f"Interpretation: {interpretation}")
    print("--------------------------------------------") 