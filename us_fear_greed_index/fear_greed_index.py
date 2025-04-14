import pandas as pd

# Import the score-based functions
from .momentum_indicator import calculate_momentum_score
from .stock_strength_indicator import calculate_strength_score
from .stock_breadth_indicator import calculate_breadth_score
from .volatility_indicator import calculate_volatility_signal
from .safe_haven_indicator import calculate_safe_haven_score
from .junk_bond_indicator import calculate_junk_bond_score

# --- Configuration ---
# Tickers for US indicators
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
    """Calculates the overall US Fear & Greed Index based on individual indicators.
    Uses standardized methodology (6 indicators, direct scores, simple average).
    Raises Exception if any indicator calculation fails.
    """
    indicator_results = {}
    scores = [] # Collect numerical scores
    indicator_functions = {
        "Market Momentum": calculate_momentum_score,
        "Stock Strength": calculate_strength_score,
        "Stock Breadth": calculate_breadth_score,
        "Volatility": calculate_volatility_signal, # Function returns (signal, score)
        "Safe Haven Demand": calculate_safe_haven_score,
        "Junk Bond Demand": calculate_junk_bond_score
    }
    
    print("Calculating US indicators...")
    
    # Loop through indicators, get score, store results
    for name, func in indicator_functions.items():
        print(f"- Calculating {name}...")
        if name == "Volatility":
            # Volatility function returns (signal, score)
            _, score = func() # We only need the score for averaging
        else:
            # Other functions return score directly
            score = func()
        scores.append(score)
        indicator_results[name] = f"{score:.2f}" # Store formatted score
        print(f"  - {name} Score: {score:.2f}")
        
    # Calculate final score (simple average)
    print("\nCalculating Final US Index Score:")
    print(f"Collected scores: {scores}")
    if scores:
        final_index_value = sum(scores) / len(scores)
        print(f"Average score: {final_index_value:.2f} from {len(scores)} indicators.")
    else:
        raise RuntimeError("No indicator scores collected for US index.")

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