from typing import Dict, Any
from .base_indicator import BaseIndicator

class SafeHavenIndicator(BaseIndicator):
    """
    Calculates safe haven demand based on gold and bond prices.
    Higher safe haven demand = lower score (fear)
    Lower safe haven demand = higher score (greed)
    """
    
    def __init__(self, market: str):
        """
        Initialize the safe haven indicator for a specific market.
        
        Args:
            market: One of 'us', 'eu', or 'cn'
        """
        self.market = market
        # Map tickers used for calculation based on market availability in API
        self.safe_haven_map = {
            'us': {
                'gold': 'GC=F',
                'bonds': ['^TNX', '^TYX']  # US Treasury yields
            },
            'eu': {
                'gold': 'GC=F',
                'bonds': ['^TNX', 'EXVM.DE']  # US Treasury yield and German govt bonds
            },
            'cn': {
                'gold_usd': 'GC=F', # Gold in USD
                'bonds': ['^TNX'],  # Use US 10Y Treasury as proxy, available in cn.safe_haven
                'currency': 'USDCNY=X',  # USD/CNY exchange rate
                'index': '^HSI'  # Hang Seng Index (proxy for risk appetite)
            }
        }
    
    def calculate(self, market_data: Dict[str, Any]) -> float:
        """
        Calculate safe haven demand score based on gold and bond prices/yields.
        Higher values (closer to 100) indicate GREED (low safe haven demand).
        Lower values (closer to 0) indicate FEAR (high safe haven demand).
        
        Args:
            market_data: Dictionary containing market data FOR THE SPECIFIC market (e.g., data under the 'eu' key)
            
        Returns:
            A score between 0 and 100 representing the greed/fear level derived from safe haven assets.
        """
        try:
            # Get safe haven data - expected directly within the passed market_data dict
            safe_haven_data = market_data.get('safe_haven', {})
            
            if not safe_haven_data:
                 raise ValueError(f"'safe_haven' key missing or empty in the provided market_data for {self.market}")

            bond_tickers = self.safe_haven_map[self.market].get('bonds', [])
            # --- Default Component Scores (Neutral = 50) ---
            gold_greed_score = 50.0 
            avg_bond_greed_score = 50.0 

            # --- Calculate Bond Greed Score --- 
            # Higher yield momentum (prices falling) -> less safe haven demand -> higher greed score.
            bond_scores = []
            for bond_ticker in bond_tickers:
                bond_data = safe_haven_data.get(bond_ticker, {})
                if bond_data and bond_data.get('momentum') is not None:
                    bond_momentum = bond_data['momentum']
                    # Increase sensitivity
                    bond_greed_component_score = 50.0 + (bond_momentum * 4.0) 
                    bond_scores.append(bond_greed_component_score)
                else:
                    print(f"Warning: Missing data or momentum for bond {bond_ticker} in {self.market}.safe_haven")

            if bond_scores:
                avg_bond_greed_score = sum(bond_scores) / len(bond_scores)
            else:
                print(f"Warning: No valid bond scores calculated for {self.market}. Using default.")

            # --- Calculate Gold Greed Score (Market Specific) --- 
            # Higher gold price momentum -> more safe haven demand -> lower greed score.
            if self.market == 'cn':
                gold_usd_ticker = self.safe_haven_map[self.market].get('gold_usd')
                if not gold_usd_ticker: raise ValueError("Config error: missing 'gold_usd' for cn")
                gold_usd_data = safe_haven_data.get(gold_usd_ticker, {})
                if not gold_usd_data or gold_usd_data.get('momentum') is None:
                    print(f"Warning: Missing data/momentum for gold {gold_usd_ticker} (CN proxy) in {self.market}.safe_haven")                    
                else:
                    gold_usd_momentum = gold_usd_data['momentum']
                    # Increase sensitivity
                    gold_greed_score = 50.0 - (gold_usd_momentum * 4.0) 
                
            else: # For US and EU
                gold_ticker = self.safe_haven_map[self.market].get('gold')
                if not gold_ticker: raise ValueError(f"Config error: missing 'gold' for {self.market}")
                gold_data = safe_haven_data.get(gold_ticker, {})
                if gold_data and gold_data.get('momentum') is not None:
                    gold_momentum = gold_data['momentum']
                     # Increase sensitivity
                    gold_greed_score = 50.0 - (gold_momentum * 4.0) 
                else:
                    print(f"Warning: Missing data or momentum for gold {gold_ticker} in {self.market}.safe_haven")
            
            # --- Combine Scores (Market Specific) --- 
            if self.market == 'cn':
                 # --- CN Specific Components --- 
                 # Currency Score: Higher USDCNY momentum (weaker CNY) -> more fear -> lower greed score
                currency_ticker = self.safe_haven_map[self.market].get('currency')
                currency_data = safe_haven_data.get(currency_ticker, {})
                currency_greed_score = 50.0 # Default
                if currency_data and currency_data.get('momentum') is not None:
                    currency_momentum = currency_data.get('momentum', 0)
                     # Increase sensitivity
                    currency_greed_score = 50.0 - (currency_momentum * 4.0) 
                else:
                     print(f"Warning: Missing data or momentum for currency {currency_ticker} in {self.market}.safe_haven")
                
                # Index Score: Higher index momentum (risk-on) -> less fear -> higher greed score
                index_ticker = self.safe_haven_map[self.market].get('index')
                index_data = market_data.get('indices', {}).get(index_ticker) or market_data.get('index', {}).get(index_ticker, {})
                index_greed_score = 50.0 # Default
                if index_data and index_data.get('momentum') is not None:
                     index_momentum = index_data.get('momentum', 0)
                      # Increase sensitivity slightly (index moves less than others)
                     index_greed_score = 50.0 + (index_momentum * 2.0) 
                else:
                    if not (market_data.get('indices', {}).get(index_ticker) or market_data.get('index', {}).get(index_ticker, {})):
                         print(f"Warning: Missing data or momentum for index {index_ticker} in {self.market} indices/index")

                # Combine CN scores with weights: Gold 30%, Bonds 30%, Currency 20%, Index 20%
                # The result is the final Greed score for this indicator
                final_safe_haven_score = (gold_greed_score * 0.3 + 
                                         avg_bond_greed_score * 0.3 + 
                                         currency_greed_score * 0.2 + 
                                         index_greed_score * 0.2)
                
            else: # For US and EU markets
                # Combine gold and bond scores (50/50 weight)
                # The result is the final Greed score for this indicator
                final_safe_haven_score = (gold_greed_score + avg_bond_greed_score) / 2
            
            # Ensure final score is within bounds [0, 100]
            return max(0.0, min(100.0, final_safe_haven_score)) 
            
        except KeyError as e:
             raise ValueError(f"Configuration Error in SafeHavenIndicator for {self.market}: Missing key {e}")
        except ValueError as e:
            print(f"Data Error calculating safe haven score for {self.market}: {str(e)}")
            raise e
        except Exception as e:
            print(f"Unexpected error calculating safe haven score for {self.market}: {str(e)}")
            raise ValueError(f"Could not calculate safe haven score for {self.market} due to an unexpected error: {e}") 