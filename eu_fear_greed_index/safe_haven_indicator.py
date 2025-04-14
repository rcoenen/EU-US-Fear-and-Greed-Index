import yfinance as yf
import pandas as pd

# Configuration
STOCK_INDEX = "^STOXX50E"
BOND_ETF = "EXHB.DE" # iShares eb.rexx® Government Germany 10.5+yr UCITS ETF (DE)
PERIOD = "20d" # Changed to 20 days to match CNN methodology

def calculate_safe_haven_signal(stock_ticker=STOCK_INDEX, bond_ticker=BOND_ETF, period=PERIOD):
    """
    Calculates the safe haven demand signal by comparing stock and bond returns.
    Returns:
        signal (str): 'Greed' if stocks outperform bonds, 'Fear' otherwise.
        stock_return (float): The calculated stock return.
        bond_return (float): The calculated bond return.
    """
    try:
        # Download data
        stocks_raw = yf.download(stock_ticker, period=period, progress=False, auto_adjust=False)
        bonds_raw = yf.download(bond_ticker, period=period, progress=False, auto_adjust=False)

        if stocks_raw.empty or bonds_raw.empty or 'Close' not in stocks_raw or 'Close' not in bonds_raw:
            print(f"Error: Could not download Close data for {stock_ticker} or {bond_ticker}.")
            return "Neutral", 0.0, 0.0

        # Select 'Close' prices and rename columns
        stocks = stocks_raw[['Close']].rename(columns={'Close': 'Stock'})
        bonds = bonds_raw[['Close']].rename(columns={'Close': 'Bond'})
        
        # Align using merge on the Date index
        combined = pd.merge(stocks, bonds, left_index=True, right_index=True, how='inner') # Inner merge ensures dates exist in both
        
        print("\n--- Debug: Safe Haven Indicator ---") # DEBUG
        print(f"Tickers: {stock_ticker} vs {bond_ticker}") # DEBUG
        print("Combined DataFrame `combined` head after merge:") # DEBUG
        print(combined.head()) # DEBUG
        print(f"Shape: {combined.shape}") # DEBUG
        print("-----------------------------------") # DEBUG

        if combined.empty or len(combined) < 2:
            print("Error: Not enough overlapping data points after alignment (merge).")
            return "Neutral", 0.0, 0.0
            
        # Explicitly get scalar start/end values using .item()
        try:
            stock_start = combined['Stock'].iloc[0].item()
            stock_end = combined['Stock'].iloc[-1].item()
            bond_start = combined['Bond'].iloc[0].item()
            bond_end = combined['Bond'].iloc[-1].item()
        except IndexError:
             print("Error: Could not get start/end values from combined data (IndexError).")
             return "Neutral", 0.0, 0.0
        except AttributeError:
             # Fallback if .item() fails (data might already be scalar?)
             print("Warning: .item() failed, attempting direct access for start/end values.")
             stock_start = combined['Stock'].iloc[0]
             stock_end = combined['Stock'].iloc[-1]
             bond_start = combined['Bond'].iloc[0]
             bond_end = combined['Bond'].iloc[-1]

        # Check for non-numeric types just in case
        if not all(isinstance(x, (int, float)) for x in [stock_start, stock_end, bond_start, bond_end]):
            print("Error: Non-numeric values found after extracting start/end prices.")
            return "Neutral", 0.0, 0.0

        # Calculate percentage returns over the aligned period
        stock_return = (stock_end / stock_start - 1) * 100 if stock_start != 0 else 0
        bond_return = (bond_end / bond_start - 1) * 100 if bond_start != 0 else 0

        # Determine signal
        signal = "Greed" if stock_return > bond_return else "Fear"
        
        return signal, stock_return, bond_return

    except Exception as e:
        print(f"Error calculating safe haven signal: {e}")
        return "Neutral", 0.0, 0.0

# --- Main Execution (for standalone testing) ---
if __name__ == "__main__":
    signal, stock_ret, bond_ret = calculate_safe_haven_signal()
    
    print("--- Safe Haven Demand ---")
    print(f"Period: {PERIOD}")
    print(f"Stock Index ({STOCK_INDEX}) Return: {stock_ret:.2f}%")
    print(f"Bond ETF ({BOND_ETF}) Return: {bond_ret:.2f}%")
    print(f"Signal: {signal}") 