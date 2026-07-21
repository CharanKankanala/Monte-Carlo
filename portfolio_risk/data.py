"""Market-data acquisition with deterministic offline fallback."""
from __future__ import annotations

from datetime import date
from pathlib import Path
import pandas as pd

ASSETS = {
    "SPY": "US large-cap equity", "QQQ": "US technology equity",
    "IWM": "US small-cap equity", "EFA": "Developed ex-US equity",
    "IEF": "Intermediate Treasuries", "TLT": "Long Treasuries",
    "GLD": "Gold", "VNQ": "US real estate", "DBC": "Broad commodities",
}
BENCHMARKS = {"SP500": {"SPY": 1.0}, "SIXTY_FORTY": {"SPY": .6, "IEF": .4}}


def download_market_data(cache: str | Path = "data/market_prices.csv",
                         start: str = "2014-01-01", end: str | None = None,
                         refresh: bool = False) -> tuple[pd.DataFrame, str]:
    """Download adjusted ETF prices; use a valid cache when the network is unavailable."""
    cache = Path(cache)
    if cache.exists() and not refresh:
        return pd.read_csv(cache, index_col=0, parse_dates=True), "cached_market_data"
    try:
        import yfinance as yf
        raw = yf.download(list(ASSETS), start=start, end=end or date.today().isoformat(),
                          auto_adjust=True, progress=False, threads=True, timeout=20)
        prices = raw["Close"] if isinstance(raw.columns, pd.MultiIndex) else raw
        prices = prices.reindex(columns=list(ASSETS)).dropna()
        if len(prices) < 750:
            raise ValueError("Downloaded history is too short")
        cache.parent.mkdir(parents=True, exist_ok=True)
        prices.rename_axis("Date").to_csv(cache)
        return prices, "yahoo_adjusted_close"
    except Exception as exc:
        if cache.exists():
            return pd.read_csv(cache, index_col=0, parse_dates=True), "cached_market_data"
        raise RuntimeError("Market download failed and no cached market dataset exists") from exc

