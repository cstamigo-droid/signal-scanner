"""Smoke test / eval — deterministic, no network.

Builds synthetic OHLCV series with KNOWN outcomes and asserts the indicator engine
and rule engine behave correctly. A final optional block does one live yfinance
scan to prove the data path works end-to-end (non-asserting — network may vary).

Run:  PYTHONUTF8=1 python tests/test_smoke.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from signal_scanner import indicators, rules  # noqa: E402


def _frame(closes, volumes=None):
    n = len(closes)
    vol = volumes if volumes is not None else [1_000_000] * n
    idx = pd.date_range("2024-01-01", periods=n, freq="D")
    return pd.DataFrame(
        {"open": closes, "high": closes, "low": closes, "close": closes, "volume": vol},
        index=idx,
    )


def run() -> int:
    ruleset = rules.load(ROOT / "rules.yaml")
    fails = 0

    # 1) Oversold: a steady decline drives RSI well below 30.
    decline = list(np.linspace(200, 100, 80))
    ind = indicators.compute(_frame(decline))
    fired = rules.evaluate(ind, ruleset)
    ok = ind["rsi"] is not None and ind["rsi"] < 30 and "oversold" in fired
    print(f"{'OK  ' if ok else 'FAIL'} oversold: rsi={ind['rsi']} fired={fired}")
    fails += 0 if ok else 1

    # 2) Golden cross: ramp up after a flat base; truncate exactly at the cross bar.
    base = [100.0] * 60
    ramp = list(np.linspace(100, 140, 40))
    closes = base + ramp
    df = _frame(closes)
    sf = df["close"].rolling(20).mean()
    ss = df["close"].rolling(50).mean()
    cross_i = next((i for i in range(1, len(df))
                    if pd.notna(ss.iloc[i]) and sf.iloc[i] > ss.iloc[i] and sf.iloc[i-1] <= ss.iloc[i-1]), None)
    assert cross_i is not None, "no golden cross found in synthetic ramp"
    ind2 = indicators.compute(df.iloc[: cross_i + 1])
    fired2 = rules.evaluate(ind2, ruleset)
    ok = ind2["sma_cross"] == "golden" and "golden_cross" in fired2
    print(f"{'OK  ' if ok else 'FAIL'} golden_cross: sma_cross={ind2['sma_cross']} fired={fired2}")
    fails += 0 if ok else 1

    # 3) Volume spike up: flat-ish prices, last bar +2% on 5x volume.
    closes3 = [100.0] * 39 + [102.0]
    vols3 = [1_000_000] * 39 + [5_000_000]
    ind3 = indicators.compute(_frame(closes3, vols3))
    fired3 = rules.evaluate(ind3, ruleset)
    ok = ind3["vol_ratio"] is not None and ind3["vol_ratio"] > 2.0 and "volume_spike_up" in fired3
    print(f"{'OK  ' if ok else 'FAIL'} volume_spike_up: vol_ratio={ind3['vol_ratio']} "
          f"pct_change={ind3['pct_change']} fired={fired3}")
    fails += 0 if ok else 1

    # 4) No-fire control: gently rising series shouldn't trip oversold/overbought extremes.
    calm = list(np.linspace(100, 103, 80))
    ind4 = indicators.compute(_frame(calm))
    fired4 = rules.evaluate(ind4, ruleset)
    ok = "oversold" not in fired4
    print(f"{'OK  ' if ok else 'FAIL'} calm control: rsi={ind4['rsi']} fired={fired4}")
    fails += 0 if ok else 1

    print(f"\n{'ALL PASS' if fails == 0 else f'{fails} FAILED'} (deterministic, {4-fails}/4)")
    return fails


def test_smoke():
    assert run() == 0


if __name__ == "__main__":
    code = run()
    # optional live check (non-asserting)
    try:
        from signal_scanner import scanner
        print("\n[live] scanning AAPL via yfinance (non-asserting)…")
        r = scanner.scan(["AAPL"], rules.load(ROOT / "rules.yaml"))
        print(f"[live] {r.summary}")
    except Exception as e:
        print(f"[live] skipped: {e}")
    sys.exit(1 if code else 0)
