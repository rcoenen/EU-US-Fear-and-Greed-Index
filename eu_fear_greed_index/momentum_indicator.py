import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Configuration
STOCK_INDEX = "^STOXX50E"
MOVING_AVG_DAYS = 125
DATA_PERIOD = "1y"

def calculate_momentum_signal(ticker=STOCK_INDEX, period=DATA_PERIOD, ma_days=MOVING_AVG_DAYS):
    """
    Calculates the market momentum signal for the given ticker.
    Returns:
        signal (str): 'Greed' if price > MA, 'Fear' otherwise.
        latest_close (float): The latest closing price.
        latest_ma (float): The latest moving average value.
        data (pd.DataFrame): DataFrame with price, MA, and signal.
    """
    try:
        # Fetch Data - Set auto_adjust=False
        data = yf.download(ticker, period=period, progress=False, auto_adjust=False)
        if data.empty or 'Close' not in data.columns:
            print(f"Error: Could not download 'Close' data for {ticker}.")
            return "Neutral", None, None, None

        # Extract 'Close' Series, handling potential MultiIndex
        if isinstance(data.columns, pd.MultiIndex):
             close_series = data['Close'] # Access 'Close' level
             if isinstance(close_series, pd.DataFrame): # If still a DataFrame (multiple 'Close' columns?), take first
                 close_series = close_series.iloc[:, 0]
        else:
             close_series = data['Close'] # Simple index
             
        # Create a clean DataFrame
        df = close_series.to_frame(name='Close')

        # Ensure Date index is present (it should be from yfinance)
        if not isinstance(df.index, pd.DatetimeIndex):
             print(f"Warning: Index for {ticker} is not DatetimeIndex. Attempting to convert.")
             try:
                 df.index = pd.to_datetime(df.index)
             except Exception as date_err:
                 print(f"Error: Could not convert index to DatetimeIndex for {ticker}: {date_err}")
                 return "Neutral", None, None, None
        
        # Calculate Moving Average
        df[f'{ma_days}d_ma'] = df['Close'].rolling(ma_days, min_periods=1).mean()

        # Calculate Momentum explicitly
        momentum_values = df['Close'] - df[f'{ma_days}d_ma']
        df['Momentum'] = momentum_values # Assign the calculated Series

        # Determine Signal (handle potential NaN at the start)
        df['Signal'] = np.where(df['Momentum'] > 0, 'Greed', 'Fear')
        df.loc[df['Momentum'].isna(), 'Signal'] = 'Neutral' # Mark initial NaNs as Neutral

        latest_close = df['Close'].iloc[-1]
        latest_ma = df[f'{ma_days}d_ma'].iloc[-1]
        latest_signal = df['Signal'].iloc[-1]

        # Check for NaN in latest MA (can happen if period < ma_days)
        if pd.isna(latest_ma):
             print(f"Warning: Moving average for {ticker} is NaN. Not enough data for {ma_days} days? Setting signal to Neutral.")
             latest_signal = "Neutral"

        return latest_signal, latest_close, latest_ma, df # Return the modified DataFrame

    except Exception as e:
        print(f"Error calculating momentum signal: {e}")
        return "Neutral", None, None, None

# --- Main Execution (for standalone testing & plotting) ---
if __name__ == "__main__":
    signal, close, ma, df = calculate_momentum_signal()
    
    if df is not None:
        print("--- Latest Momentum Data ---")
        # Use f-string for column name consistency
        print(df[['Close', f'{MOVING_AVG_DAYS}d_ma', 'Signal']].tail())

        # Plot
        print("\nPlotting data...")
        df[['Close',f'{MOVING_AVG_DAYS}d_ma']].plot(
            title=f'{STOCK_INDEX} Momentum ({MOVING_AVG_DAYS}-Day MA)',
            figsize=(10,5)
        )
        plt.ylabel("Index Value")
        plt.grid(True)
        plt.show()
        print("Plot displayed.")
    else:
        print("Could not generate momentum data or plot.") 