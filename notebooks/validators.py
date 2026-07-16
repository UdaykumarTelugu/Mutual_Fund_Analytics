import logging
from typing import Optional, List
from src.utils.logger import log_anomaly, AnomalyCategory
from src.analytics.benchmark import is_financial_sector

logger = logging.getLogger(__name__)

def validate_financial_inputs(
    company_id: str,
    company_name: str,
    financial_year: str,
    sector: str,
    source_value: Optional[float],
    calc_value: Optional[float],
    denominator: Optional[float]
) -> bool:
    """
    General validation rule checker.
    Validate: Missing source values, Missing calculated values, Negative denominator cases.
    Does not stop execution (always returns True).
    """
    if source_value is None:
        logger.warning(f"Validation: Missing benchmark field for {company_id} FY{financial_year}")
        log_anomaly(
            company_id=company_id, company_name=company_name, financial_year=financial_year, sector=sector,
            ratio_name="General", calculated_value=str(calc_value), source_value="None", difference="N/A",
            category=AnomalyCategory.MISSING_DATA, reason="Missing benchmark field", suggested_resolution="Ignore or fetch source"
        )
        
    if calc_value is None:
        logger.warning(f"Validation: Missing calculated value for {company_id} FY{financial_year}")
        log_anomaly(
            company_id=company_id, company_name=company_name, financial_year=financial_year, sector=sector,
            ratio_name="General", calculated_value="None", source_value=str(source_value), difference="N/A",
            category=AnomalyCategory.MISSING_DATA, reason="Missing calculated field", suggested_resolution="Check inputs"
        )

    if denominator is not None and denominator < 0:
        logger.warning(f"Validation: Negative denominator case for {company_id} FY{financial_year}")
        log_anomaly(
            company_id=company_id, company_name=company_name, financial_year=financial_year, sector=sector,
            ratio_name="General", calculated_value=str(calc_value), source_value=str(source_value), difference="N/A",
            category=AnomalyCategory.VALIDATION_FAILURE, reason="Negative denominator", suggested_resolution="Verify accounting principles"
        )
        
    return True

def check_duplicate_years(years: List[str]) -> List[str]:
    """Logs duplicate financial years and returns deduplicated sorted list."""
    seen = set()
    dupes = set()
    for y in years:
        if y in seen:
            dupes.add(y)
        seen.add(y)
        
    if dupes:
        logger.warning(f"Validation: Duplicate financial years detected: {dupes}")
        
    return sorted(list(seen))
