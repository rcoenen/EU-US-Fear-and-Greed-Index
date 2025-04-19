import numpy as np
from typing import Dict, Optional, Any

def format_regional_comparison_table(
    eu_results: Dict[str, Any],
    us_results: Dict[str, Any],
    cn_results: Optional[Dict[str, Any]],
    eu_final_score: Optional[float],
    us_final_score: Optional[float],
    cn_final_score: Optional[float]
) -> str:
    """
    Formats the regional Fear & Greed index results into a text-based table.

    Args:
        eu_results: Dictionary of EU indicator results.
        us_results: Dictionary of US indicator results.
        cn_results: Dictionary of CN indicator results (or None if not available).
        eu_final_score: Final EU score (or None if not available).
        us_final_score: Final US score (or None if not available).
        cn_final_score: Final CN score (or None if not available).

    Returns:
        A string containing the formatted comparison table.
    """
    if eu_final_score is None or us_final_score is None:
        return "Regional comparison requires at least EU and US scores."

    lines = []
    cn_available = cn_final_score is not None and cn_results is not None
    
    lines.append("\n---------------- REGIONAL COMPARISON ----------------")
    headers = ['Indicator', 'EU', 'US']
    if cn_available:
        headers.append('CN')
    lines.append(f"{headers[0]:<25} {headers[1]:<10} {headers[2]:<10}" + (f" {headers[3]:<10}" if cn_available else ""))
    lines.append("-" * (60 if not cn_available else 70))
    
    # Get all unique indicator names
    all_indicators = set(eu_results.keys()) | set(us_results.keys())
    if cn_available:
        all_indicators |= set(cn_results.keys())
    
    for indicator in sorted(all_indicators):
        eu_score_str = eu_results.get(indicator, "N/A")
        us_score_str = us_results.get(indicator, "N/A")
        cn_score_str = cn_results.get(indicator, "N/A") if cn_available else None
        
        try:
            # Handle potential string formatting like "Indicator Name: 12.34"
            eu_val_str = eu_score_str.split(":")[-1].strip() if isinstance(eu_score_str, str) else str(eu_score_str)
            us_val_str = us_score_str.split(":")[-1].strip() if isinstance(us_score_str, str) else str(us_score_str)
            cn_val_str = cn_score_str.split(":")[-1].strip() if cn_available and isinstance(cn_score_str, str) else (str(cn_score_str) if cn_available else "N/A")

            eu_score = float(eu_val_str) if eu_val_str != "N/A" else float('nan')
            us_score = float(us_val_str) if us_val_str != "N/A" else float('nan')
            cn_score = float(cn_val_str) if cn_available and cn_val_str != "N/A" else float('nan')
            
            # Format with 2 decimal places for indicators
            eu_display = f"{eu_score:.2f}" if not np.isnan(eu_score) else "N/A"
            us_display = f"{us_score:.2f}" if not np.isnan(us_score) else "N/A"
            cn_display = f"{cn_score:.2f}" if cn_available and not np.isnan(cn_score) else "N/A"
            
            lines.append(f"{indicator:<25} {eu_display:<10} {us_display:<10}" + (f" {cn_display:<10}" if cn_available else ""))
        except (ValueError, IndexError):
            lines.append(f"{indicator:<25} {'N/A':<10} {'N/A':<10}" + (f" {'N/A':<10}" if cn_available else ""))
    
    lines.append("-" * (60 if not cn_available else 70))
    # Round final scores to integers
    lines.append(f"{'Final Score':<25} {int(round(eu_final_score)):<10} {int(round(us_final_score)):<10}" + 
          (f" {int(round(cn_final_score)):<10}" if cn_available else ""))
    lines.append("--------------------------------------------")

    return "\n".join(lines) 