import yfinance as yf
import pandas as pd

# Configuration
HIGH_YIELD_ETF = "HYG" # Changed to iShares iBoxx $ High Yield Corporate Bond ETF
INVESTMENT_GRADE_ETF = "LQD" # Changed to iShares iBoxx $ Investment Grade Corporate Bond ETF
PERIOD = "1mo" # Lookback period for comparison

def calculate_junk_bond_signal(high_yield_ticker=HIGH_YIELD_ETF, 
                                investment_grade_ticker=INVESTMENT_GRADE_ETF, 
                                period=PERIOD):
    """
    Calculates the junk bond demand signal by comparing their relative performance.
    Returns:
        signal (str): 'Greed' if high yield outperforms, 'Fear' otherwise.
        hy_return (float): High yield bond return.
        ig_return (float): Investment grade bond return.
    """
    try:
        # Download data
        hy_bonds_raw = yf.download(high_yield_ticker, period=period, progress=False, auto_adjust=False)
        ig_bonds_raw = yf.download(investment_grade_ticker, period=period, progress=False, auto_adjust=False)

        if hy_bonds_raw.empty or ig_bonds_raw.empty or 'Close' not in hy_bonds_raw or 'Close' not in ig_bonds_raw:
            print(f"Error: Could not download Close data for {high_yield_ticker} or {investment_grade_ticker}.")
            return "Neutral", 0.0, 0.0

        # Select 'Close' prices and rename
        hy_bonds = hy_bonds_raw[['Close']].rename(columns={'Close': 'HY'})
        ig_bonds = ig_bonds_raw[['Close']].rename(columns={'Close': 'IG'})

        # Align using merge on the Date index
        combined = pd.merge(hy_bonds, ig_bonds, left_index=True, right_index=True, how='inner')
        
        # --- Debug --- Keep or remove
        # print("\n--- Debug: Junk Bond Indicator (US) ---")
        # print(f"Tickers: {high_yield_ticker} vs {investment_grade_ticker}") 
        # print("Combined DataFrame `combined` head after merge:") 
        # print(combined.head())
        # print(f"Shape: {combined.shape}") 
        # print("-----------------------------------") 
        # --- End Debug --- 

        if combined.empty or len(combined) < 2:
            print("Error: Not enough overlapping data points after alignment (merge).")
            return "Neutral", 0.0, 0.0
            
        # Explicitly get scalar start/end values using .item()
        try:
            hy_start = combined['HY'].iloc[0].item()
            hy_end = combined['HY'].iloc[-1].item()
            ig_start = combined['IG'].iloc[0].item()
            ig_end = combined['IG'].iloc[-1].item()
        except IndexError:
             print("Error: Could not get start/end values from combined bond data (IndexError).")
             return "Neutral", 0.0, 0.0
        except AttributeError:
             print("Warning: .item() failed, attempting direct access for bond start/end values.")
             hy_start = combined['HY'].iloc[0]
             hy_end = combined['HY'].iloc[-1]
             ig_start = combined['IG'].iloc[0]
             ig_end = combined['IG'].iloc[-1]

        # Check for non-numeric types
        if not all(isinstance(x, (int, float)) for x in [hy_start, hy_end, ig_start, ig_end]):
            print("Error: Non-numeric values found after extracting bond start/end prices.")
            return "Neutral", 0.0, 0.0
        
        # Calculate percentage returns
        hy_return = (hy_end / hy_start - 1) * 100 if hy_start != 0 else 0
        ig_return = (ig_end / ig_start - 1) * 100 if ig_start != 0 else 0

        # Determine signal (higher junk bond return suggests more risk appetite)
        signal = "Greed" if hy_return > ig_return else "Fear"
        
        return signal, hy_return, ig_return

    except Exception as e:
        print(f"Error calculating junk bond signal: {e}")
        return "Neutral", 0.0, 0.0

# --- Main Execution (for standalone testing) ---
if __name__ == "__main__":
    signal, hy_ret, ig_ret = calculate_junk_bond_signal()
    
    print("--- US Junk Bond Demand ---")
    print(f"Period: {PERIOD}")
    print(f"High Yield ETF ({HIGH_YIELD_ETF}) Return: {hy_ret:.2f}%")
    print(f"Inv Grade ETF ({INVESTMENT_GRADE_ETF}) Return: {ig_ret:.2f}%")
    print(f"Signal: {signal}") 