import numpy as np


def calculate_daily_returns(close_prices):
    """Calculate daily percentage returns from close prices."""
    if close_prices is None:
        return None

    daily_returns = close_prices.pct_change().dropna()
    if daily_returns.empty:
        return None

    return daily_returns


def calculate_volatility(daily_returns):
    """Return average daily return, daily volatility, annualized volatility."""
    if daily_returns is None:
        return None, None, None

    average_daily_return = float(daily_returns.mean())
    daily_volatility = float(daily_returns.std())
    annualized_volatility = float(daily_volatility * (252 ** 0.5))

    return average_daily_return, daily_volatility, annualized_volatility


def calculate_beta(stock_returns, market_returns):
    """Calculate beta of a stock relative to market returns."""
    if stock_returns is None or market_returns is None:
        return None

    aligned_stock, aligned_market = stock_returns.align(market_returns, join="inner")
    aligned_data = aligned_stock.to_frame("stock").join(
        aligned_market.to_frame("market")
    ).dropna()

    if aligned_data.empty:
        return None

    covariance = aligned_data["stock"].cov(aligned_data["market"])
    variance = aligned_data["market"].var()

    if variance == 0:
        return None

    return float(covariance / variance)


def calculate_var(returns):
    """Calculate 5th percentile Value at Risk (VaR)."""
    if returns is None:
        return None

    clean_returns = returns.dropna()
    if clean_returns.empty:
        return None

    return float(np.percentile(clean_returns, 5))
