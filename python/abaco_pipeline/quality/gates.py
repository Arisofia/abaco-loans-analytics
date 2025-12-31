"""Quality gates (v2 scaffold)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class QualityResult:
    completeness: float
    freshness_hours: float


def compute_freshness_hours(as_of: datetime, now: datetime | None = None) -> float:
    now_dt = now or datetime.now(timezone.utc)
    delta = now_dt - as_of
    return delta.total_seconds() / 3600.0
