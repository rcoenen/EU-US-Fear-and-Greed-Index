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
    """Load market data and calculate fear and greed indices using specific functions (like test harness)"""
    logger.info("Loading market data and calculating indices directly...")
    
    indices_data = {}
    
    # --- Calculate EU Index --- (Direct call)
    try:
        eu_score, eu_components = get_eu_index()
        eu_interpretation = interpret_eu_score(eu_score)
        indices_data['eu'] = {
            'score': eu_score, 
            'components': eu_components, 
            'interpretation': eu_interpretation
        }
        logger.info(f"EU Index calculated directly: {eu_score:.2f}")
    except Exception as e:
        logger.error(f"Error calculating EU index directly: {e}", exc_info=True)
        indices_data['eu'] = {'score': None, 'components': {}, 'interpretation': "Error", 'error': str(e)}

    # --- Calculate US Index --- (Direct call)
    try:
        us_score, us_components = get_us_index()
        us_interpretation = interpret_us_score(us_score)
        indices_data['us'] = {
            'score': us_score, 
            'components': us_components, 
            'interpretation': us_interpretation
        }
        logger.info(f"US Index calculated directly: {us_score:.2f}")
    except Exception as e:
        logger.error(f"Error calculating US index directly: {e}", exc_info=True)
        indices_data['us'] = {'score': None, 'components': {}, 'interpretation': "Error", 'error': str(e)}

    # --- Calculate CN Index (if available) --- (Direct call)
    if cn_module_available:
        try:
            cn_score, cn_components = get_cn_index()
            cn_interpretation = interpret_cn_score(cn_score)
            indices_data['cn'] = {
                'score': cn_score, 
                'components': cn_components, 
                'interpretation': cn_interpretation
            }
            logger.info(f"CN Index calculated directly: {cn_score:.2f}")
        except Exception as e:
            logger.error(f"Error calculating CN index directly: {e}", exc_info=True)
            indices_data['cn'] = {'score': None, 'components': {}, 'interpretation': "Error", 'error': str(e)}
    else:
        indices_data['cn'] = {'score': None, 'components': {}, 'interpretation': "Not Available", 'error': "Module not imported"}

    # Check if any data was successfully calculated
    if not any(data.get('score') is not None for data in indices_data.values()):
        st.error("Failed to calculate any index data. Please check logs and API connection.")
        return None # Return None if all calculations failed

    logger.info("Direct index calculations finished.")
    return indices_data

# --- Initialize the Streamlit app and add sidebar ---
logger.info("Initializing Streamlit app...")
# Remove the main title
# st.title("📊 Global Fear & Greed Index Dashboard") 
st.caption("Displays comparative Fear & Greed index values for China, EU, and US markets")

# Add GitHub link, project context, and logo to sidebar
with st.sidebar:
    st.image("static/img/tradewar_EU-US-logo.jpg", width=256)  # Display logo with half the original width
    st.markdown("### Project Information")
    st.markdown(
        """
        Amidst the Trump Trade War that the US is waging on the world, understanding market sentiment is crucial. 
        This project provides comparable Fear & Greed indices for the Chinese, European, and US markets using a unified methodology.
        """
    )
    st.markdown("For more information about this project and how it works, visit:")
    st.markdown("[GitHub Repository](https://github.com/rcoenen/EU-US-Fear-and-Greed-Index)")
    st.markdown("---")

# Add VSTOXX reminder to sidebar as well
# st.sidebar.warning("Note: EU Volatility uses VSTOXX. Ensure `VSTOXX.csv` exists in `eu_fear_greed_index` folder or data fetching is live.")

# --- Wrap main execution in try-except ---
try:
    logger.info("Starting main dashboard execution...")
    start_time = time.time()
    
    # Call the potentially cached load_data function
    cached_load_data = st.cache_data(ttl=3600)(load_data)
    logger.info("Cache initialized, fetching data...")
    
    data = cached_load_data()
    logger.info("Data fetch completed successfully")
    
    # Placeholders for buttons
    col_btn1, col_btn2, _ = st.columns([1.5, 2, 5])

    with col_btn1:
        if st.button("🔄 Refresh Data", key="refresh_data_button"):
            logger.info("Refresh button clicked, clearing cache...")
            st.cache_data.clear()
            st.rerun()

    with col_btn2:
        # run_animation = st.button("▶️ Test Needle Animation (0-100)", key="animate_button") # Button hidden
        run_animation = False # Ensure animation doesn't run automatically

    st.markdown("---") # Separator

    # --- Display Gauges ---
    logger.info("Rendering gauges...")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.header("🇨🇳 China")
        cn_gauge_placeholder = st.empty() # Placeholder for CN Matplotlib gauge
        if not run_animation:
            logger.info("Creating CN gauge...")
            cn_fig = create_matplotlib_gauge(data["cn"]["score"], data["cn"]["interpretation"])
            cn_gauge_placeholder.pyplot(cn_fig, use_container_width=False)
            plt.close(cn_fig) # Close the figure to free memory
            
            with st.expander("View CN Indicator Details", expanded=True):
                # Convert metrics to DataFrame for display
                metrics_df = pd.DataFrame({
                    'Metric': list(data["cn"]["components"].keys()),
                    'Score': list(data["cn"]["components"].values())
                })
                st.dataframe(metrics_df)

    with col2:
        st.header("🇪🇺 Europe")
        eu_gauge_placeholder = st.empty() # Placeholder for EU Matplotlib gauge
        if not run_animation:
            logger.info("Creating EU gauge...")
            eu_fig = create_matplotlib_gauge(data["eu"]["score"], data["eu"]["interpretation"])
            eu_gauge_placeholder.pyplot(eu_fig, use_container_width=False)
            plt.close(eu_fig) # Close the figure to free memory
            
            with st.expander("View EU Indicator Details", expanded=True):
                # Convert metrics to DataFrame for display
                metrics_df = pd.DataFrame({
                    'Metric': list(data["eu"]["components"].keys()),
                    'Score': list(data["eu"]["components"].values())
                })
                st.dataframe(metrics_df)

    with col3:
        st.header("🇺🇸 United States")
        us_gauge_placeholder = st.empty() # Placeholder for US Matplotlib gauge
        if not run_animation:
            logger.info("Creating US gauge...")
            us_fig = create_matplotlib_gauge(data["us"]["score"], data["us"]["interpretation"])
            us_gauge_placeholder.pyplot(us_fig, use_container_width=False)
            plt.close(us_fig) # Close the figure to free memory
            
            with st.expander("View US Indicator Details", expanded=True):
                # Convert metrics to DataFrame for display
                metrics_df = pd.DataFrame({
                    'Metric': list(data["us"]["components"].keys()),
                    'Score': list(data["us"]["components"].values())
                })
                st.dataframe(metrics_df)

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
    # Use timezone-aware datetime and add timezone name (%Z)
    st.caption("Last updated: " + datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z"))
    
    logger.info(f"Dashboard displayed successfully in {time.time() - start_time:.2f} seconds")

except Exception as e:
    # Handle errors and provide user feedback
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
            eu_gauge_placeholder.pyplot(eu_fig)
            plt.close(eu_fig)
        
        with col2:
            us_fig = create_matplotlib_gauge(i, "Animation")
            us_gauge_placeholder.pyplot(us_fig)
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
#         return None

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