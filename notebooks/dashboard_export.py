"""
Sprint Day 14 – Dashboard Export Engine
Produces CSV and JSON exports of the ranked fund scorecard for downstream
dashboard consumption.

Output files:
  output/fund_rankings.csv
  output/fund_rankings.json
  output/fund_scorecard_summary.csv
"""

import csv
import json
import logging
import os
from typing import Dict, List

from src.analytics.scoring_engine import FundScore

logger = logging.getLogger(__name__)

OUTPUT_DIR = "output"
RANKINGS_CSV = os.path.join(OUTPUT_DIR, "fund_rankings.csv")
RANKINGS_JSON = os.path.join(OUTPUT_DIR, "fund_rankings.json")
SCORECARD_CSV = os.path.join(OUTPUT_DIR, "fund_scorecard_summary.csv")


def _ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# CSV Export
# ---------------------------------------------------------------------------
def export_rankings_csv(fund_scores: List[FundScore]) -> bool:
    """
    Export ranked fund scores to CSV.

    Args:
        fund_scores: Pre-ranked list of FundScore objects.

    Returns:
        True on success, False on failure.
    """
    _ensure_output_dir()
    if not fund_scores:
        logger.warning("DashboardExport: No fund scores to export (CSV).")
        return False

    fieldnames = [
        "rank", "fund_id", "fund_name", "financial_year", "sector",
        "weighted_score",
        "net_profit_margin", "operating_margin", "roe", "roce",
        "de_ratio_inv", "revenue_cagr_3yr", "pat_cagr_3yr",
        "fcf_conversion", "cfo_quality", "composite_quality",
    ]

    try:
        with open(RANKINGS_CSV, mode="w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            for fs in fund_scores:
                row = {
                    "rank":             fs.rank,
                    "fund_id":          fs.fund_id,
                    "fund_name":        fs.fund_name,
                    "financial_year":   fs.financial_year,
                    "sector":           fs.sector,
                    "weighted_score":   fs.weighted_score,
                }
                row.update(fs.component_scores)
                writer.writerow(row)
        logger.info(f"DashboardExport: Rankings CSV written → {RANKINGS_CSV}")
        return True
    except Exception as exc:
        logger.error(f"DashboardExport: CSV export failed – {exc}")
        return False


# ---------------------------------------------------------------------------
# JSON Export
# ---------------------------------------------------------------------------
def export_rankings_json(fund_scores: List[FundScore]) -> bool:
    """
    Export ranked fund scores to JSON.

    Args:
        fund_scores: Pre-ranked list of FundScore objects.

    Returns:
        True on success, False on failure.
    """
    _ensure_output_dir()
    if not fund_scores:
        logger.warning("DashboardExport: No fund scores to export (JSON).")
        return False

    payload = []
    for fs in fund_scores:
        payload.append({
            "rank":             fs.rank,
            "fund_id":          fs.fund_id,
            "fund_name":        fs.fund_name,
            "financial_year":   fs.financial_year,
            "sector":           fs.sector,
            "weighted_score":   fs.weighted_score,
            "component_scores": fs.component_scores,
            "warnings":         fs.warnings,
        })

    try:
        with open(RANKINGS_JSON, mode="w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, ensure_ascii=False)
        logger.info(f"DashboardExport: Rankings JSON written → {RANKINGS_JSON}")
        return True
    except Exception as exc:
        logger.error(f"DashboardExport: JSON export failed – {exc}")
        return False


# ---------------------------------------------------------------------------
# Scorecard Summary CSV (top-line KPIs only)
# ---------------------------------------------------------------------------
def export_scorecard_summary_csv(fund_scores: List[FundScore]) -> bool:
    """
    Export a lightweight scorecard summary suitable for a dashboard table.

    Args:
        fund_scores: Pre-ranked list of FundScore objects.

    Returns:
        True on success, False on failure.
    """
    _ensure_output_dir()
    if not fund_scores:
        logger.warning("DashboardExport: No fund scores to export (scorecard).")
        return False

    fieldnames = [
        "rank", "fund_id", "fund_name", "financial_year", "sector",
        "weighted_score", "roe", "roce", "net_profit_margin",
        "revenue_cagr_3yr", "pat_cagr_3yr",
    ]

    try:
        with open(SCORECARD_CSV, mode="w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for fs in fund_scores:
                row = {
                    "rank":             fs.rank,
                    "fund_id":          fs.fund_id,
                    "fund_name":        fs.fund_name,
                    "financial_year":   fs.financial_year,
                    "sector":           fs.sector,
                    "weighted_score":   fs.weighted_score,
                }
                row.update(fs.component_scores)
                writer.writerow(row)
        logger.info(f"DashboardExport: Scorecard summary written → {SCORECARD_CSV}")
        return True
    except Exception as exc:
        logger.error(f"DashboardExport: Scorecard CSV export failed – {exc}")
        return False


# ---------------------------------------------------------------------------
# Convenience: run all exports
# ---------------------------------------------------------------------------
def export_all(fund_scores: List[FundScore]) -> Dict[str, bool]:
    """Run all three exports and return a status dict."""
    return {
        "rankings_csv":     export_rankings_csv(fund_scores),
        "rankings_json":    export_rankings_json(fund_scores),
        "scorecard_csv":    export_scorecard_summary_csv(fund_scores),
    }
