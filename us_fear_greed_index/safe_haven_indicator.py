import yfinance as yf
import pandas as pd
import numpy as np

# Configuration
STOCK_INDEX = "^GSPC" # Changed to S&P 500
BOND_ETF = "IEF" # Changed to iShares 7-10 Year Treasury Bond ETF
PERIOD = "20d" # Changed to 20 days to match CNN description

def calculate_safe_haven_score(stock_ticker=STOCK_INDEX, bond_ticker=BOND_ETF, period=PERIOD):
    """
    Calculates the safe haven demand signal by comparing stock and bond returns.
    Returns:
        score (float): The calculated safe haven score.
    """
    try:
        # Download data
        stocks_raw = yf.download(stock_ticker, period=period, progress=False, auto_adjust=False)
        bonds_raw = yf.download(bond_ticker, period=period, progress=False, auto_adjust=False)

        if stocks_raw.empty or bonds_raw.empty or 'Close' not in stocks_raw or 'Close' not in bonds_raw:
            print(f"Error: Could not download Close data for {stock_ticker} or {bond_ticker}.")
            return 0.0

        # Select 'Close' prices and rename columns
        stocks = stocks_raw[['Close']].rename(columns={'Close': 'Stock'})
        bonds = bonds_raw[['Close']].rename(columns={'Close': 'Bond'})
        
        # Align using merge on the Date index
        combined = pd.merge(stocks, bonds, left_index=True, right_index=True, how='inner') # Inner merge ensures dates exist in both
        
        # --- Debug --- Keep or remove
        # print("\n--- Debug: Safe Haven Indicator (US) ---") 
        # print(f"Tickers: {stock_ticker} vs {bond_ticker}") 
        # print("Combined DataFrame `combined` head after merge:") 
        # print(combined.head())
        # print(f"Shape: {combined.shape}") 
        # print("-----------------------------------") 
        # --- End Debug ---

        if combined.empty or len(combined) < 2:
            print("Error: Not enough overlapping data points after alignment (merge).")
            return 0.0
            
        # Explicitly get scalar start/end values using .item()
        try:
            stock_start = combined['Stock'].iloc[0].item()
            stock_end = combined['Stock'].iloc[-1].item()
            bond_start = combined['Bond'].iloc[0].item()
            bond_end = combined['Bond'].iloc[-1].item()
        except IndexError:
             print("Error: Could not get start/end values from combined data (IndexError).")
             return 0.0
        except AttributeError:
             print("Warning: .item() failed, attempting direct access for start/end values.")
             stock_start = combined['Stock'].iloc[0]
             stock_end = combined['Stock'].iloc[-1]
             bond_start = combined['Bond'].iloc[0]
             bond_end = combined['Bond'].iloc[-1]

        # Check for non-numeric types just in case
        if not all(isinstance(x, (int, float)) for x in [stock_start, stock_end, bond_start, bond_end]):
            print("Error: Non-numeric values found after extracting start/end prices.")
            return 0.0

        # Calculate percentage returns over the aligned period
        stock_return = (stock_end / stock_start - 1) * 100 if stock_start != 0 else 0
        bond_return = (bond_end / bond_start - 1) * 100 if bond_start != 0 else 0

        # Calculate score based on the difference, scaled to 0-100
        # Use sigmoid function for smoother scaling of extreme values
        max_diff_scale = 5.0 
        difference = stock_return - bond_return
        
        # Sigmoid transformation for smoother scaling
        normalized_diff = difference / max_diff_scale
        sigmoid = 1 / (1 + np.exp(-normalized_diff))
        score = sigmoid * 100
        
        # Ensure minimum score is 5 and maximum is 95 to avoid extreme values
        score = max(5, min(95, score))

        print(f"Safe Haven: Stock Ret={stock_return:.2f}%, Bond Ret={bond_return:.2f}%, Diff={difference:.2f}%, Score={score:.2f}")
        return score

    except Exception as e:
        print(f"Error calculating safe haven signal: {e}")
        # Raise error instead of returning default
        raise ValueError("Error calculating US safe haven score.")

# --- Main Execution (for standalone testing) ---
if __name__ == "__main__":
    score = calculate_safe_haven_score()
    
    print("--- US Safe Haven Demand ---")
    print(f"Period: {PERIOD}")
    # Stock/bond returns calculated internally
    print(f"Calculated Score: {score:.2f}") 