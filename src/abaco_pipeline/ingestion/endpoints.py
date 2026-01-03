"""Endpoint registry helpers (v2 scaffold)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass(frozen=True)
class Endpoint:
    name: str
    path: str


def load_endpoints(cfg: Dict[str, Any]) -> List[Endpoint]:
    endpoints_cfg = (cfg.get("cascade") or {}).get("endpoints") or {}
    endpoints: list[Endpoint] = []
    for name, path in endpoints_cfg.items():
        endpoints.append(Endpoint(name=str(name), path=str(path)))
    return endpoints
