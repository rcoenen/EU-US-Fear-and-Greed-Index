import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# API Configuration
API_ENDPOINT = "https://fear-and-greed-index-cf45c36c07dc.herokuapp.com/api/v1/data"

def fetch_market_data():
    """
    Fetches market data from the API endpoint.
    
    Returns:
        dict: The complete market data response from the API.
    Raises:
        ValueError: If the API request fails or returns invalid data.
    """
    try:
        response = requests.get(API_ENDPOINT)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        data = response.json()
        
        if data.get("status") != "online" or "market_data" not in data:
            raise ValueError("API returned invalid or incomplete data")
            
        return data["market_data"]
    except requests.RequestException as e:
        raise ValueError(f"Failed to fetch data from API: {str(e)}")
    except ValueError as e:
        raise e
    except Exception as e:
        raise ValueError(f"Error processing API data: {str(e)}")

def get_eu_market_data():
    """
    Fetches EU market data from the API endpoint.
    
    Returns:
        dict: The EU market data.
    """
    return fetch_market_data().get("eu", {})

def get_us_market_data():
    """
    Fetches US market data from the API endpoint.
    
    Returns:
        dict: The US market data.
    """
    return fetch_market_data().get("us", {})

def get_ticker_data(ticker, region="eu"):
    """
    Gets data for a specific ticker from the API.
    
    Args:
        ticker (str): The ticker symbol to fetch.
        region (str): Either "eu" or "us".
        
    Returns:
        dict: The ticker data.
    Raises:
        ValueError: If the ticker is not found.
    """
    market_data = get_eu_market_data() if region == "eu" else get_us_market_data()
    
    if not market_data:
        raise ValueError(f"No market data available for {region}")
    
    tickers_data = market_data.get("tickers", {})
    
    if ticker not in tickers_data:
        raise ValueError(f"Ticker {ticker} not found in {region} market data")
        
    return tickers_data[ticker]

def simulate_historical_data(ticker_data, days=60):
    """
    Simulates historical price data based on current price and momentum.
    This is needed since the API only provides current snapshots, not historical series.
    
    Args:
        ticker_data (dict): The ticker data from the API.
        days (int): Number of days to simulate.
        
    Returns:
        pd.DataFrame: A DataFrame with simulated historical data.
    """
    current_price = ticker_data.get("current_price")
    if not current_price:
        raise ValueError("No current price available")
        
    # Use momentum to estimate price change over time
    momentum = ticker_data.get("momentum", 0) / 100  # Convert to decimal
    
    # Create date range ending today
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    dates = pd.date_range(start=start_date, end=end_date, periods=days)
    
    # Generate synthetic price series
    # Start from current price and work backwards using momentum
    prices = []
    vol_factor = 0.015  # Volatility factor for random noise
    price = current_price
    
    # Work backwards
    for i in range(days):
        prices.append(price)
        # Apply reverse momentum with some randomness
        random_factor = 1 + np.random.normal(0, vol_factor)
        daily_change = (momentum / days) * random_factor
        price = price / (1 + daily_change)
    
    # Reverse to get chronological order
    prices.reverse()
    
    # Create volume data
    volume = ticker_data.get("volume", 0)
    volumes = [volume * (0.8 + 0.4 * np.random.random()) for _ in range(days)]
    
    # Create DataFrame
    df = pd.DataFrame({
        'Close': prices,
        'Volume': volumes
    }, index=dates)
    
    return df

def get_ticker_historical_data(tickers, region="eu"):
    """
    Gets simulated historical data for multiple tickers.
    
    Args:
        tickers (list): List of ticker symbols.
        region (str): Either "eu" or "us".
        
    Returns:
        dict: Dictionary of DataFrames with ticker data.
    """
    market_data = get_eu_market_data() if region == "eu" else get_us_market_data()
    tickers_data = market_data.get("tickers", {})
    
    result = {}
    for ticker in tickers:
        if ticker in tickers_data:
            try:
                data = simulate_historical_data(tickers_data[ticker])
                result[ticker] = data
            except Exception as e:
                print(f"Warning: Could not simulate data for {ticker}: {str(e)}")
                continue
        else:
            print(f"Warning: No data available for {ticker}")
    
    return result 