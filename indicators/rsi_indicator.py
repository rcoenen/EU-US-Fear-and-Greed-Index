from typing import Dict, Any
from .base_indicator import BaseIndicator

class RSIIndicator(BaseIndicator):
    """
    Calculates RSI-based score for the market.
    Higher RSI = higher score (greed)
    Lower RSI = lower score (fear)
    """
    
    def __init__(self, market: str):
        """
        Initialize the RSI indicator for a specific market.
        
        Args:
            market: One of 'us', 'eu', or 'cn'
        """
        self.market = market
        self.index_map = {
            'us': ['^GSPC'],  # S&P 500
            'eu': ['^STOXX50E'],  # EURO STOXX 50
            'cn': ['000001.SS', '000300.SS']  # Shanghai Composite and CSI 300
        }
        
        # Define key stocks to monitor for each market
        self.stock_map = {
            'us': ['XLB', 'XLE', 'XLF', 'XLI', 'XLK', 'XLP', 'XLRE', 'XLU', 'XLV', 'XLY'],  # Sector ETFs
            'eu': ['ABI.BR', 'ADS.DE', 'ALV.DE', 'BAYN.DE', 'CS.PA'],
            'cn': ['0700.HK', '1211.HK', '600036.SS', '601318.SS', '601398.SS']
        }
    
    def calculate(self, market_data: Dict[str, Any]) -> float:
        """
        Calculate RSI score based on major indices and key stocks.
        
        Args:
            market_data: Dictionary containing market data from the API
            
        Returns:
            A score between 0 and 100
            
        Raises:
            ValueError: If required index/ticker data or RSI values are missing.
        """
        try:
            # Get indices and tickers data
            indices = market_data.get('indices', {})
            if not indices and self.market == 'eu':
                indices = market_data.get('index', {})
            tickers = market_data.get('tickers', {})
            sector_etfs = market_data.get('sector_etfs', {})
            
            # Collect RSI values
            rsi_values = []
            required_sources_found = 0
            
            # Get RSI from major indices - raise error if index or RSI is missing
            for index_id in self.index_map[self.market]:
                if index_id not in indices:
                    raise ValueError(f"Required index data missing for {index_id} in RSI calculation")
                index_data = indices[index_id]
                if 'rsi' not in index_data:
                    raise ValueError(f"RSI value missing for index {index_id}")
                rsi_values.append(index_data['rsi'])
                required_sources_found += 1
            
            # Get RSI from key stocks/ETFs - raise error if stock or RSI is missing
            for stock_id in self.stock_map[self.market]:
                if self.market == 'us':
                    if stock_id not in sector_etfs:
                        raise ValueError(f"Required sector ETF data missing for {stock_id} in RSI calculation")
                    stock_data = sector_etfs[stock_id]
                else:
                    if stock_id not in tickers:
                        raise ValueError(f"Required ticker data missing for {stock_id} in RSI calculation")
                    stock_data = tickers[stock_id]
                
                if 'rsi' not in stock_data:
                    raise ValueError(f"RSI value missing for stock/ETF {stock_id}")
                rsi_values.append(stock_data['rsi'])
                required_sources_found += 1
            
            # Check if we found any RSI values
            if not rsi_values:
                # This case might be redundant now due to checks above, but good safety net
                raise ValueError(f"No RSI values found for market {self.market}") 
            
            # Calculate average RSI
            avg_rsi = sum(rsi_values) / len(rsi_values)
            
            # Directly map avg_rsi (0-100) to score (0-100)
            score = avg_rsi
            
            return max(0, min(100, score))
            
        except KeyError as e:
            # Re-raise key errors as ValueErrors
            raise ValueError(f"Missing expected key in market data: {e}")
        except Exception as e:
             # Re-raise other exceptions
            # print(f"Unexpected error calculating RSI score for {self.market}: {str(e)}")
            raise e 