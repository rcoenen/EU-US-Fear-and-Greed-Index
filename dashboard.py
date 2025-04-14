import streamlit as st
import time
import numpy as np
# import plotly.graph_objects as go # Remove if Plotly not used elsewhere
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.patheffects as path_effects # Import path effects
import pandas as pd # Keep for data handling
import os
import sys
from datetime import timedelta
# from utils import fetch_eu_data, fetch_us_data, interpret_score, interpret_eu_score, interpret_us_score # Assuming utils.py exists

# --- Add subdirectories to path for imports --- 
# This ensures the dashboard can find the modules in the subdirectories
# Note: Having __init__.py files helps, but sometimes explicit path modification is needed depending on execution context.
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(project_root, 'eu_fear_greed_index'))
sys.path.insert(0, os.path.join(project_root, 'us_fear_greed_index'))

# --- Import calculation functions --- 
try:
    from eu_fear_greed_index.fear_greed_index import get_final_index as get_eu_index, interpret_score as interpret_eu_score
except ImportError as e:
    st.error(f"Failed to import EU index module: {e}. Ensure 'eu_fear_greed_index' directory and its files exist.")
    st.stop()

try:
    from us_fear_greed_index.fear_greed_index import get_final_index as get_us_index, interpret_score as interpret_us_score
except ImportError as e:
    st.error(f"Failed to import US index module: {e}. Ensure 'us_fear_greed_index' directory and its files exist.")
    st.stop()

# --- Configuration ---
st.set_page_config(page_title="Fear & Greed Index Dashboard", layout="wide")

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
    ax.text(center[0], center[1] + radius * 0.2, f"{score:.1f}", 
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

# --- Load Data ---
@st.cache_data(ttl=3600) # Cache for 1 hour
def load_data():
    # Call the actual imported functions
    eu_score, eu_results = get_eu_index() 
    us_score, us_results = get_us_index()

    eu_interpretation = interpret_eu_score(eu_score)
    us_interpretation = interpret_us_score(us_score)
    return eu_results, eu_score, eu_interpretation, us_results, us_score, us_interpretation

# --- Streamlit App Layout ---
st.title("📊 Fear & Greed Index Dashboard (EU & US)")
st.caption("Displays custom Fear & Greed index values calculated using yfinance data.")

# Load data
eu_results, eu_score, eu_interpretation, us_results, us_score, us_interpretation = load_data()

# Placeholders for buttons
col_btn1, col_btn2, _ = st.columns([1, 2, 5]) # Adjust column ratios as needed

with col_btn1:
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

with col_btn2:
    run_animation = st.button("▶️ Test Needle Animation (0-100)")

st.markdown("---") # Separator

# --- Display Gauges ---
col1, col2 = st.columns(2)

with col1:
    st.header("🇪🇺 EU Index")
    eu_gauge_placeholder = st.empty() # Placeholder for EU Matplotlib gauge
    if not run_animation:
        eu_fig = create_matplotlib_gauge(eu_score, eu_interpretation)
        eu_gauge_placeholder.pyplot(eu_fig, use_container_width=False)
        plt.close(eu_fig) # Close the figure to free memory
        
        with st.expander("View EU Indicator Details"):
             if eu_results:
                # Assuming results are already in a suitable format (like a DataFrame)
                st.dataframe(eu_results)
             else:
                st.warning("Could not fetch EU indicator data.")

with col2:
    st.header("🇺🇸 US Index")
    us_gauge_placeholder = st.empty() # Placeholder for US Matplotlib gauge
    if not run_animation:
        us_fig = create_matplotlib_gauge(us_score, us_interpretation)
        us_gauge_placeholder.pyplot(us_fig, use_container_width=False)
        plt.close(us_fig) # Close the figure to free memory

        with st.expander("View US Indicator Details"):
             if us_results:
                 st.dataframe(us_results)
             else:
                 st.warning("Could not fetch US indicator data.")

# --- Run Animation if Triggered ---
if run_animation:
    steps = 50 # Number of steps
    sleep_time = 3.0 / steps # Total 3 seconds duration
    
    for val in range(0, 101, 100 // steps):
        # Use one of the specific interpret functions (assuming they map ranges the same)
        interp_text = interpret_eu_score(val) 
        
        # Ensure val doesn't exceed 100 for the last step if steps isn't a divisor of 100
        current_score = min(val, 100.0) 
        
        eu_fig_anim = create_matplotlib_gauge(current_score, interp_text)
        us_fig_anim = create_matplotlib_gauge(current_score, interp_text)
        
        with col1:
            eu_gauge_placeholder.pyplot(eu_fig_anim, use_container_width=False)
            plt.close(eu_fig_anim) # Close figure after displaying
        with col2:
            us_gauge_placeholder.pyplot(us_fig_anim, use_container_width=False)
            plt.close(us_fig_anim) # Close figure after displaying
            
        time.sleep(sleep_time)
    
    # Stop animation by forcing a rerun (clears the run_animation state)
    st.rerun()

# --- Sidebar --- 
st.sidebar.header("About")
st.sidebar.info("""
This dashboard calculates and displays simplified Fear & Greed indices for the EU and US markets 
based on publicly available data via the `yfinance` library.

**Indicators:**
- Market Momentum
- Stock Strength (Sample)
- Stock Breadth (Sample)
- Volatility (VSTOXX/VIX)
- Safe Haven Demand
- Junk Bond Demand
- Put/Call Proxy (EU: N/A, US: VIX Level)

**Disclaimer:** This is for educational purposes only and uses approximations for some indicators. 
It may not perfectly match proprietary indices like CNN's.
""")

# Add VSTOXX reminder to sidebar as well
# st.sidebar.warning("**EU Index Requirement:** Ensure `VSTOXX.csv` is downloaded from STOXX.com and placed inside the `eu_fear_greed_index` folder for accurate EU Volatility calculation.") 