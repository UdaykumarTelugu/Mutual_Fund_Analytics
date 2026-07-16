"""
Module for calculating core financial ratios.
Includes profitability, return, leverage, and efficiency ratios.
"""

import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


def _safe_divide(numerator: float, denominator: float) -> Optional[float]:
    """
    Safely divides two numbers, handling divide-by-zero conditions.

    Args:
        numerator (float): The numerator.
        denominator (float): The denominator.

    Returns:
        Optional[float]: The quotient, or None if the denominator is zero.
    """
    if denominator == 0:
        logger.warning("Divide by zero encountered. Returning None.")
        return None
    return numerator / denominator


def _handle_financial_sector(ratio_name: str, value: Optional[float], sector: str) -> Optional[float]:
    """Applies sector benchmark handling for Financial companies."""
    if sector.lower() in ("financial", "financials", "banking"):
        logger.info(f"Applying sector benchmark handling for {ratio_name} (Financials).")
    return value


def calculate_net_profit_margin(net_profit: float, revenue: float, sector: str = "") -> Optional[float]:
    """
    Calculates the Net Profit Margin.

    Formula: (Net Profit / Sales) * 100

    Args:
        net_profit (float): Total net profit.
        revenue (float): Total revenue (Sales).
        sector (str, optional): Industry sector. Defaults to "".

    Returns:
        Optional[float]: Net Profit Margin, or None if revenue is zero.
    """
    val = _safe_divide(net_profit, revenue)
    if val is not None:
        val = val * 100
    return _handle_financial_sector("Net Profit Margin", val, sector)


def calculate_operating_profit_margin(
    operating_profit: float, 
    revenue: float, 
    company_id: str = "UNKNOWN",
    company_name: str = "UNKNOWN",
    financial_year: str = "UNKNOWN",
    opm_percentage: Optional[float] = None,
    sector: str = ""
) -> Optional[float]:
    """
    Calculates the Operating Profit Margin.

    Formula: (Operating Profit / Sales) * 100

    Args:
        operating_profit (float): Operating profit (EBIT).
        revenue (float): Total revenue (Sales).
        company_id (str, optional): ID of the company. Defaults to "UNKNOWN".
        company_name (str, optional): Name of the company. Defaults to "UNKNOWN".
        financial_year (str, optional): Financial year. Defaults to "UNKNOWN".
        opm_percentage (Optional[float]): Expected OPM percentage to cross-check.
        sector (str, optional): Industry sector. Defaults to "".

    Returns:
        Optional[float]: Operating Profit Margin, or None if revenue is zero.
    """
    calculated_opm_ratio = _safe_divide(operating_profit, revenue)
    if calculated_opm_ratio is None:
        return None
        
    calculated_opm = calculated_opm_ratio * 100
    
    if opm_percentage is not None:
        diff = abs(calculated_opm - opm_percentage)
        if diff > 1.0:
            logger.warning(
                f"OPM mismatch >1%: Company ID: {company_id}, Company Name: {company_name}, "
                f"FY: {financial_year}, Expected OPM: {opm_percentage:.4f}, "
                f"Calculated OPM: {calculated_opm:.4f}, Difference: {diff:.4f}"
            )
            
    return _handle_financial_sector("Operating Profit Margin", calculated_opm, sector)


def calculate_return_on_equity(
    net_income: float, 
    equity: float, 
    reserves: float = 0.0,
    sector: str = ""
) -> Optional[float]:
    """
    Calculates the Return on Equity (ROE).

    Formula: Net Profit / (Equity Capital + Reserves) * 100

    Args:
        net_income (float): Net income of the company.
        equity (float): Total share capital or equity.
        reserves (float): Reserves and surplus.
        sector (str, optional): Industry sector. Defaults to "".

    Returns:
        Optional[float]: ROE, or None if equity + reserves <= 0.
    """
    total_equity = equity + reserves
    if total_equity <= 0:
        logger.warning("Equity + Reserves <= 0 encountered. ROE calculation returning None.")
        return None
    val = _safe_divide(net_income, total_equity)
    if val is not None:
        val = val * 100
    return _handle_financial_sector("Return on Equity", val, sector)


def calculate_return_on_capital_employed(
    ebit: float, 
    equity: float, 
    reserves: float, 
    borrowings: float, 
    sector: str = ""
) -> Optional[float]:
    """
    Calculates the Return on Capital Employed (ROCE).

    Formula: EBIT / (Equity + Reserves + Borrowings) * 100

    Args:
        ebit (float): Earnings before interest and taxes.
        equity (float): Share capital or equity.
        reserves (float): Reserves and surplus.
        borrowings (float): Total borrowings (debt).
        sector (str, optional): Industry sector. Defaults to "".

    Returns:
        Optional[float]: ROCE, or None if denominator is zero.
    """
    capital_employed = equity + reserves + borrowings
    val = _safe_divide(ebit, capital_employed)
    if val is not None:
        val = val * 100
    return _handle_financial_sector("Return on Capital Employed", val, sector)


