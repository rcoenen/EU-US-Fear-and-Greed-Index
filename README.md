# EU & US Fear & Greed Indices (Open Source)

## Motivation

In an era marked by significant geopolitical events and policy shifts, such as trade disputes and evolving global economic relationships, understanding the *relative* impact on major economies like the US and the EU is crucial. Market sentiment can be heavily influenced by these factors, often in divergent ways.

This project was initiated to develop a tool that allows for a direct, data-driven comparison of market sentiment (Fear vs. Greed) between the US and EU. By using consistent, open-source methodologies for both indices, we aim to provide insights into questions like:

*   How are specific events or policies perceived differently by US vs. EU markets?
*   Which economy's market sentiment appears more resilient or volatile in the face of global uncertainty?
*   What are the key differences in fear and greed drivers between these major markets?

## Project Goal

This project implements comparable Fear & Greed Index calculations for both the European Union (EU) and United States (US) markets, relying exclusively on publicly available, open-source data (primarily via the `yfinance` library).

The primary goal is to create a **consistent and comparable** set of sentiment indicators for the EU and US markets using transparent, open methodologies. While inspired by CNN's Fear & Greed Index, our approach focuses on creating equivalent metrics that work for both markets using only openly available data.

## Key Features

- **Real-time Data**: All calculations use live market data from `yfinance`
- **Balanced Scoring**: Carefully calibrated scoring mechanisms ensure fair comparison between EU and US markets
- **Aggressive Fear Detection**: Enhanced sensitivity to market stress signals
- **Volume-Weighted Metrics**: Most indicators use volume data to weight their calculations
- **Smart Data Approximation**: Where exact equivalents aren't available (e.g., VSTOXX), we use carefully chosen proxies

## Calculation Methodology

Both indices use six key indicators, each designed to capture different aspects of market sentiment:

1. **Market Momentum** (20% weight)
   - US: S&P 500 vs moving average
   - EU: EURO STOXX 50 (^STOXX50E) vs 90-day MA
   - Includes volatility-adjusted momentum detection
   - Enhanced sensitivity to downward trends

2. **Stock Strength** (20% weight)
   - Volume-weighted analysis of stocks near highs vs lows
   - Uses representative samples of 30 major stocks for each market
   - Enhanced sensitivity to downward movements

3. **Stock Breadth** (20% weight)
   - Advanced volume-weighted calculation of advancing vs declining stocks
   - Incorporates momentum detection and trend analysis
   - Uses aggressive fear multipliers during market stress

4. **Volatility** (20% weight)
   - US: Direct VIX data
   - EU: Calculated using VGK ETF as VSTOXX proxy
   - Percentile-based scoring against 1-year history

5. **Safe Haven Demand** (10% weight)
   - Compares stock performance vs government bonds
   - Uses market-appropriate bond ETFs for each region

6. **Junk Bond Demand** (10% weight)
   - Analyzes spread between high-yield and investment-grade bonds
   - Uses equivalent ETF pairs for both markets

## Data Approximations & Methodology Notes

Important considerations about our approach:

1. **VSTOXX Approximation**
   - Cannot access VSTOXX directly through `yfinance`
   - Use VGK ETF volatility as proxy
   - Validated against historical VSTOXX patterns

2. **Sample-Based Calculations**
   - Use carefully selected samples of 30 major stocks for each market
   - Ensures consistent comparison between regions
   - Regular validation of sample representativeness

3. **Fear Bias**
   - Implemented stronger sensitivity to fear signals
   - US calculation tuned for more aggressive fear detection
   - EU calculation maintains balanced sensitivity

4. **Score Interpretation**
   - 0-25: Extreme Fear
   - 26-45: Fear
   - 46-55: Neutral
   - 56-75: Greed
   - 76-100: Extreme Greed

## Recent Improvements

- Enhanced fear detection sensitivity in stock breadth calculations
- Implemented volume-weighted scoring across all applicable indicators
- Added ultra-sensitive momentum detection
- Improved score normalization for better EU-US comparison
- Streamlined UI with integer-only score display
- Enhanced error handling and data validation

## How to Run

1. **Setup Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```

2. **Run the Dashboard:**
   ```bash
   streamlit run dashboard.py
   ```
   Access the dashboard via the URL provided in your terminal.

3. **Run Tests:**
   ```bash
   python test_harness.py
   ```

## Dependencies

- Python 3.8+
- yfinance
- pandas
- numpy
- streamlit
- matplotlib

This README provides a high-level overview. For detailed calculation logic, please refer to the source code within the `eu_fear_greed_index` and `us_fear_greed_index` directories. 