import yfinance as yf
import pandas as pd

# Use the same tickers as in the stock_breadth_indicator.py
tickers = [
    'ASML.AS', 'SAP.DE', 'ADYEN.AS', 'OR.PA', 'MC.PA', 'AIR.PA', 'SU.PA', 'BNP.PA', 
    'ENEL.MI', 'ISP.MI', 'TTE.PA', 'IBE.MC', 'ITX.MC', 'BAYN.DE', 'IFX.DE', 'SIE.DE', 
    'ALV.DE', 'DTE.DE', 'ADS.DE', 'ABI.BR', 'NOVN.SW', 'NOKIA.HE', 'SAN.PA', 'KER.PA', 
    'FLTR.L', 'STLAM.MI', 'UCG.MI', 'VOW.DE', 'CS.PA', 'PRX.AS'
]

# Download data for the last 5 days
data = yf.download(tickers, period='5d', group_by='ticker')

# Track movements
up_count = 0
down_count = 0
unchanged_count = 0
missing_data = 0

print(f"Checking price changes for {len(tickers)} EU tickers...")
print("-" * 50)

for ticker in tickers:
    if ticker in data:
        ticker_data = data[ticker]
        
        if isinstance(ticker_data, pd.DataFrame) and len(ticker_data) >= 2:
            latest = ticker_data['Close'].iloc[-1]
            prev = ticker_data['Close'].iloc[-2]
            change = (latest - prev) / prev * 100
            
            if change > 0:
                direction = 'UP'
                up_count += 1
            elif change < 0:
                direction = 'DOWN'
                down_count += 1
            else:
                direction = 'UNCHANGED'
                unchanged_count += 1
                
            print(f"{ticker}: {direction} ({change:.2f}%)")
        else:
            print(f"{ticker}: INSUFFICIENT DATA")
            missing_data += 1
    else:
        print(f"{ticker}: NO DATA")
        missing_data += 1

print("-" * 50)
print(f"Summary:")
print(f"UP: {up_count} tickers")
print(f"DOWN: {down_count} tickers")
print(f"UNCHANGED: {unchanged_count} tickers")
print(f"MISSING DATA: {missing_data} tickers")

# Calculate breadth score (for comparison with the original script)
if up_count + down_count > 0:
    breadth_score = (up_count / (up_count + down_count)) * 100
    print(f"Calculated breadth score: {breadth_score:.2f}")
else:
    print("Cannot calculate breadth score (no up/down data)") 