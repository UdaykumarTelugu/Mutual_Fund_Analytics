"""
Module for calculating Cash Flow Key Performance Indicators (KPIs).
Includes FCF, CapEx Intensity, FCF Conversion, CFO Quality Score,
and Capital Allocation Pattern classification.
"""

import enum
import logging
import csv
import os
from typing import Optional, Tuple, List

logger = logging.getLogger(__name__)


class CapitalAllocationPattern(enum.Enum):
    """Enumeration of Capital Allocation Pattern Labels."""
    REINVESTOR = "Reinvestor"
    SHAREHOLDER_RETURNS = "Shareholder Returns"
    LIQUIDATING_ASSETS = "Liquidating Assets"
    DISTRESS_SIGNAL = "Distress Signal"
    GROWTH_FUNDED_BY_DEBT = "Growth Funded by Debt"
    CASH_ACCUMULATOR = "Cash Accumulator"
    PRE_REVENUE = "Pre-Revenue"
    MIXED = "Mixed"


def _safe_divide(numerator: float, denominator: float) -> Optional[float]:
    """Helper function for safe division."""
    if denominator == 0:
        return None
    return numerator / denominator


def calculate_free_cash_flow(cfo: Optional[float], cfi: Optional[float]) -> Optional[float]:
    """
    Calculates Free Cash Flow (FCF).

    Formula: Operating Cash Flow + Investing Cash Flow

    Args:
        cfo (float): Cash Flow from Operations.
        cfi (float): Cash Flow from Investing.

    Returns:
        Optional[float]: Free Cash Flow.
    """
    if cfo is None or cfi is None:
        logger.warning("Missing cash flow data for FCF calculation.")
        return None
    return cfo + cfi


def calculate_capex_intensity(cfi: Optional[float], sales: Optional[float]) -> Tuple[Optional[float], Optional[str]]:
    """
    Calculates Capital Expenditure Intensity.

    Formula: Absolute(Investing Cash Flow) / Sales * 100

    Args:
        cfi (float): Cash Flow from Investing.
        sales (float): Total Revenue/Sales.

    Returns:
        Tuple[Optional[float], Optional[str]]: CapEx Intensity ratio and classification label.
    """
    if cfi is None or sales is None:
        logger.warning("Missing data for CapEx Intensity.")
        return None, None
        
    ratio = _safe_divide(abs(cfi), sales)
    if ratio is None:
        logger.warning("Sales equals zero encountered in CapEx Intensity.")
        return None, None
        
    intensity = ratio * 100
    if intensity < 3.0:
        label = "Asset Light"
    elif 3.0 <= intensity <= 8.0:
        label = "Moderate"
    else:
        label = "Capital Intensive"
        
    return intensity, label


def calculate_fcf_conversion(fcf: Optional[float], operating_profit: Optional[float]) -> Optional[float]:
    """
    Calculates Free Cash Flow Conversion.

    Formula: Free Cash Flow / Operating Profit * 100

    Args:
        fcf (float): Free Cash Flow.
        operating_profit (float): Operating Profit.

    Returns:
        Optional[float]: FCF Conversion ratio, or None if operating profit is zero.
    """
    if fcf is None or operating_profit is None:
        logger.warning("Missing data for FCF Conversion.")
        return None
        
    ratio = _safe_divide(fcf, operating_profit)
    if ratio is None:
        logger.warning("Operating Profit equals zero encountered in FCF Conversion.")
        return None
        
    return ratio * 100


def calculate_cfo_quality_score(cfos: List[Optional[float]], pats: List[Optional[float]]) -> Tuple[Optional[float], Optional[str]]:
    """
    Calculates CFO Quality Score.

    Formula: Average over the latest available 5 years: CFO / PAT

    Args:
        cfos (List[Optional[float]]): Cash Flow from Operations history.
        pats (List[Optional[float]]): Profit After Tax history.

    Returns:
        Tuple[Optional[float], Optional[str]]: CFO Quality Score and classification label.
    """
    valid_ratios = []
    for c, p in zip(cfos, pats):
        if c is not None and p is not None and p != 0:
            valid_ratios.append(c / p)
        elif p == 0:
            logger.warning("PAT equals zero encountered while calculating CFO quality score.")
    
    if not valid_ratios:
        logger.warning("No valid years available for CFO quality score.")
        return None, None
        
    avg_score = sum(valid_ratios) / len(valid_ratios)
    
    if avg_score > 1.0:
        label = "High Quality"
    elif 0.5 <= avg_score <= 1.0:
        label = "Moderate"
    else:
        label = "Accrual Risk"
        
    return avg_score, label


