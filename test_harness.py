# test_harness.py
import sys
import os
import traceback

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
    print("\n--- Running EU Index Calculation ---")
    try:
        eu_final_score, eu_results = get_eu_index()
        eu_interpretation = interpret_eu_score(eu_final_score)
        
        print("\n---------------- EU RESULTS ----------------")
        print(f"Final EU Index Score: {eu_final_score:.2f} / 100")
        print(f"Interpretation: {eu_interpretation}")
        print("--------------------------------------------")
        print("Individual Indicator Results:")
        for name, result_str in eu_results.items():
            # Result is now the score string
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
        print(f"Final US Index Score: {us_final_score:.2f} / 100")
        print(f"Interpretation: {us_interpretation}")
        print("--------------------------------------------")
        print("Individual Indicator Results:")
        # US results should now also be score strings
        for name, result_val in us_results.items(): 
            print(f"  - {name}: {result_val}")
        print("--------------------------------------------")

    except Exception as e:
        print(f"\n❌❌❌ ERROR during US Index Calculation ❌❌❌")
        traceback.print_exc()
        print("--------------------------------------------")

    print("\n--- Test Harness Finished ---")

if __name__ == "__main__":
    main() 