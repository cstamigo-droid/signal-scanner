"""Uniform Result type (reused from mcp-factory)."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


@dataclass
class Result:
    source: str
    ok: bool
    summary: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    score: float | None = None
    confidence: float | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def failed(cls, source: str, error: str) -> "Result":
        return cls(source=source, ok=False, summary=f"no data ({error})", error=error)
