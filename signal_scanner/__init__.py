"""signal-scanner — rule-based stock/crypto screener with alerts.

Define a watchlist and a ruleset (YAML) of indicator conditions; the scanner pulls
market data, computes indicators (price, %change, RSI, SMA cross, volume, 52w range),
fires the rules that match, and delivers signals to the console, Telegram (optional),
or any MCP host.

Keyless by default: market data via yfinance (no API key). Telegram delivery and
Finnhub are optional and degrade gracefully when unconfigured.
"""
__version__ = "0.1.0"
