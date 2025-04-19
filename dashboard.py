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
from datetime import timedelta, datetime
import traceback # Import traceback for printing errors
import logging
import argparse
from dotenv import load_dotenv
from utils.api_client import get_cn_market_data, get_eu_market_data, get_us_market_data

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
    """Load market data and calculate fear and greed indices using the API."""
    logger.info("Loading market data from API...")
    
    indices_data = {}
    
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

    # Check if any data was successfully calculated
    if not any(data.get('score') is not None for data in indices_data.values()):
        st.error("Failed to fetch any index data. Please check logs and API connection.")
        return None

    logger.info("API data fetching finished.")
    return indices_data

# --- Initialize the Streamlit app and add sidebar ---
logger.info("Initializing Streamlit app...")
st.caption("Displays comparative Fear & Greed index values for China, EU, and US markets")

# Add GitHub link, project context, and logo to sidebar
with st.sidebar:
    st.image("static/img/blink-blink.gif", width=256)
    st.markdown("### Project Information")
    st.markdown(
        """
        Amidst the Trump Trade War that the US is waging on the world, understanding market sentiment is crucial. 
        This project provides comparable Fear & Greed indices for the Chinese, European, and US markets using a unified methodology.
        """
    )
    st.markdown("For more information about this project and how it works, visit:")
    st.markdown("[GitHub Repository](https://github.com/robinhood-jim/fear-and-greed-index)")

# --- Main App Logic ---
try:
    start_time = time.time()
    logger.info("Starting dashboard display...")

    # Load data
    indices = load_data()
    if indices is None:
        st.error("Failed to load market data. Please check the logs for details.")
        st.stop()

    # Create columns for gauges
    col1, col2, col3 = st.columns(3)

    # Helper function to format score value
    def format_score(value):
        if isinstance(value, (int, float)):
            return f"{value:.2f}"
        return str(value)

    # Display EU market
    with col1:
        st.markdown("### European Market")
        if indices['eu']['score'] is not None:
            # Display gauge
            eu_fig = create_matplotlib_gauge(indices['eu']['score'], indices['eu']['interpretation'])
            st.pyplot(eu_fig)
            plt.close(eu_fig)
            
            # Display component metrics
            metrics_list = list(indices['eu']['components'].keys())
            scores_list = list(indices['eu']['components'].values())
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
        st.markdown("### US Market")
        if indices['us']['score'] is not None:
            # Display gauge
            us_fig = create_matplotlib_gauge(indices['us']['score'], indices['us']['interpretation'])
            st.pyplot(us_fig)
            plt.close(us_fig)
            
            # Display component metrics
            metrics_list = list(indices['us']['components'].keys())
            scores_list = list(indices['us']['components'].values())
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
        st.markdown("### Chinese Market")
        if indices['cn']['score'] is not None:
            # Display gauge
            cn_fig = create_matplotlib_gauge(indices['cn']['score'], indices['cn']['interpretation'])
            st.pyplot(cn_fig)
            plt.close(cn_fig)
            
            # Display component metrics
            metrics_list = list(indices['cn']['components'].keys())
            scores_list = list(indices['cn']['components'].values())
            scores_list_display = [format_score(score) for score in scores_list]
            
            metrics_df = pd.DataFrame({
                'Metric': metrics_list,
                'Score': scores_list_display
            })
            st.dataframe(metrics_df, use_container_width=True)
        else:
            st.error("CN data unavailable")

    # --- Methodology Explanation ---
    with st.expander("Methodology", expanded=True):
        st.markdown("""
        ## Fear & Greed Index Calculation
        
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
        """)

    # --- Footer ---
    st.markdown("---")
    st.caption("Last updated: " + datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z"))
    
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
            
        time.sleep(0.05)  # Control animation speed
    
    # Reset progress bar
    progress_bar.empty()
    
    logger.info("Animation completed")

# --- Remove functions related to the deleted section ---
# def display_components_table(indices):
#     """Display component metrics for all markets"""
#     try:
#         logger.info(\"Creating components table...\")
#         # ... (rest of the function code) ...
#     except Exception as e:
#         logger.error(f\"Error displaying components table: {e}\", exc_info=True)
#         st.error(f\"Error displaying components: {str(e)}\")

# def create_gauge(score, title):
#     """Create a gauge chart for the fear and greed index"""
#     try:
#         # ... (rest of the function code) ...
#         return fig
#     except Exception as e:
#         logger.error(f\"Error creating gauge chart: {e}\", exc_info=True)
#         st.error(f\"Error creating gauge: {str(e)}\")

# def app():
#     """Main app function"""
#     try:
#         # ... (rest of the function code) ...
#     except Exception as e:
#         logger.error(f\"App error: {e}\", exc_info=True)
#         st.error(f\"Application error: {str(e)}\")

# --- Remove the main call to app() ---
# if __name__ == \"__main__\":
#     app() 

# --- Ensure the top part still runs if this script is executed directly ---
# (The code outside functions will run when `streamlit run dashboard.py` is executed) 