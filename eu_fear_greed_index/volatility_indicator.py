import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

# Configuration
VSTOXX_TICKER = "^V2TX" # Ticker for VSTOXX on Yahoo Finance

def load_vstoxx_data():
    """Loads VSTOXX data using the yfinance library."""
    print(f"Fetching VSTOXX data for ticker {VSTOXX_TICKER}...")
    try:
        # Fetch data for the last ~3 years to ensure enough for calculations
        end_date = datetime.now()
        start_date = end_date - timedelta(days=3*365)
        
        vstoxx = yf.Ticker(VSTOXX_TICKER)
        df = vstoxx.history(start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))

        if df.empty:
            print(f"Error: No data returned for {VSTOXX_TICKER}. Check the ticker symbol or date range.")
            return None

        # --- Data Cleaning & Preparation ---
        # Keep only necessary columns ('Close')
        if 'Close' not in df.columns:
             print(f"Error: Expected column 'Close' not found in yfinance data for {VSTOXX_TICKER}.")
             return None

        df = df[['Close']]

        # Ensure Close is numeric, coercing errors
        df['Close'] = pd.to_numeric(df['Close'], errors='coerce')
        df.dropna(subset=['Close'], inplace=True)

        # Index is already datetime from yfinance
        
        print(f"Successfully fetched {len(df)} data points for {VSTOXX_TICKER}.")
        return df

    except Exception as e:
        print(f"Error fetching or processing VSTOXX data for {VSTOXX_TICKER} using yfinance: {e}")
        return None

# --- Remove the old main execution block ---
# (The code below this comment in the original file will be removed)
# Removed the main execution block that previously loaded from CSV and printed stats. 