import streamlit as st
import time
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.patheffects as path_effects # Import path effects
import pandas as pd # Keep for data handling
import os
import sys
from datetime import timedelta, datetime, timezone, date
import traceback # Import traceback for printing errors
import logging
import argparse
import re # Import regex module
from dotenv import load_dotenv
from utils.api_client import get_cn_market_data, get_eu_market_data, get_us_market_data, get_daily_summary_data

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('dashboard.log')
    ]
)
logger = logging.getLogger(__name__)

# --- Add subdirectories to path for imports --- 
# This ensures the dashboard can find the modules in the subdirectories
# Note: Having __init__.py files helps, but sometimes explicit path modification is needed depending on execution context.
script_dir = os.path.dirname(__file__)
eu_module_path = os.path.abspath(os.path.join(script_dir, 'eu_fear_greed_index'))
us_module_path = os.path.abspath(os.path.join(script_dir, 'us_fear_greed_index'))
cn_module_path = os.path.abspath(os.path.join(script_dir, 'cn_fear_greed_index'))

# Ensure all paths are added
if eu_module_path not in sys.path:
    sys.path.insert(0, eu_module_path)
if us_module_path not in sys.path:
    sys.path.insert(0, us_module_path)
if cn_module_path not in sys.path:
    sys.path.insert(0, cn_module_path)

