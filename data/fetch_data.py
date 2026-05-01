from pathlib import Path

import yfinance as yf


def fetch_close_prices(ticker: str, period: str = "6mo", interval: str = "1d"):
    """Download close prices for a ticker and return a 1D series."""
    # Keep yfinance cache inside the project so writes always succeed.
    cache_dir = Path(".cache") / "yfinance"
    cache_dir.mkdir(parents=True, exist_ok=True)
    if hasattr(yf, "set_tz_cache_location"):
        yf.set_tz_cache_location(str(cache_dir))

    try:
        data = yf.download(
            ticker,
            period=period,
            interval=interval,
            auto_adjust=True,
            progress=False,
        )
    except Exception:
        return None

    if data.empty or "Close" not in data:
        return None

    close_prices = data["Close"]
    if getattr(close_prices, "ndim", 1) > 1:
        close_prices = close_prices.iloc[:, 0]

    return close_prices
