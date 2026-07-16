

import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import logging
from typing import Optional, Tuple
from src.utils.logger import log_anomaly, AnomalyCategory

logger = logging.getLogger(__name__)

def is_financial_sector(sector: Optional[str]) -> bool:
    """Checks whether the given sector string belongs to the financial sector.

    Args:
        sector (Optional[str]): Sector label for the company.

    Returns:
        bool: True if the sector is financial (bank, NBFC, insurance, etc.).
    """
    if not sector:
        return False
    financial_keywords = ["bank", "nbfc", "insurance", "financial services", "financials"]
    s = sector.lower()
    return any(kw in s for kw in financial_keywords)

def check_leverage_exception(debt_to_equity: Optional[float], sector: Optional[str]) -> bool:
    """
    Checks if high leverage warning should be suppressed.
    Returns True if suppressed (is financial), False otherwise.
    """
    if debt_to_equity is None:
        return False
        
    if is_financial_sector(sector):
        # Document behaviour: Suppressing the High Debt-to-Equity warning.
        # Do not mark these companies as highly leveraged solely because of structurally high leverage.
        logger.info(f"Financial sector exception triggered: Suppressing leverage warning for sector '{sector}'.")
        return True
    return False

def validate_roce_benchmark(
    company_id: str,
    company_name: str,
    financial_year: str,
    sector: str,
    calculated_roce: Optional[float],
    source_roce: Optional[float]
) -> Optional[float]:
    """
    Compare calculated ROCE vs source ROCE. 
    If absolute difference > 5 percentage points, log anomaly.
    Always returns the analytical (calculated) value.
    """
    if calculated_roce is not None and source_roce is not None:
        diff = abs(calculated_roce - source_roce)
        if diff > 5.0:
            log_anomaly(
                company_id=company_id,
                company_name=company_name,
                financial_year=financial_year,
                sector=sector,
                ratio_name="ROCE",
                calculated_value=f"{calculated_roce:.4f}",
                source_value=f"{source_roce:.4f}",
                difference=f"{diff:.4f}",
                category=AnomalyCategory.FORMULA_DIFFERENCE,
                reason="Calculated ROCE deviates from source by > 5%",
                suggested_resolution="Review numerator/denominator inclusions (e.g. leases/goodwill)"
            )
            logger.warning(f"ROCE mismatch for {company_id} FY{financial_year}")
    return calculated_roce

def validate_roe_benchmark(
    company_id: str,
    company_name: str,
    financial_year: str,
    sector: str,
    calculated_roe: Optional[float],
    source_roe: Optional[float]
) -> Tuple[Optional[float], Optional[float]]:
    """
    Compare calculated ROE vs source ROE.
    Returns (calculated_roe, source_roe).
    """
    if calculated_roe is not None and source_roe is not None:
        diff = abs(calculated_roe - source_roe)
        if diff > 1.0:
            # "Some source values may be anomalous... For analytics always use calculated ROE... For display retain original"
            log_anomaly(
                company_id=company_id,
                company_name=company_name,
                financial_year=financial_year,
                sector=sector,
                ratio_name="ROE",
                calculated_value=f"{calculated_roe:.4f}",
                source_value=f"{source_roe:.4f}",
                difference=f"{diff:.4f}",
                category=AnomalyCategory.DATA_SOURCE_ISSUE,
                reason="Source ROE anomalous or calculated ROE deviates",
                suggested_resolution="Use calculated ROE for analytics"
            )
            logger.warning(f"ROE mismatch for {company_id} FY{financial_year}")
            
    return calculated_roe, source_roe

def auto_categorise_anomaly(
    ratio_name: str,
    calc: Optional[float],
    source: Optional[float],
    sector: str
) -> AnomalyCategory:
    """Automatically categorises a benchmark anomaly based on the magnitude of divergence.

    Args:
        ratio_name (str): Name of the financial ratio being categorised.
        calc (Optional[float]): Calculated value.
        source (Optional[float]): Source/reference value.
        sector (str): Company sector label.

    Returns:
        AnomalyCategory: The best-matching anomaly category.
    """
    if calc is None or source is None:
        return AnomalyCategory.MISSING_DATA
    if is_financial_sector(sector) and ratio_name in ("Debt_to_Equity", "Asset_Turnover"):
        return AnomalyCategory.SECTOR_EXCEPTION

    diff = abs(calc - source)
    if diff > 10.0:
        return AnomalyCategory.DATA_SOURCE_ISSUE
    elif diff > 0.0:
        return AnomalyCategory.FORMULA_DIFFERENCE

    return AnomalyCategory.UNKNOWN
if __name__ == "__main__":
    print("Testing benchmark module...")

    print(is_financial_sector("Banking"))
    print(is_financial_sector("IT"))

    print(check_leverage_exception(6.5, "Banking"))
    print(check_leverage_exception(6.5, "Information Technology"))
    