def calculate_return_on_assets(net_income: float, total_assets: float, sector: str = "") -> Optional[float]:
    """
    Calculates the Return on Assets (ROA).

    Formula: Net Profit / Total Assets * 100

    Args:
        net_income (float): Net income.
        total_assets (float): Total assets.
        sector (str, optional): Industry sector. Defaults to "".

    Returns:
        Optional[float]: ROA, or None if total assets are zero.
    """
    val = _safe_divide(net_income, total_assets)
    if val is not None:
        val = val * 100
    return _handle_financial_sector("Return on Assets", val, sector)


def calculate_debt_to_equity(
    borrowings: float, 
    equity_capital: float, 
    reserves: float, 
    sector: str = ""
) -> Optional[float]:
    """
    Calculates the Debt-to-Equity (D/E) ratio.

    Formula: Borrowings / (Equity Capital + Reserves)

    Args:
        borrowings (float): Total borrowings.
        equity_capital (float): Share capital.
        reserves (float): Reserves and surplus.
        sector (str, optional): The industry sector of the company. Defaults to "".

    Returns:
        Optional[float]: Debt to Equity ratio, 0.0 if debt-free, or None for invalid inputs.
    """
    if borrowings == 0:
        return 0.0

    if sector.lower() in ("financial", "financials", "banking"):
        logger.info("Financials sector exception: Standard D/E may not be meaningful.")

    total_equity = equity_capital + reserves
    if total_equity <= 0 and borrowings > 0:
        logger.warning("Negative or zero equity with positive borrowings encountered in Debt to Equity calculation.")
        return None

    return _safe_divide(borrowings, total_equity)

def check_high_leverage(debt_to_equity: Optional[float], sector: str = "") -> bool:
    """
    Checks if a company has high leverage.

    Args:
        debt_to_equity (Optional[float]): Debt-to-Equity ratio.
        sector (str, optional): Industry sector. Defaults to "".

    Returns:
        bool: True if high leverage, False otherwise.
    """
    if debt_to_equity is None:
        return False
        
    if sector.lower() in ("financial", "financials", "banking"):
        logger.info("Suppressing high leverage warning for Financials company.")
        return False
        
    if debt_to_equity > 5.0:
        logger.warning(f"High leverage flagged (D/E: {debt_to_equity:.2f}).")
        return True
        
    return False


def calculate_interest_coverage_ratio(
    operating_profit: float, 
    other_income: float, 
    interest_expense: float
) -> Tuple[Optional[float], Optional[str]]:
    """
    Calculates the Interest Coverage Ratio (ICR).

    Formula: (Operating Profit + Other Income) / Interest Expense

    Args:
        operating_profit (float): Operating profit (EBIT).
        other_income (float): Other income.
        interest_expense (float): Interest expenses.

    Returns:
        Tuple[Optional[float], Optional[str]]: A tuple containing the ICR and an optional label.
    """
    if interest_expense == 0:
        logger.info("Debt-free company: Zero interest expense encountered.")
        return None, "Debt Free"
        
    icr = _safe_divide(operating_profit + other_income, interest_expense)
    return icr, None

def check_icr_warning(icr: Optional[float]) -> bool:
    """
    Checks if the Interest Coverage Ratio is too low.

    Args:
        icr (Optional[float]): Interest Coverage Ratio.

    Returns:
        bool: True if ICR < 1.5, False otherwise.
    """
    if icr is None:
        return False
        
    if icr < 1.5:
        return True
        
    return False


def calculate_net_debt(borrowings: float, investments: float) -> float:
    """
    Calculates the Net Debt.

    Formula: Borrowings - Investments

    Args:
        borrowings (float): Total short-term and long-term debt.
        investments (float): Total investments (proxy for liquid assets).

    Returns:
        float: Net debt value.
    """
    return borrowings - investments


def calculate_asset_turnover(sales: float, total_assets: float, sector: str = "") -> Optional[float]:
    """
    Calculates the Asset Turnover ratio.
    
    Formula: Sales / Total Assets

    Args:
        sales (float): Total revenue or net sales.
        total_assets (float): Total assets.
        sector (str, optional): The industry sector. Defaults to "".

    Returns:
        Optional[float]: Asset Turnover ratio, or None if assets are zero.
    """
    if sector.lower() in ("financial", "financials", "banking"):
        logger.info("Asset turnover is generally not applicable to the Financials sector.")
        return None

    return _safe_divide(sales, total_assets)
