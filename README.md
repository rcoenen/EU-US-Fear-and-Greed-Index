# Global Fear & Greed Index Dashboard

![Dashboard Screenshot](static/img/screenshot_updated.png)

A real-time dashboard that calculates and displays Fear & Greed Index values for **Chinese (CN)**, European (EU), and US markets, using a custom, unified implementation based on multiple market indicators.

# CN, EU & US Fear & Greed Indices (Open Source)

## Motivation

In an era marked by significant geopolitical events and policy shifts, understanding the *relative* impact on major economies like China, the US, and the EU is crucial. Market sentiment can be heavily influenced by these factors, often in divergent ways.

This project was initiated to develop a tool that allows for a direct, data-driven comparison of market sentiment (Fear vs. Greed) between the CN, US, and EU. By using consistent, open-source methodologies for all indices, we aim to provide insights into questions like:

*   How are specific events or policies perceived differently by CN, US, vs. EU markets?
*   Which economy\'s market sentiment appears more resilient or volatile in the face of global uncertainty?
*   What are the key differences in fear and greed drivers between these major markets?

## Project Goal

This project implements comparable Fear & Greed Index calculations for the Chinese (CN), European Union (EU), and United States (US) markets, relying primarily on data fetched via a dedicated API (which uses `yfinance` as a source).

The primary goal is to create a **consistent and comparable** set of sentiment indicators for the CN, EU, and US markets using transparent, open methodologies.

## Key Features

- **Real-time Data**: Calculations use live market data fetched via API.
- **Unified Methodology**: Consistent indicators and calculations applied across all three regions for comparability.
- **Indicator Suite**: Utilizes a suite of 6 indicators covering momentum, volatility, safe havens, bond spreads, RSI, and market trend.

## Calculation Methodology

All three indices use the same unified methodology for comparability:

### Component Metrics
Each metric is normalized to a 0-100 scale where:
- 0 represents Extreme Fear
- 100 represents Extreme Greed

### Common Metrics Used:
- **Momentum**: Average momentum across indices (-20% to +20% range) (high = greed, low = fear)
- **Volatility**: Current market volatility (high = fear, low = greed)
- **RSI**: Average RSI of major indices (30-70 range) (high = greed, low = fear)
- **Safe Haven Demand**: Inverted RSI of safe-haven assets (high = fear)
- **Market Trend**: Moving average deviation (-10% to +10% range) (high deviation = greed, low deviation = fear)
- **Junk Bond Demand**: Measures investor appetite for higher risk (high demand = greed, low demand = fear).

### Index Categories
The final numerical scores map to these sentiment categories:
- 0-24: Extreme Fear
- 25-44: Fear
- 45-54: Neutral
- 55-74: Greed
- 75-100: Extreme Greed

Note: Not all metrics are available for all regions. The final score is the average of all available metrics.

## How to Run

1.  **Setup Environment:**
    ```bash
    # Create a virtual environment (optional but recommended)
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\\Scripts\\activate`

    # Install dependencies
    pip install -r requirements.txt
    ```

2.  **Run the Dashboard:**
    ```bash
    streamlit run dashboard.py
    ```
    Access the dashboard via the URL provided in your terminal. The dashboard uses the default API endpoint (`https://fear-and-greed-index-cf45c36c07dc.herokuapp.com/api/v1/data`).

3.  **Run Tests:**
    ```bash
    # Run the test harness to verify calculations
    python3 test_harness.py

    # Optionally specify a different API endpoint for testing
    # python3 test_harness.py --endpoint <your_test_api_url>
    ```

## Dependencies

- Python 3.9+
- streamlit
- pandas
- numpy
- matplotlib
- plotly
- requests
- python-dotenv

This README provides a high-level overview. For detailed calculation logic, please refer to the source code within the `cn_fear_greed_index`, `eu_fear_greed_index`, `us_fear_greed_index`, and `indicators` directories. The `utils` directory contains shared utilities like the API client and reporting functions. 