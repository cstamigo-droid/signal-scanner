"""Rule engine — declarative YAML conditions over computed indicators.

A ruleset is a list of named rules; a rule fires when ALL its conditions are true
(AND semantics). Clients edit rules.yaml — no code changes. Example:

    rules:
      - name: oversold_dip
        when:
          - {indicator: rsi, op: "<", value: 30}
          - {indicator: pct_from_52w_high, op: "<", value: -20}
      - name: golden_cross
        when:
          - {indicator: sma_cross, op: "==", value: golden}
"""
from __future__ import annotations

import operator
from pathlib import Path
from typing import Any

_OPS = {
    "<": operator.lt, "<=": operator.le, ">": operator.gt, ">=": operator.ge,
    "==": operator.eq, "!=": operator.ne,
}


def load(path: str | Path) -> list[dict[str, Any]]:
    """Load and validate a ruleset YAML. Returns a list of rule dicts."""
    import yaml
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"ruleset not found: {p}")
    doc = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    rules = doc.get("rules", [])
    for r in rules:
        if "name" not in r or "when" not in r:
            raise ValueError(f"rule missing 'name'/'when': {r}")
        for c in r["when"]:
            if c.get("op") not in _OPS:
                raise ValueError(f"unknown op {c.get('op')!r} in rule {r['name']}")
    return rules


def _cond_true(cond: dict[str, Any], ind: dict[str, Any]) -> bool:
    val = ind.get(cond["indicator"])
    if val is None:
        return False
    target = cond["value"]
    op = _OPS[cond["op"]]
    try:
        # numeric compare when both look numeric; else string compare for ==/!=
        if isinstance(val, (int, float)) and isinstance(target, (int, float)):
            return bool(op(val, target))
        return bool(op(str(val), str(target)))
    except TypeError:
        return False


def evaluate(indicators: dict[str, Any], rules: list[dict[str, Any]]) -> list[str]:
    """Return the names of rules whose every condition is satisfied."""
    fired = []
    for r in rules:
        if all(_cond_true(c, indicators) for c in r["when"]):
            fired.append(r["name"])
    return fired
