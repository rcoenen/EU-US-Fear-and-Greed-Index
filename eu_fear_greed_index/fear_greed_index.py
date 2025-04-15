import pandas as pd

# Import functions from our indicator modules
from .momentum_indicator import calculate_momentum_score
from .volatility_indicator import calculate_eu_volatility_indicator
from .safe_haven_indicator import calculate_safe_haven_score
from .junk_bond_indicator import calculate_junk_bond_score
from .stock_strength_indicator import calculate_strength_score
from .stock_breadth_indicator import calculate_breadth_score

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

def get_eu_index():
    """Calculates the overall EU Fear & Greed Index based on individual indicators.
    Raises Exception if any indicator calculation fails.
    """
    results = {}
    scores = []
    indicator_functions = {
        "Market Momentum": calculate_momentum_score,
        "Stock Strength": calculate_strength_score,
        "Stock Breadth": calculate_breadth_score,
        "Volatility": calculate_eu_volatility_indicator,  # Using VGK as proxy
        "Safe Haven Demand": calculate_safe_haven_score,
        "Junk Bond Demand": calculate_junk_bond_score
    }

    print("Calculating EU Indicators...")
    # Loop through indicators, calculate, and store results
    # If any calculation fails, the exception will propagate up and stop the index calculation
    for name, func in indicator_functions.items():
        print(f"- Calculating {name}...")
        # All functions now return a single score (0-100)
        score = func()
        scores.append(score)
        results[name] = f"{score:.2f}" # Store the calculated score
        print(f"  - {name} Score: {score:.2f}")

    # --- Calculate final score --- 
    print("\nCalculating Final EU Index Score:")
    print(f"Collected scores: {scores}")

    if scores: # Should always have 6 scores if no exception occurred
        final_index_value = sum(scores) / len(scores)
        print(f"Average score: {final_index_value:.2f} from {len(scores)} valid indicators.")
    else:
        # This case should not be reachable if fail-fast is working
        raise RuntimeError("No indicator scores were collected, but no error was raised.")

    return final_index_value, results

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
    
    final_score, results = get_eu_index()
    interpretation = interpret_score(final_score)
    
    print("\n--------------------------------------------")
    print(f"Final Index Score: {final_score:.2f} / 100")
    print(f"Interpretation: {interpretation}")
    print("--------------------------------------------") 