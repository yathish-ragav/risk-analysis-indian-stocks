from data.fetch_data import fetch_close_prices
from risk.risk_metrics import (
    calculate_beta,
    calculate_daily_returns,
    calculate_var,
    calculate_volatility,
)


def _format_percent(value):
    return f"{value:.4%}" if value is not None else "N/A"


def _format_float(value):
    return f"{value:.4f}" if value is not None else "N/A"


def _analyze_stock(ticker, market_returns):
    close_prices = fetch_close_prices(ticker)
    if close_prices is None:
        return None

    daily_returns = calculate_daily_returns(close_prices)
    if daily_returns is None:
        return None

    average_daily_return, daily_volatility, annualized_volatility = calculate_volatility(
        daily_returns
    )
    beta = calculate_beta(daily_returns, market_returns)
    var_5 = calculate_var(daily_returns)

    return {
        "ticker": ticker,
        "data_points": len(close_prices),
        "average_daily_return": average_daily_return,
        "daily_volatility": daily_volatility,
        "annualized_volatility": annualized_volatility,
        "beta": beta,
        "var_5": var_5,
    }


def _print_results_table(results):
    if not results:
        print("No stock results to display.")
        return

    row_format = (
        "{:<4} | {:<12} | {:>11} | {:>10} | {:>10} | {:>10} | {:>8} | {:>10}"
    )
    headers = (
        "Rank",
        "Ticker",
        "Data Points",
        "Avg Return",
        "Daily Vol",
        "Annual Vol",
        "Beta",
        "VaR",
    )

    header_line = row_format.format(*headers)
    print(header_line)
    print("-" * len(header_line))
    for index, result in enumerate(results, start=1):
        print(
            row_format.format(
                index,
                result["ticker"],
                result["data_points"],
                _format_percent(result["average_daily_return"]),
                _format_percent(result["daily_volatility"]),
                _format_percent(result["annualized_volatility"]),
                _format_float(result["beta"]),
                _format_percent(result["var_5"]),
            )
        )


def main():
    tickers = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS"]
    market_ticker = "^NSEI"
    market_close_prices = fetch_close_prices(market_ticker)
    if market_close_prices is None:
        print(f"No valid close-price data fetched for market benchmark {market_ticker}.")
        return

    market_returns = calculate_daily_returns(market_close_prices)
    if market_returns is None:
        print(f"Not enough market data to calculate returns for {market_ticker}.")
        return

    results = []
    for ticker in tickers:
        stock_result = _analyze_stock(ticker, market_returns)
        if stock_result is None:
            print(f"Skipping {ticker}: insufficient data.")
            continue
        results.append(stock_result)

    if not results:
        print("No stocks had enough data for analysis.")
        return

    results.sort(key=lambda item: item["annualized_volatility"])

    print(f"Market benchmark: {market_ticker}")
    print("Ranking: lowest to highest risk by annualized volatility")
    _print_results_table(results)


if __name__ == "__main__":
    main()
