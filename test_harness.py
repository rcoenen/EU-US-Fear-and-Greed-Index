# test_harness.py
import sys
import os
import traceback
import numpy as np

print("--- Test Harness Initializing ---")

# --- Add subdirectories to path for imports --- 
# This ensures the script can find the modules in the subdirectories
script_dir = os.path.dirname(__file__)
eu_module_path = os.path.abspath(os.path.join(script_dir, 'eu_fear_greed_index'))
us_module_path = os.path.abspath(os.path.join(script_dir, 'us_fear_greed_index'))

if eu_module_path not in sys.path:
    sys.path.insert(0, eu_module_path)
if us_module_path not in sys.path:
    sys.path.insert(0, us_module_path)
    
# Also add the parent directory to resolve intra-package imports if needed
project_root = os.path.abspath(os.path.join(script_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    
print(f"Adjusted sys.path:")
# print(sys.path) # Uncomment for deep debugging

# --- Import calculation functions --- 
try:
    print("Importing EU module functions...")
    # Import the main index function and the interpretation helper
    from eu_fear_greed_index.fear_greed_index import get_eu_index, interpret_score as interpret_eu_score
    print("EU import successful.")
except ImportError as e:
    print(f"❌ Failed to import EU index module: {e}. Ensure 'eu_fear_greed_index' directory and its files exist.")
    sys.exit(1) # Exit if core modules can't be imported

try:
    print("Importing US module functions...")
    # Remember we use get_final_index from the US module
    from us_fear_greed_index.fear_greed_index import get_final_index as get_us_index, interpret_score as interpret_us_score 
    print("US import successful.")
except ImportError as e:
    print(f"❌ Failed to import US index module: {e}. Ensure 'us_fear_greed_index' directory and its files exist.")
    sys.exit(1)

def main():
    eu_final_score = None
    us_final_score = None
    eu_results = {}
    us_results = {}
    
    print("\n--- Running EU Index Calculation ---")
    try:
        eu_final_score, eu_results = get_eu_index()
        eu_interpretation = interpret_eu_score(eu_final_score)
        
        print("\n---------------- EU RESULTS ----------------")
        print(f"Final EU Index Score: {int(round(eu_final_score))} / 100")
        print(f"Interpretation: {eu_interpretation}")
        print("--------------------------------------------")
        print("Individual Indicator Results:")
        for name, result_str in eu_results.items():
            # Keep decimal points for individual indicators
            try:
                score = float(result_str.split(":")[-1].strip())
                print(f"  - {name}: {score:.2f}")
            except (ValueError, IndexError):
                print(f"  - {name}: {result_str}")
        print("--------------------------------------------")
        
    except Exception as e:
        print(f"\n❌❌❌ ERROR during EU Index Calculation ❌❌❌")
        traceback.print_exc()
        print("--------------------------------------------")

    print("\n--- Running US Index Calculation ---")
    try:
        us_final_score, us_results = get_us_index() # Use the imported alias
        us_interpretation = interpret_us_score(us_final_score)
        
        print("\n---------------- US RESULTS ----------------")
        print(f"Final US Index Score: {int(round(us_final_score))} / 100")
        print(f"Interpretation: {us_interpretation}")
        print("--------------------------------------------")
        print("Individual Indicator Results:")
        for name, result_val in us_results.items():
            # Keep decimal points for individual indicators
            try:
                score = float(result_val.split(":")[-1].strip())
                print(f"  - {name}: {score:.2f}")
            except (ValueError, IndexError):
                print(f"  - {name}: {result_val}")
        print("--------------------------------------------")

    except Exception as e:
        print(f"\n❌❌❌ ERROR during US Index Calculation ❌❌❌")
        traceback.print_exc()
        print("--------------------------------------------")

    # Print side-by-side comparison table
    if eu_final_score is not None and us_final_score is not None:
        print("\n---------------- EU vs US COMPARISON ----------------")
        print(f"{'Indicator':<25} {'EU':<10} {'US':<10} {'Difference':<10}")
        print("-" * 60)
        
        # Get all unique indicator names
        all_indicators = set(eu_results.keys()) | set(us_results.keys())
        
        for indicator in sorted(all_indicators):
            eu_score_str = eu_results.get(indicator, "N/A")
            us_score_str = us_results.get(indicator, "N/A")
            
            try:
                eu_score = float(eu_score_str.split(":")[-1].strip()) if eu_score_str != "N/A" else float('nan')
                us_score = float(us_score_str.split(":")[-1].strip()) if us_score_str != "N/A" else float('nan')
                diff = eu_score - us_score if not (np.isnan(eu_score) or np.isnan(us_score)) else float('nan')
                
                # Format with 2 decimal places for indicators
                eu_display = f"{eu_score:.2f}" if not np.isnan(eu_score) else "N/A"
                us_display = f"{us_score:.2f}" if not np.isnan(us_score) else "N/A"
                diff_display = f"{diff:.2f}" if not np.isnan(diff) else "N/A"
                
                print(f"{indicator:<25} {eu_display:<10} {us_display:<10} {diff_display:<10}")
            except (ValueError, IndexError):
                print(f"{indicator:<25} {'N/A':<10} {'N/A':<10} {'N/A':<10}")
        
        print("-" * 60)
        # Round final scores to integers
        print(f"{'Final Score':<25} {int(round(eu_final_score)):<10} {int(round(us_final_score)):<10} {int(round(eu_final_score - us_final_score)):<10}")
        print("--------------------------------------------")

    print("\n--- Test Harness Finished ---")

if __name__ == "__main__":
    main() 