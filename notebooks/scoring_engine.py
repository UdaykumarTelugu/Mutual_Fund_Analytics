"""
Sprint Day 14 – Scoring Engine
Scores and ranks mutual funds using a multi-dimensional weighted model
built from KPIs computed in Days 08-13.

Weights (sum to 1.0):
  - Net Profit Margin      : 0.10
  - Operating Margin       : 0.10
  - ROE                    : 0.15
  - ROCE                   : 0.15
  - Debt-to-Equity (inv)   : 0.10  (lower D/E → higher score)
  - Revenue CAGR 3yr       : 0.10
  - PAT CAGR 3yr           : 0.10
  - FCF Conversion         : 0.10
  - CFO Quality            : 0.05
  - Composite Quality Score: 0.05
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Scoring weights – must sum to 1.0
# ---------------------------------------------------------------------------
WEIGHTS: Dict[str, float] = {
    "net_profit_margin":      0.10,
    "operating_margin":       0.10,
    "roe":                    0.15,
    "roce":                   0.15,
    "de_ratio_inv":           0.10,   # inverted  (lower D/E → better score)
    "revenue_cagr_3yr":       0.10,
    "pat_cagr_3yr":           0.10,
    "fcf_conversion":         0.10,
    "cfo_quality":            0.05,
    "composite_quality":      0.05,
}

assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9, "Scoring weights must sum to 1.0"


@dataclass
class FundScore:
    """Holds the normalised component scores and final rank for one fund-year."""
    fund_id: str
    fund_name: str
    financial_year: str
    sector: str
    component_scores: Dict[str, float] = field(default_factory=dict)
    weighted_score: float = 0.0
    rank: int = 0
    warnings: List[str] = field(default_factory=list)


def _normalise_percentile(values: List[Optional[float]]) -> List[float]:
    """
    Min-max normalise a list of values to [0, 100].
    None values map to 0.0.
    """
    clean = [(v if v is not None else 0.0) for v in values]
    lo, hi = min(clean), max(clean)
    if hi == lo:
        return [50.0 for _ in clean]      # all same → mid-score
    return [((v - lo) / (hi - lo)) * 100.0 for v in clean]


def _invert(score: float) -> float:
    """Invert a 0-100 score (used for D/E where lower is better)."""
    return 100.0 - score


def compute_scores(records: List[Dict]) -> List[FundScore]:
    """
    Compute weighted scores for a list of fund records.

    Each record must contain at minimum:
        fund_id, fund_name, financial_year, sector
    and optionally any of the KPI keys listed in WEIGHTS.

    Args:
        records: List of dicts, one per fund per year.

    Returns:
        List[FundScore] sorted by weighted_score descending with ranks assigned.
    """
    if not records:
        logger.warning("ScoringEngine: empty records list – no scores computed.")
        return []

    # -----------------------------------------------------------------------
    # 1. Extract each metric column
    # -----------------------------------------------------------------------
    raw: Dict[str, List[Optional[float]]] = {
        "net_profit_margin":  [r.get("net_profit_margin_pct") for r in records],
        "operating_margin":   [r.get("operating_profit_margin_pct") for r in records],
        "roe":                [r.get("return_on_equity_pct") for r in records],
        "roce":               [r.get("return_on_capital_employed_pct") for r in records],
        "de_ratio_inv":       [r.get("debt_to_equity") for r in records],   # will invert later
        "revenue_cagr_3yr":   [r.get("revenue_cagr_3yr") for r in records],
        "pat_cagr_3yr":       [r.get("pat_cagr_3yr") for r in records],
        "fcf_conversion":     [r.get("fcf_conversion") for r in records],
        "cfo_quality":        [r.get("cfo_quality") for r in records],
        "composite_quality":  [r.get("composite_quality_score") for r in records],
    }

    # -----------------------------------------------------------------------
    # 2. Normalise each metric to [0, 100]
    # -----------------------------------------------------------------------
    normalised: Dict[str, List[float]] = {}
    for metric, vals in raw.items():
        norm = _normalise_percentile(vals)
        if metric == "de_ratio_inv":
            norm = [_invert(v) for v in norm]   # lower D/E → better
        normalised[metric] = norm

    # -----------------------------------------------------------------------
    # 3. Build FundScore objects with weighted totals
    # -----------------------------------------------------------------------
    fund_scores: List[FundScore] = []
    for idx, record in enumerate(records):
        fs = FundScore(
            fund_id=str(record.get("fund_id", record.get("company_id", "UNKNOWN"))),
            fund_name=str(record.get("fund_name", record.get("company_name", "UNKNOWN"))),
            financial_year=str(record.get("financial_year", "")),
            sector=str(record.get("sector", "")),
        )

        weighted_total = 0.0
        for metric, weight in WEIGHTS.items():
            score = normalised[metric][idx]
            fs.component_scores[metric] = round(score, 4)
            weighted_total += score * weight

        fs.weighted_score = round(weighted_total, 4)

        # Warn on missing critical metrics
        missing = [m for m in ("roe", "roce", "net_profit_margin")
                   if raw[m][idx] is None]
        if missing:
            msg = f"Missing KPIs {missing} for {fs.fund_id} FY{fs.financial_year}"
            fs.warnings.append(msg)
            logger.warning(msg)

        fund_scores.append(fs)

    # -----------------------------------------------------------------------
    # 4. Sort and assign ranks
    # -----------------------------------------------------------------------
    fund_scores.sort(key=lambda x: x.weighted_score, reverse=True)
    for rank_idx, fs in enumerate(fund_scores, start=1):
        fs.rank = rank_idx
        logger.info(
            f"Rank {fs.rank} | {fs.fund_id} | {fs.fund_name} | "
            f"FY {fs.financial_year} | Score {fs.weighted_score:.4f}"
        )

    return fund_scores
