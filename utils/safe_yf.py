"""
Safe yfinance utilities with error handling, timeouts, and fallbacks for Streamlit Cloud.
"""
import os
import time
from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf
import streamlit as st

# Configuration
TIMEOUT = 10  # seconds
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds
CACHE_DIR = "data"
CACHE_EXPIRY = 24  # hours

# Streamlit-specific memory cache
@st.cache_data(ttl=3600)  # 1 hour TTL
def _cached_yf_download(ticker, period, interval, timeout, auto_adjust):
    """Streamlit-cached version of yf.download to prevent redundant API calls."""
    return yf.download(
        tickers=ticker,
        period=period,
        interval=interval,
        timeout=timeout,
        progress=False,
        threads=False,  # More reliable on Streamlit Cloud
        auto_adjust=auto_adjust  # Handle the auto_adjust parameter explicitly
    )

def ensure_cache_dir():
    """Ensure the cache directory exists."""
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

def get_cache_path(ticker, period):
    """Get the cache file path for a ticker and period."""
    return os.path.join(CACHE_DIR, f"{ticker}_{period}.csv")

def is_cache_valid(cache_path):
    """Check if cache file exists and is recent enough."""
    if not os.path.exists(cache_path):
        return False
    cache_age = time.time() - os.path.getmtime(cache_path)
    return cache_age < (CACHE_EXPIRY * 3600)  # Convert hours to seconds

def safe_yf_download(ticker, period="1y", interval="1d", fallback_warning=True, auto_adjust=True):
    """
    Safely download data from Yahoo Finance with fallback to cached data.
    
    Args:
        ticker (str): The ticker symbol
        period (str): The data period (e.g., "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max")
        interval (str): The data interval (e.g., "1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo")
        fallback_warning (bool): Whether to show a warning when falling back to cached data
        auto_adjust (bool): Whether to automatically adjust OHLC using adj close
    
    Returns:
        pd.DataFrame: The downloaded data or cached fallback
    """
    ensure_cache_dir()
    cache_path = get_cache_path(ticker, period)
    
    # Try to load from Yahoo Finance with Streamlit caching
    for attempt in range(MAX_RETRIES):
        try:
            df = _cached_yf_download(ticker, period, interval, TIMEOUT, auto_adjust)
            
            if not df.empty:
                # Cache the successful download
                df.to_csv(cache_path)
                return df
                
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
                continue
            break
    
    # If we get here, either all attempts failed or returned empty data
    # Try to load from cache
    if os.path.exists(cache_path):
        if fallback_warning and isinstance(st._get_report_ctx(), type(None)) is False:
            st.warning(f"⚠️ Using cached data for {ticker} (Yahoo Finance request failed)")
        return pd.read_csv(cache_path, index_col=0, parse_dates=True)
    
    raise ValueError(f"Failed to fetch data for {ticker} and no valid cache found")

@st.cache_data(ttl=3600)  # 1 hour TTL
def safe_yf_multiple(tickers, period="1y", interval="1d", auto_adjust=True):
    """
    Safely download data for multiple tickers with individual fallbacks.
    Uses Streamlit caching to prevent redundant API calls.
    
    Args:
        tickers (list): List of ticker symbols
        period (str): The data period
        interval (str): The data interval
        auto_adjust (bool): Whether to automatically adjust OHLC using adj close
    
    Returns:
        dict: Dictionary of DataFrames, one per ticker
    """
    results = {}
    failed_tickers = []
    
    for ticker in tickers:
        try:
            df = safe_yf_download(ticker, period, interval, auto_adjust=auto_adjust)
            if not df.empty:
                results[ticker] = df
            else:
                failed_tickers.append(ticker)
        except Exception as e:
            failed_tickers.append(ticker)
            if isinstance(st._get_report_ctx(), type(None)) is False:
                st.error(f"Failed to fetch {ticker}: {str(e)}")
    
    if failed_tickers and isinstance(st._get_report_ctx(), type(None)) is False:
        st.warning(f"⚠️ Failed to fetch data for: {', '.join(failed_tickers)}")
    
    return results

def initialize_cache(tickers, period="1y", auto_adjust=True):
    """
    Pre-fetch and cache data for a list of tickers.
    Useful for initializing the cache before deploying to Streamlit Cloud.
    
    Args:
        tickers (list): List of ticker symbols
        period (str): The data period to cache
        auto_adjust (bool): Whether to automatically adjust OHLC using adj close
    """
    for ticker in tickers:
        try:
            df = safe_yf_download(ticker, period, auto_adjust=auto_adjust, fallback_warning=False)
            print(f"✓ Cached {ticker}")
        except Exception as e:
            print(f"✗ Failed to cache {ticker}: {str(e)}")

# Example usage in your main code:
"""
from utils.safe_yf import safe_yf_download, safe_yf_multiple

# Single ticker with fallback
try:
    df = safe_yf_download("^STOXX50E", period="6mo", auto_adjust=True)
    if not df.empty:
        # Process data
        pass
except Exception as e:
    st.error(f"Could not fetch STOXX50E data: {e}")

# Multiple tickers with Streamlit caching
tickers = ["^GSPC", "^STOXX50E"]
data = safe_yf_multiple(tickers, period="1y", auto_adjust=True)
for ticker, df in data.items():
    if not df.empty:
        # Process each dataframe
        pass
""" 