def determine_capital_allocation_pattern(
    cfo: Optional[float],
    cfi: Optional[float],
    cff: Optional[float],
    cfo_quality_label: Optional[str] = None
) -> CapitalAllocationPattern:
    """
    Determines the Capital Allocation Pattern label based on cash flow activities.

    Args:
        cfo (float): Cash Flow from Operations.
        cfi (float): Cash Flow from Investing.
        cff (float): Cash Flow from Financing.
        cfo_quality_label (str, optional): The CFO quality label for further precision.

    Returns:
        CapitalAllocationPattern: The classified pattern label from the predefined Enum.
    """
    if cfo is None or cfi is None or cff is None:
        logger.warning("Missing cash flow data for pattern classification.")
        return CapitalAllocationPattern.MIXED

    # Determine signs using strict inequalities for positive (+)
    cfo_sign = "+" if cfo > 0 else "-"
    cfi_sign = "+" if cfi > 0 else "-"
    cff_sign = "+" if cff > 0 else "-"

    pattern = (cfo_sign, cfi_sign, cff_sign)

    if pattern == ("+", "-", "-"):
        if cfo_quality_label == "High Quality":
            return CapitalAllocationPattern.SHAREHOLDER_RETURNS
        return CapitalAllocationPattern.REINVESTOR
    elif pattern == ("+", "+", "-"):
        return CapitalAllocationPattern.LIQUIDATING_ASSETS
    elif pattern == ("-", "+", "+"):
        return CapitalAllocationPattern.DISTRESS_SIGNAL
    elif pattern == ("-", "-", "+"):
        return CapitalAllocationPattern.GROWTH_FUNDED_BY_DEBT
    elif pattern == ("+", "+", "+"):
        return CapitalAllocationPattern.CASH_ACCUMULATOR
    elif pattern == ("-", "-", "-"):
        return CapitalAllocationPattern.PRE_REVENUE
    elif pattern == ("+", "-", "+"):
        return CapitalAllocationPattern.MIXED
    
    return CapitalAllocationPattern.MIXED


def generate_capital_allocation_csv(records: List[dict], output_path: str = "output/capital_allocation.csv"):
    """
    Generates the capital allocation CSV report.
    
    Args:
        records: List of dictionaries containing company cash flow data.
        output_path: Path to the output CSV file.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    fieldnames = [
        "company_id", "company_name", "financial_year",
        "cfo", "cfi", "cff",
        "cfo_sign", "cfi_sign", "cff_sign",
        "pattern_label", "cfo_quality",
        "free_cash_flow", "capex_intensity"
    ]
    
    try:
        with open(output_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for record in records:
                cfo = record.get("cfo")
                cfi = record.get("cfi")
                cff = record.get("cff")
                
                cfo_sign = "+" if cfo is not None and cfo > 0 else ("-" if cfo is not None else "")
                cfi_sign = "+" if cfi is not None and cfi > 0 else ("-" if cfi is not None else "")
                cff_sign = "+" if cff is not None and cff > 0 else ("-" if cff is not None else "")
                
                row = {
                    "company_id": record.get("company_id", ""),
                    "company_name": record.get("company_name", ""),
                    "financial_year": record.get("financial_year", ""),
                    "cfo": cfo if cfo is not None else "",
                    "cfi": cfi if cfi is not None else "",
                    "cff": cff if cff is not None else "",
                    "cfo_sign": cfo_sign,
                    "cfi_sign": cfi_sign,
                    "cff_sign": cff_sign,
                    "pattern_label": record.get("pattern_label", ""),
                    "cfo_quality": record.get("cfo_quality", ""),
                    "free_cash_flow": record.get("free_cash_flow", ""),
                    "capex_intensity": record.get("capex_intensity", "")
                }
                writer.writerow(row)
    except Exception as e:
        logger.error(f"Unexpected exception during CSV generation: {e}")