# Also add the parent directory to resolve intra-package imports if needed
project_root = os.path.abspath(os.path.join(script_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# --- Import calculation functions --- 
try:
    from eu_fear_greed_index.fear_greed_index import get_eu_index, interpret_score as interpret_eu_score
    logger.info("Successfully imported EU index module")
except ImportError as e:
    logger.error(f"Failed to import EU index module: {e}")
    st.error(f"Failed to import EU index module: {e}. Ensure 'eu_fear_greed_index' directory and its files exist.")
    st.stop()

try:
    from us_fear_greed_index.fear_greed_index import get_us_index, interpret_score as interpret_us_score
    logger.info("Successfully imported US index module")
except ImportError as e:
    logger.error(f"Failed to import US index module: {e}")
    st.error(f"Failed to import US index module: {e}. Ensure 'us_fear_greed_index' directory and its files exist.")
    st.stop()

# --- Import CN calculation functions (ensure it's here) ---
# Was previously removed, adding it back for consistency
try:
    from cn_fear_greed_index.fear_greed_index import get_cn_index, interpret_score as interpret_cn_score
    logger.info("Successfully imported CN index module")
    cn_module_available = True
except ImportError as e:
    logger.warning(f"Failed to import CN index module: {e}. CN calculations will be skipped in dashboard.")
    cn_module_available = False
    # Don't stop the dashboard if CN fails, just disable its section

# --- Configuration ---
st.set_page_config(
    page_title="Global Fear & Greed Index",
    layout="wide",
    initial_sidebar_state="expanded"
)
logger.info("Dashboard configuration initialized")

# Define colors for different sentiment ranges
EXTREME_FEAR_COLOR = "#ff0000"
FEAR_COLOR = "#ff9900"
NEUTRAL_COLOR = "#ffff00"
GREED_COLOR = "#00cc00"
EXTREME_GREED_COLOR = "#006600"

def interpret_api_score(score):
    """Interprets a Fear & Greed score from the API."""
    if score is None:
        return "Error"
    elif score >= 75:
        return "Extreme Greed"
    elif score >= 55:
        return "Greed"
    elif score >= 45:
        return "Neutral"
    elif score >= 25:
        return "Fear"
    else:
        return "Extreme Fear"

# --- NEW: Matplotlib Gauge Function ---
def create_matplotlib_gauge(score, interpretation):
    """Creates a Matplotlib gauge chart for the Fear & Greed score."""
    
    fig, ax = plt.subplots(figsize=(4, 2.5), subplot_kw={'aspect': 'equal'})
    fig.patch.set_facecolor('#1a1a1a') # Match dark background
    ax.set_facecolor('#1a1a1a')

    # Define colors and ranges (adjust ranges/colors as needed)
    ranges = [(0, 25), (25, 45), (45, 55), (55, 75), (75, 100)]
    colors = ["#d9534f", "#f0ad4e", "#f7f79f", "#aad4a6", "#5cb85c"]
    labels = ["Extreme Fear", "Fear", "Neutral", "Greed", "Extreme Greed"]
    
    # Arc parameters
    center = (0, 0)
    radius = 1.0
    width = 0.9 # Thickness proportion (e.g., 0.9 means 90% filled inwards)
    inner_radius = radius * (1 - width) # Calculate inner radius based on width
    
    # Draw the gauge arcs using Wedges for inward thickness
    ax.clear() # Clear previous arcs if any (might not be needed but safe)
    ax.set_facecolor('#1a1a1a') # Re-set background color after clear
    for i, (range_min, range_max) in enumerate(ranges):
        theta1_deg = (1 - range_max / 100) * 180 # Map 0-100 to 180-0 degrees (Wedge uses degrees)
        theta2_deg = (1 - range_min / 100) * 180
        wedge = patches.Wedge(center, radius, theta1_deg, theta2_deg, 
                              width=radius - inner_radius, # Width of the wedge ring 
                              facecolor=colors[i], edgecolor=None) # Use facecolor, no border
        ax.add_patch(wedge)

    # Define path effects for outline before using it (only for text and pivot)
    text_path_effects = [path_effects.withStroke(linewidth=2.5, foreground='black')]

    # --- Draw the needle manually outlined ---
    needle_length = radius * 0.9
    angle = (1 - score / 100) * np.pi # Map 0-100 to pi-0 radians
    x_end = needle_length * np.cos(angle)
    y_end = needle_length * np.sin(angle)
    
    original_linewidth = 3
    outline_width = 2.5 # Should match the path effects linewidth
    
    # 1. Draw black outline first (thicker, lower zorder)
    ax.plot([center[0], x_end], [center[1], y_end], color='black', 
            linewidth=original_linewidth + outline_width, 
            solid_capstyle='round', zorder=4) # zorder below main needle
            
    # 2. Draw white needle on top
    ax.plot([center[0], x_end], [center[1], y_end], color='white', 
            linewidth=original_linewidth, 
            solid_capstyle='round', zorder=5)
            
    # Add pivot circle (ensure it's on top)
    pivot = patches.Circle(center, radius * 0.08, color='white', zorder=8) # Higher zorder, remove path effect
    ax.add_patch(pivot)

    # Add text labels (Score and Interpretation) using the defined path effects
    ax.text(center[0], center[1] + radius * 0.2, f"{int(round(score))}", 
            horizontalalignment='center', verticalalignment='center', 
            fontsize=20, fontweight='bold', color='white', zorder=7,
            path_effects=text_path_effects) # Apply outline to score
    ax.text(center[0], center[1] - radius * 0.1, interpretation, 
            horizontalalignment='center', verticalalignment='center', 
            fontsize=10, color='white', zorder=7,
            path_effects=text_path_effects) # Apply outline to interpretation

    # Set limits and turn off axis
    ax.set_xlim(-radius * 1.1, radius * 1.1)
    ax.set_ylim(center[1], radius * 1.1) # Only show top half
    ax.axis('off')
    
    # Adjust layout tightly
    fig.tight_layout(pad=0.1)

    return fig

# --- Define load_data function ---
@st.cache_data(ttl=900)
def load_data():
    """Load market data and calculate fear and greed indices using the API.
    
    Returns:
        tuple: (Dictionary containing index data, datetime object of update time)
    """
    logger.info("Loading market data from API...")
    
    indices_data = {}
    update_time = datetime.now().astimezone() # Capture time before potential errors
    all_successful = True
    
    # --- Get EU Market Data ---
    try:
        eu_data = get_eu_market_data()
        if 'indicators' in eu_data:
            # Calculate average score from all indicators
            eu_scores = [score for score in eu_data['indicators'].values() if isinstance(score, (int, float))]
            eu_score = sum(eu_scores) / len(eu_scores) if eu_scores else None
            eu_interpretation = interpret_api_score(eu_score)
            indices_data['eu'] = {
                'score': eu_score,
                'components': eu_data['indicators'],
                'interpretation': eu_interpretation
            }
            logger.info(f"EU Index from API: {eu_score:.2f}")
        else:
            raise ValueError("No indicators found in EU market data")
    except Exception as e:
        logger.error(f"Error getting EU market data: {e}", exc_info=True)
        indices_data['eu'] = {'score': None, 'components': {}, 'interpretation': "Error", 'error': str(e)}
        all_successful = False

    # --- Get US Market Data ---
    try:
        us_data = get_us_market_data()
        if 'indicators' in us_data:
            # Calculate average score from all indicators
            us_scores = [score for score in us_data['indicators'].values() if isinstance(score, (int, float))]
            us_score = sum(us_scores) / len(us_scores) if us_scores else None
            us_interpretation = interpret_api_score(us_score)
            indices_data['us'] = {
                'score': us_score,
                'components': us_data['indicators'],
                'interpretation': us_interpretation
            }
            logger.info(f"US Index from API: {us_score:.2f}")
        else:
            raise ValueError("No indicators found in US market data")
    except Exception as e:
        logger.error(f"Error getting US market data: {e}", exc_info=True)
        indices_data['us'] = {'score': None, 'components': {}, 'interpretation': "Error", 'error': str(e)}
        all_successful = False

    # --- Get CN Market Data ---
    try:
        cn_data = get_cn_market_data()
        if 'indicators' in cn_data:
            # Calculate average score from all indicators
            cn_scores = [score for score in cn_data['indicators'].values() if isinstance(score, (int, float))]
            cn_score = sum(cn_scores) / len(cn_scores) if cn_scores else None
            cn_interpretation = interpret_api_score(cn_score)
            indices_data['cn'] = {
                'score': cn_score,
                'components': cn_data['indicators'],
                'interpretation': cn_interpretation
            }
            logger.info(f"CN Index from API: {cn_score:.2f}")
        else:
            raise ValueError("No indicators found in CN market data")
    except Exception as e:
        logger.error(f"Error getting CN market data: {e}", exc_info=True)
        indices_data['cn'] = {'score': None, 'components': {}, 'interpretation': "Error", 'error': str(e)}
        all_successful = False

    # Check if any data was successfully calculated
    if not any(data.get('score') is not None for data in indices_data.values()):
        st.error("Failed to fetch any index data. Please check logs and API connection.")
        # Return None for data, but still return the captured time
        return None, update_time 

    logger.info("API data fetching finished.")
    # Return data and the timestamp
    return indices_data, update_time

# --- NEW: Load daily summary data function ---
@st.cache_data(ttl=900)
def load_daily_summary():
    """Load daily summary data from the API and add interpretation/flags."""
    logger.info("Loading daily summary data from API...")
    try:
        summary_data = get_daily_summary_data()
        df = pd.DataFrame.from_dict(summary_data, orient='index')
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        df = df.rename(columns={
            'CN_avg_score': 'China',
            'EU_avg_score': 'Europe',
            'US_avg_score': 'USA'
        })

        # Add interpretation and flags
        region_map = {
            'Europe': {'flag': '🇪🇺', 'col': 'Europe'},
            'USA': {'flag': '🇺🇸', 'col': 'USA'},
            'China': {'flag': '🇨🇳', 'col': 'China'}
        }

        for region, details in region_map.items():
            score_col = details['col']
            df[f'{region}_interpretation'] = df[score_col].apply(lambda x: interpret_api_score(x) if pd.notna(x) else "N/A")
            df[f'{region}_flag'] = details['flag'] # Add flag column

        logger.info(f"Successfully loaded and processed {len(df)} days of summary data with interpretations.")
        return df
    except Exception as e:
        logger.error(f"Error loading daily summary data: {e}", exc_info=True)
        st.error(f"Could not load historical summary data: {e}")
        return pd.DataFrame()

# --- Helper Function to Link Tickers ---
def link_tickers_in_markdown(markdown_string):
    """Finds ticker symbols in a markdown table and converts them to links."""
    
    # Regex to find markdown table rows (simplistic, assumes structure)
    # Looks for lines starting with | `ticker`
    table_row_pattern = re.compile(r"^\|\s*(`[^`]+`)")
    # Regex to find tickers within backticks, handling potential '*' 
    ticker_pattern = re.compile(r"`(\^?[A-Z0-9\.\-=]+)(\s*\*)?`")
    yahoo_link_format = "https://finance.yahoo.com/quote/{symbol}"

    processed_lines = []
    in_table = False
    for line in markdown_string.split('\n'):
        # Basic table detection (can be made more robust)
        if '| US Market' in line:
            in_table = True
            processed_lines.append(line)
            continue
        elif in_table and not line.strip().startswith('|'):
            in_table = False # End of table

        if in_table and line.strip().startswith('|'):
            parts = line.split('|')
            new_parts = [parts[0]] # Keep the initial empty part
            for part in parts[1:]:
                # Process each cell for tickers
                match = ticker_pattern.search(part)
                if match:
                    full_ticker_text = match.group(0) # e.g., `^GSPC` or `GC=F *`
                    symbol_only = match.group(1)     # e.g., ^GSPC or GC=F
                    star_marker = match.group(2) if match.group(2) else "" # e.g., " *" or ""
                    link_text = f"{symbol_only}{star_marker.strip()}" # Text shown in link
                    url = yahoo_link_format.format(symbol=symbol_only)
                    link_markdown = f"[`{link_text}`]({url})"
                    # Replace only the first occurrence in the part to avoid issues
                    new_part = part.replace(full_ticker_text, link_markdown, 1)
                    new_parts.append(new_part)
                else:
                    new_parts.append(part)
            processed_lines.append("|".join(new_parts))
        else:
            processed_lines.append(line)
            
    return "\n".join(processed_lines)

# --- Initialize the Streamlit app and add sidebar ---
logger.info("Initializing Streamlit app...")
# st.caption("Displays comparative Fear & Greed index values for China, EU, and US markets") # Removed redundant static caption

# Add GitHub link, project context, and logo to sidebar
with st.sidebar:
    st.image("static/img/blink-blink.gif", width=256)
    
    # --- Add Trade War Context ---
    # Ensure trade_war_days and liberation_day_url are accessible here
    # They are defined later in the main try block, so we need to calculate/define them earlier
    # or pass them. Let's calculate them here for simplicity within the sidebar context.
    liberation_day_sidebar = date(2025, 4, 2)
    today_sidebar = date.today()
    trade_war_days_sidebar = (today_sidebar - liberation_day_sidebar).days
    liberation_day_url_sidebar = "https://en.wikipedia.org/wiki/Trump%27s_Liberation_Day_tariffs#:~:text=Tariff%20announcement,-Trump's%20Liberation%20Day&text=In%20the%20White%20House%20Rose,our%20declaration%20of%20economic%20independence.%22"
    
    st.markdown("#### Trade War Context")
    st.markdown(f"""
    It's been **{trade_war_days_sidebar}** days since [Liberation Day]({liberation_day_url_sidebar}), 
    when the current trade war began. Amidst these global economic shifts, 
    understanding market sentiment is crucial.
    
    This project provides comparable Fear & Greed indices for the Chinese 🇨🇳, 
    European 🇪🇺, and US 🇺🇸 markets using publicly available data.
    """)

# --- Main App Logic ---
try:
    start_time = time.time()
    logger.info("Starting dashboard display...")

    # Load data and capture update time
    indices, last_update_time = load_data()
    if indices is None:
        st.error("Failed to load market data. Please check the logs for details.")
        # Display last attempted update time even if failed
        if last_update_time:
             # Convert to UTC before formatting
             utc_update_time = last_update_time.astimezone(timezone.utc)
             # Use markdown for more prominence
             st.markdown(f"**Latest Fear & Greed indicators fetched:** {utc_update_time.strftime('%Y-%m-%d %H:%M:%S %Z')}") 
        else:
             st.markdown("**Timestamp unavailable**") # Fallback if time wasn't fetched
        st.stop()
        
    # --- Calculate Trade War Days ---
    liberation_day = date(2025, 4, 2)
    today = date.today()
    trade_war_days = (today - liberation_day).days
    
    # --- Headline for Gauges ---
    st.header(f"Latest Fear & Greed Readings (Trade War Day #{trade_war_days})")

    # Create columns for gauges
    col1, col2, col3 = st.columns(3)

    # Helper function to format score value
    def format_score(value):
        if isinstance(value, (int, float)):
            return f"{value:.2f}"
        return str(value)

    # Display EU market
    with col1:
        # st.markdown("### European Market (Latest)") # Removed title
        st.markdown("<h2 style='text-align: center;'>🇪🇺</h2>", unsafe_allow_html=True) # Centered Flag
        if indices['eu']['score'] is not None:
            # Display gauge
            eu_fig = create_matplotlib_gauge(indices['eu']['score'], indices['eu']['interpretation'])
            st.pyplot(eu_fig)
            plt.close(eu_fig)
            
            # Display component metrics, filtering out 'Final Index'
            with st.expander("EU Component Scores", expanded=False):
                components = {k: v for k, v in indices['eu']['components'].items() if k != 'Final Index'}
                metrics_list = list(components.keys())
                scores_list = list(components.values())
                scores_list_display = [format_score(score) for score in scores_list]
                
                metrics_df = pd.DataFrame({
                    'Metric': metrics_list,
                    'Score': scores_list_display
                })
                st.dataframe(metrics_df, use_container_width=True)
        else:
            st.error("EU data unavailable")

    # Display US market
    with col2:
        # st.markdown("### US Market (Latest)") # Removed title
        st.markdown("<h2 style='text-align: center;'>🇺🇸</h2>", unsafe_allow_html=True) # Centered Flag
        if indices['us']['score'] is not None:
            # Display gauge
            us_fig = create_matplotlib_gauge(indices['us']['score'], indices['us']['interpretation'])
            st.pyplot(us_fig)
            plt.close(us_fig)
            
            # Display component metrics, filtering out 'Final Index'
            with st.expander("US Component Scores", expanded=False):
                components = {k: v for k, v in indices['us']['components'].items() if k != 'Final Index'}
                metrics_list = list(components.keys())
                scores_list = list(components.values())
                scores_list_display = [format_score(score) for score in scores_list]
                
                metrics_df = pd.DataFrame({
                    'Metric': metrics_list,
                    'Score': scores_list_display
                })
                st.dataframe(metrics_df, use_container_width=True)
        else:
            st.error("US data unavailable")

    # Display CN market
    with col3:
        # st.markdown("### Chinese Market (Latest)") # Removed title
        st.markdown("<h2 style='text-align: center;'>🇨🇳</h2>", unsafe_allow_html=True) # Centered Flag
        if indices['cn']['score'] is not None:
            # Display gauge
            cn_fig = create_matplotlib_gauge(indices['cn']['score'], indices['cn']['interpretation'])
            st.pyplot(cn_fig)
            plt.close(cn_fig)
            
            # Display component metrics, filtering out 'Final Index'
            with st.expander("CN Component Scores", expanded=False):
                components = {k: v for k, v in indices['cn']['components'].items() if k != 'Final Index'}
                metrics_list = list(components.keys())
                scores_list = list(components.values())
                scores_list_display = [format_score(score) for score in scores_list]
                
                metrics_df = pd.DataFrame({
                    'Metric': metrics_list,
                    'Score': scores_list_display
                })
                st.dataframe(metrics_df, use_container_width=True)
        else:
            st.error("CN data unavailable")

    # --- Add Reload Button and Timestamp (Placed vertically) --- 
    # Removed st.columns for this section
    # Ensure last_update_time is available here
    if last_update_time: 
         # Use markdown for more prominence
         utc_update_time = last_update_time.astimezone(timezone.utc)
         st.markdown(f"**Latest Fear & Greed indicators fetched:** {utc_update_time.strftime('%Y-%m-%d %H:%M:%S %Z')}") 
    else:
         st.markdown("**Timestamp unavailable**") # Fallback if time wasn't fetched
    
    # Place button directly below timestamp
    if st.button("🔄 Reload"):
        load_data.clear()
        load_daily_summary.clear()
        st.success("Data reloaded!")
        st.rerun()
        
    daily_summary_df = load_daily_summary()

    if not daily_summary_df.empty:
        try:
            # Define colors
            colors = {'Europe': 'blue', 'USA': 'red', 'China': 'yellow'}
            
            # Create Plotly figure
            fig_historical = px.line(
                daily_summary_df, 
                x=daily_summary_df.index, 
                y=['Europe', 'USA', 'China'], 
                title="Daily Average Fear & Greed Scores",
                labels={'value': 'Average Score', 'index': 'Date'},
                color_discrete_map=colors,
                # Add custom data for hovertemplate
                custom_data=[
                    daily_summary_df['Europe_flag'], daily_summary_df['Europe_interpretation'],
                    daily_summary_df['USA_flag'], daily_summary_df['USA_interpretation'],
                    daily_summary_df['China_flag'], daily_summary_df['China_interpretation']
                ]
            )
            
            # --- Update trace names to flags for legend ---
            flag_map = {'Europe': '🇪🇺', 'USA': '🇺🇸', 'China': '🇨🇳'}
            for trace in fig_historical.data:
                if trace.name in flag_map:
                    trace.name = flag_map[trace.name]
            
            # Apply templates individually using update_traces selector
            fig_historical.update_traces(
                hovertemplate='%{customdata[0]} Index: %{y:.1f}<br>%{customdata[1]}<extra></extra>',
                selector={"name": "Europe"} # Use original name 'Europe'
            )
            fig_historical.update_traces(
                hovertemplate='%{customdata[2]} Index: %{y:.1f}<br>%{customdata[3]}<extra></extra>',
                selector={"name": "USA"} # Use original name 'USA'
            )
            fig_historical.update_traces(
                hovertemplate='%{customdata[4]} Index: %{y:.1f}<br>%{customdata[5]}<extra></extra>',
                selector={"name": "China"} # Use original name 'China'
            )
            
            # --- Add sentiment bands ---
            sentiment_bands = [
                (0, 25, EXTREME_FEAR_COLOR, "Extreme Fear"),
                (25, 45, FEAR_COLOR, "Fear"),
                (45, 55, NEUTRAL_COLOR, "Neutral"),
                (55, 75, GREED_COLOR, "Greed"),
                (75, 100, EXTREME_GREED_COLOR, "Extreme Greed"),
            ]
            
            for y_start, y_end, color, name in sentiment_bands:
                fig_historical.add_shape(
                    type="rect",
                    xref="paper", yref="y",
                    x0=0, y0=y_start,
                    x1=1, y1=y_end,
                    fillcolor=color,
                    opacity=0.2,  # Adjust opacity as needed
                    layer="below",
                    line_width=0,
                )
                
            # --- Add FEAR/GREED Text Annotations ---
            # Position FEAR label in the middle of the Extreme Fear band (0-25)
            fig_historical.add_annotation(
                x=0.5, y=12.5, # x=0.5 (center), y=midpoint of 0-25
                text="<b>FEAR</b>", 
                showarrow=False,
                xref='paper', yref='y',
                font=dict(color=EXTREME_FEAR_COLOR, size=24, family="Arial"), # Red, Larger
                opacity=0.7 # Adjust opacity if needed
            )
            # Position GREED label in the middle of the Extreme Greed band (75-100)
            fig_historical.add_annotation(
                x=0.5, y=87.5, # x=0.5 (center), y=midpoint of 75-100
                text="<b>GREED</b>", 
                showarrow=False,
                xref='paper', yref='y',
                font=dict(color=GREED_COLOR, size=24, family="Arial"), # Green, Larger
                opacity=0.7 # Adjust opacity if needed
            )
            
            # Customize layout (optional) - Ensure y-axis range covers 0-100 if not automatic
            fig_historical.update_layout(
                xaxis_title="Date",
                yaxis_title="Average Score (0=Fear, 100=Greed)",
                hovermode="x unified", # Show all values for a given date on hover
                yaxis_range=[0, 100], # Explicitly set y-axis range
            )
            
            st.plotly_chart(fig_historical, use_container_width=True)
            
            # --- Context Blurb Moved Below Chart ---
            liberation_day_url = "https://en.wikipedia.org/wiki/Trump%27s_Liberation_Day_tariffs#:~:text=Tariff%20announcement,-Trump's%20Liberation%20Day&text=In%20the%20White%20House%20Rose,our%20declaration%20of%20economic%20independence.%22"
            st.markdown(f"""
            This chart tracks market sentiment starting around [Liberation Day]({liberation_day_url}) 
            (April 2, 2025), when new tariffs marked the start of the current trade war. 
            """)
            
        except Exception as e:
            logger.error(f"Error creating historical chart: {e}", exc_info=True)
            st.error(f"Failed to display historical trend chart: {e}")
    else:
        st.warning("Historical summary data is currently unavailable.")

    # --- Methodology Explanation ---
    with st.expander("FAQ", expanded=True):
        # Updated content from user provided text
        faq_markdown = """
        ### Data Sources & Timing

        *   **Primary Data Source:** We primarily use the **Yahoo Finance API** (`yfinance`) to fetch historical and current market data for various financial instruments. This includes stock prices, index levels, ETF prices, bond yields, and currency exchange rates.
        *   **Data Availability:** All data used is sourced from publicly available financial market information.
        *   **Update Frequency:** The system fetches fresh data and recalculates the indicators and index approximately **every 3 hours**. This ensures the index reflects recent market conditions. The data is cached locally (using SQLite or PostgreSQL) to provide quick responses between updates. Additionally, a snapshot of the calculated index for each region is saved to a MySQL database every 3 hours for historical tracking.

        ### Market Data Collection

        *   For each market (US, EU, CN), we fetch data for a predefined list of symbols (tickers). These symbols represent:
            *   **Major Market Indices:** e.g., `^GSPC` (S&P 500), `^STOXX50E` (STOXX Europe 50), `000001.SS` (Shanghai Composite).
            *   **Sector ETFs (US/CN):** Exchange-Traded Funds representing different market sectors (e.g., `XLK` for Technology, `XLF` for Financials).
            *   **Individual Stocks (EU/CN):** A selection of large-cap stocks relevant to the region (e.g., `TTE.PA`, `601318.SS`).
            *   **Volatility Measures:** e.g., `^VIX` (CBOE Volatility Index). For EU/CN, volatility is calculated from the main index's historical price changes if a direct ticker isn't available or preferred.
            *   **Safe Haven Assets:** Gold futures (`GC=F`), Treasury yields (`^TNX`, `^TYX`), relevant government bond ETFs (e.g., `EXVM.DE`), and key currency pairs (e.g., `USDCNY=X`).
            *   **Bond Market Indicators:** High-yield corporate bond ETFs (e.g., `HYG`, `IHYG.L`, `KHYB`) and Investment-grade corporate bond ETFs (e.g., `LQD`, `IEAC.L`).

        *   *The specific tickers used for each indicator calculation are defined within the `INDICATOR_TICKERS` configuration in the code.*

        #### Fetched Symbols (Tickers) by Region:

        The following table lists the *unique* set of symbols fetched for each region. Note that the CN market column includes both Chinese/HK symbols and global/US symbols used for specific indicator calculations (marked with \*).

        | US Market (`all_us_tickers`) | EU Market (`all_eu_tickers`) | CN Market (Chinese/HK + Global\*) |
        | :--------------------------- | :--------------------------- | :-------------------------------- |
        | `^GSPC`                      | `^STOXX50E`                  | `000001.SS`                       |
        | `^DJI`                       | `TTE.PA`                     | `^HSI`                            |
        | `^IXIC`                      | `UCG.MI`                     | `000300.SS`                       |
        | `^RUT`                       | `ALV.DE`                     | `399001.SZ`                       |
        | `XLK`                        | `CS.PA`                      | `399006.SZ`                       |
        | `XLF`                        | `ABI.BR`                     | `512000.SS`                       |
        | `XLE`                        | `SAN.PA`                     | `159939.SZ`                       |
        | `XLV`                        | `ITX.MC`                     | `512330.SS`                       |
        | `XLY`                        | `ENEL.MI`                    | `512800.SS`                       |
        | `XLP`                        | `IBE.MC`                     | `159928.SZ`                       |
        | `XLI`                        | `IFX.DE`                     | `159936.SZ`                       |
        | `XLB`                        | `SIE.DE`                     | `512170.SS`                       |
        | `XLU`                        | `DTE.DE`                     | `512290.SS`                       |
        | `XLRE`                       | `ADS.DE`                     | `512580.SS`                       |
        | `^VIX`                       | `NOKIA.HE`                   | `159945.SZ`                       |
        | `GC=F`                       | `BAYN.DE`                    | `512660.SS`                       |
        | `^TNX`                       | `VOW.DE`                     | `GC=F` \*                         |
        | `^TYX`                       | `FLTR.L`                     | `^TNX` \*                         |
        | `USDEUR=X`                   | `NOVN.SW`                    | `^VIX` \*                         |
        | `HYG`                        | `ISP.MI`                     | `USDCNY=X` \*                     |
        | `JNK`                        | `STLAM.MI`                   | `511260.SS`                       |
        | `LQD`                        | `KER.PA`                     | `511380.SS`                       |
        |                              | `PRX.AS`                     | `KHYB` \*                         |
        |                              | `GC=F`                       | `511270.SS`                       |
        |                              | `EXVM.DE`                    | `601318.SS`                       |
        |                              | `^TNX`                       | `600036.SS`                       |
        |                              | `EURUSD=X`                   | `601888.SS`                       |
        |                              | `IHYG.L`                     | `600519.SS`                       |
        |                              | `IEAC.L`                     | `601988.SS`                       |
        |                              |                              | `600028.SS`                       |
        |                              |                              | `600050.SS`                       |
        |                              |                              | `601857.SS`                       |
        |                              |                              | `601398.SS`                       |
        |                              |                              | `601628.SS`                       |
        |                              |                              | `600104.SS`                       |
        |                              |                              | `601088.SS`                       |
        |                              |                              | `0700.HK`                         |
        |                              |                              | `9988.HK`                         |
        |                              |                              | `1211.HK`                         |
        |                              |                              | `512880.SS`                       |
        |                              |                              | `510050.SS`                       |
        |                              |                              | `510300.SS`                       |

        _\*Global/US-based symbols used for specific indicator calculations (e.g., global benchmarks for Safe Haven Demand, proxy for Junk Bond Demand, global risk indicator)._

        ### Indicator Calculation

        *   Using the fetched data, we calculate **six key indicators** for each market:
            1.  **Market Momentum:** Measures the market's momentum based on the primary index's 4-month price change, adjusted by its Relative Strength Index (RSI).
            2.  **Volatility:** Measures market fear using volatility metrics (like the VIX for the US, or calculated historical volatility for EU/CN), scaled inversely (higher volatility means lower score/more fear).
            3.  **RSI (Relative Strength Index):** Calculates the average RSI across a basket of relevant indices and stocks/ETFs to gauge overbought/oversold conditions.
            4.  **Safe Haven Demand:** Measures the relative performance of safe-haven assets (like gold and government bonds) compared to riskier assets. A higher score indicates lower demand for safe havens (more greed). The calculation differs slightly for China to include currency and local index factors.
            5.  **Market Trend:** Compares the primary market index's current price to its 50-day simple moving average (SMA). A price significantly above the average indicates greed, while one far below indicates fear.
            6.  **Junk Bond Demand:** Calculates the credit spread between high-yield (junk) bonds and investment-grade or government bonds. A narrowing spread (lower risk premium) indicates higher greed, while a widening spread indicates higher fear. The score is scaled inversely.

        *   *Each indicator is calculated and scaled to produce a score between 0 (Extreme Fear) and 100 (Extreme Greed), based on predefined thresholds and scaling parameters found in `INDICATOR_SCALING_PARAMS`.*

        ### Final Index Calculation

        *   The **Final Fear & Greed Index** score for each region is calculated by taking an **equal-weighted average** of the scores from the six indicators calculated in the previous step.
        *   *If any indicator calculation fails (due to missing data, etc.), it is excluded from the average. The final score is based on the average of the remaining *valid* indicators.*
        *   Based on the final score, an interpretation is assigned:
            *   0-20: Extreme Fear
            *   21-40: Fear
            *   41-60: Neutral
            *   61-80: Greed
            *   81-100: Extreme Greed
        
        *This process provides a snapshot of market sentiment for each region based on these diverse factors.*
        """
        # Linkify tickers in the FAQ markdown
        linked_faq_markdown = link_tickers_in_markdown(faq_markdown)
        st.markdown(linked_faq_markdown, unsafe_allow_html=True)

    # --- Footer ---
    st.markdown("---")
    
    logger.info(f"Dashboard displayed successfully in {time.time() - start_time:.2f} seconds")

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    logger.error("Dashboard error occurred", exc_info=True)
    print("--- ERROR IN DASHBOARD --- ")
    traceback.print_exc()
    print("------")

# --- Animation Feature (Hidden) ---
if 'run_animation' in locals() and run_animation:
    animation_frames = 100
    step = 1
    
    logger.info("Running needle animation...")
    
    progress_text = "Animation in progress. Please wait."
    progress_bar = st.progress(0, text=progress_text)
    
    # Animation loop
    for i in range(0, animation_frames + 1, step):
        # Update progress bar
        progress_bar.progress(i / animation_frames, text=f"{progress_text} ({i}%)")
        
        # Create and update the gauge charts
        with col1:
            eu_fig = create_matplotlib_gauge(i, "Animation")
            st.pyplot(eu_fig)
            plt.close(eu_fig)
        
        with col2:
            us_fig = create_matplotlib_gauge(i, "Animation")
            st.pyplot(us_fig)
            plt.close(us_fig)
            
        with col3:
            cn_fig = create_matplotlib_gauge(i, "Animation")
            st.pyplot(cn_fig)
            plt.close(cn_fig)
        
        time.sleep(0.05)  # Control animation speed
    
    # Reset progress bar
    progress_bar.empty()
    
    logger.info("Animation completed")

# --- Remove functions related to the deleted section ---
# def display_components_table(indices):
#     """Display component metrics for all markets"""
#     try:
#         logger.info("Creating components table...")
#         # ... (rest of the function code) ...
#     except Exception as e:
#         logger.error(f"Error displaying components table: {e}", exc_info=True)
#         st.error(f"Error displaying components: {str(e)}")

# def create_gauge(score, title):
#     """Create a gauge chart for the fear and greed index"""
#     try:
#         # ... (rest of the function code) ...
#         return fig
#     except Exception as e:
#         logger.error(f"Error creating gauge chart: {e}", exc_info=True)
#         st.error(f"Error creating gauge: {str(e)}")

# def app():
#     """Main app function"""
#     try:
#         # ... (rest of the function code) ...
#     except Exception as e:
#         logger.error(f"App error: {e}", exc_info=True)
#         st.error(f"Application error: {str(e)}")

# --- Remove the main call to app() ---
# if __name__ == "__main__":
#     app() 

# --- Ensure the top part still runs if this script is executed directly ---
# (The code outside functions will run when `streamlit run dashboard.py` is executed) 