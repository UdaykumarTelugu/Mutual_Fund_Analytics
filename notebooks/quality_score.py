"""
Module for calculating the Composite Quality Score.
Combines profitability, efficiency, cash flow, and growth metrics.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

def calculate_composite_quality_score(
    profitability_score: float,
    efficiency_score: float,
    cash_flow_score: float,
    growth_score: float
) -> Optional[float]:
    """
    Calculates the Composite Quality Score.
    
    Combines profitability, efficiency, cash flow, and growth metrics into a normalized score.

    Args:
        profitability_score (float): Normalized score for profitability (0-100).
        efficiency_score (float): Normalized score for efficiency (0-100).
        cash_flow_score (float): Normalized score for cash flow quality (0-100).
        growth_score (float): Normalized score for growth (0-100).

    Returns:
        Optional[float]: A composite quality score between 0 and 100, or None if inputs are invalid.
    """
    try:
        if any(s is None for s in [profitability_score, efficiency_score, cash_flow_score, growth_score]):
            logger.warning("Missing one or more sub-scores. Cannot calculate composite quality score.")
            return None
            
        composite = (profitability_score + efficiency_score + cash_flow_score + growth_score) / 4.0
        
        # Clamp to 0-100
        composite = max(0.0, min(100.0, composite))
        return composite
    except Exception as e:
        logger.error(f"Unexpected exception in composite quality score calculation: {e}")
        return None
