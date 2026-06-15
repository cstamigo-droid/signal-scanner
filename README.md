# signal-scanner — rule-based stock/crypto screener with alerts

Define a **watchlist** and a **ruleset** (plain YAML); the scanner pulls market data,
computes indicators, and tells you which symbols match — on the console, in **Telegram**,
or from any **MCP host** (Claude Desktop / Claude Code).

> Built once, reskinned per client: swap `watchlist.txt` + `rules.yaml`, ship.

## Why it's different
- **Keyless by default.** Market data via yfinance — no API key. Works for stocks, ETFs, FX (`EURUSD=X`) and crypto (`BTC-USD`). Demo it anywhere.
- **No-code rules.** Clients edit `rules.yaml` (conditions on indicators) — never the code.
- **Honest signals.** Indicators are computed from *closed* bars (no look-ahead); a symbol with no data is reported, never faked.
- **Delivery that degrades.** Telegram alerts when a bot token is set; otherwise prints to console. The scanner always runs.
- **Three surfaces, one engine.** CLI (one-shot or `--watch`), Telegram push, and an MCP `scan` tool.

## Indicators & rules
Indicators per symbol: `price`, `pct_change`, `rsi`, `sma_fast`, `sma_slow`,
`sma_cross` (`golden`/`death`), `vol_ratio` (vs 20-day avg), `pct_from_52w_high`, `pct_from_52w_low`.

A rule fires when **all** its conditions are true:
```yaml
rules:
  - name: oversold
    when:
      - {indicator: rsi, op: "<", value: 30}
  - name: volume_spike_up
    when:
      - {indicator: vol_ratio, op: ">", value: 2.0}
      - {indicator: pct_change, op: ">", value: 1.0}
```

## Quickstart
```bash
pip install -r requirements.txt
PYTHONUTF8=1 python tests/test_smoke.py     # deterministic, no network — proves the engine

python -m signal_scanner                    # scan the watchlist once, print matches
python -m signal_scanner AAPL MSFT BTC-USD  # scan ad-hoc symbols
python -m signal_scanner --watch            # loop every SCAN_INTERVAL_S (default 15m)
python -m signal_scanner --notify           # also push matches to Telegram (if configured)
```

### Telegram (optional)
Create a bot with @BotFather, get the token; get your chat id from @userinfobot. Then in `.env`:
```
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
```

### As an MCP server (Claude Desktop)
```json
{
  "signal-scanner": {
    "command": "python",
    "args": ["-m", "signal_scanner.server"],
    "cwd": "C:/path/to/signal-scanner"
  }
}
```
Then ask Claude: *"Run my scanner"* or *"Any signals on NVDA and BTC-USD?"*

## Configuration
All knobs in `config.py` / `.env` (see `.env.example`): RSI period, SMA fast/slow,
volume window, lookback, poll interval, data backend, Telegram. A client reskin is
usually just `watchlist.txt` + `rules.yaml`.

## Architecture
```
watchlist.txt ─┐
               ├─ scanner.py ─ data.py(yfinance) ─ indicators.py ─ rules.py(rules.yaml)
rules.yaml ────┘                                                         │
                                                  signals ──> console / Telegram / MCP `scan`
```
Reuses the mcp-factory contract (`Result`, `formatting`, `cache`) so it composes with the rest of the catalog.

## License
MIT.
