"""
Module for calculating Compound Annual Growth Rate (CAGR).
Supports Revenue, PAT, and EPS over various timeframes (3, 5, 10 years).
"""

import enum
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class CagrFlag(enum.Enum):
    """Enumeration for CAGR edge case flags."""
    NORMAL = "NORMAL"
    ZERO_BASE = "ZERO_BASE"
    INSUFFICIENT = "INSUFFICIENT"
    DECLINE_TO_LOSS = "DECLINE_TO_LOSS"
    TURNAROUND = "TURNAROUND"
    BOTH_NEGATIVE = "BOTH_NEGATIVE"


# Type alias for return format (value, flag)
CagrResult = Tuple[Optional[float], CagrFlag]


def _calculate_cagr_base(start_value: float, end_value: float, years: int) -> CagrResult:
    """
    Core reusable function to calculate CAGR, handling complex edge cases.

    Formula: ((end_value / start_value) ** (1 / years) - 1) * 100

    Args:
        start_value (float): The value at the beginning of the period.
        end_value (float): The value at the end of the period.
        years (int): Number of years for the CAGR period.

    Returns:
        CagrResult: A tuple containing the CAGR value (float or None) and a CagrFlag.
    """
    if years <= 0:
        logger.warning(f"Insufficient years for CAGR: {years}")
        return None, CagrFlag.INSUFFICIENT

    if start_value == 0:
        logger.warning("CAGR base is zero. Calculation is undefined.")
        return None, CagrFlag.ZERO_BASE

    if start_value > 0 and end_value < 0:
        logger.info("CAGR flagged as DECLINE_TO_LOSS.")
        return None, CagrFlag.DECLINE_TO_LOSS

    if start_value < 0 and end_value > 0:
        logger.info("CAGR flagged as TURNAROUND.")
        return None, CagrFlag.TURNAROUND

    if start_value < 0 and end_value < 0:
        logger.info("CAGR flagged as BOTH_NEGATIVE.")
        return None, CagrFlag.BOTH_NEGATIVE

    try:
        cagr = (((end_value / start_value) ** (1 / years)) - 1) * 100
        return cagr, CagrFlag.NORMAL
    except Exception as e:
        logger.error(f"Unexpected mathematical error computing CAGR: {e}")
        return None, CagrFlag.INSUFFICIENT


def validate_historical_data(years: list[int], values: list[Optional[float]], period: int) -> bool:
    """
    Validates the historical data for CAGR calculation.

    Args:
        years (list[int]): List of years.
        values (list[Optional[float]]): List of financial values.
        period (int): Number of years required for calculation.

    Returns:
        bool: True if valid, False otherwise.
    """
    if not years or not values:
        logger.warning("Missing values: years or values list is empty.")
        return False
        
    if len(years) != len(values):
        logger.warning("Missing values: mismatch between years and values count.")
        return False

    if any(v is None for v in values):
        logger.warning("Null values found in financial records.")
        return False

    if len(years) != len(set(years)):
        logger.warning("Duplicate years found in historical data.")
        return False

    if sorted(years) != years:
        logger.warning("Incorrect year ordering. Years must be sorted chronologically.")
        return False

    expected_years = list(range(years[0], years[-1] + 1))
    if years != expected_years:
        logger.warning("Missing financial records for some years in the sequence.")
        return False

    if (years[-1] - years[0]) < period:
        logger.warning(f"Insufficient history. Required {period} years, available {years[-1] - years[0]} years.")
        return False

    return True


def _calculate_cagr_from_history(years: list[int], values: list[Optional[float]], period: int) -> CagrResult:
    """
    Wrapper to validate history and compute CAGR for the requested period.
    """
    is_valid = validate_historical_data(years, values, period)
    if not is_valid:
        return None, CagrFlag.INSUFFICIENT
        
    end_value = values[-1]
    start_value = values[-1 - period]
    
    return _calculate_cagr_base(start_value, end_value, period)


def calculate_revenue_cagr(years: list[int], revenues: list[Optional[float]], period: int) -> CagrResult:
    """
    Calculates Revenue CAGR.
    Supports 3, 5, or 10 year periods dynamically.

    Args:
        years (list[int]): Sequence of years.
        revenues (list[Optional[float]]): Corresponding sequence of revenues.
        period (int): Number of years for the CAGR window.

    Returns:
        CagrResult: Tuple of (CAGR value, Flag).
    """
    return _calculate_cagr_from_history(years, revenues, period)


def calculate_pat_cagr(years: list[int], pats: list[Optional[float]], period: int) -> CagrResult:
    """
    Calculates Profit After Tax (PAT) CAGR.
    Supports 3, 5, or 10 year periods dynamically.

    Args:
        years (list[int]): Sequence of years.
        pats (list[Optional[float]]): Corresponding sequence of PATs.
        period (int): Number of years for the CAGR window.

    Returns:
        CagrResult: Tuple of (CAGR value, Flag).
    """
    return _calculate_cagr_from_history(years, pats, period)


def calculate_eps_cagr(years: list[int], eps_values: list[Optional[float]], period: int) -> CagrResult:
    """
    Calculates Earnings Per Share (EPS) CAGR.
    Supports 3, 5, or 10 year periods dynamically.

    Args:
        years (list[int]): Sequence of years.
        eps_values (list[Optional[float]]): Corresponding sequence of EPS values.
        period (int): Number of years for the CAGR window.

    Returns:
        CagrResult: Tuple of (CAGR value, Flag).
    """
    return _calculate_cagr_from_history(years, eps_values, period)
