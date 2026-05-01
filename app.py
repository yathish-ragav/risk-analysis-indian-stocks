import pandas as pd
import streamlit as st

from data.fetch_data import fetch_close_prices
from risk.risk_metrics import (
    calculate_beta,
    calculate_daily_returns,
    calculate_var,
    calculate_volatility,
)


MARKET_TICKER = "^NSEI"
HIGH_VOLATILITY_THRESHOLD = 0.30
VERY_NEGATIVE_VAR_THRESHOLD = -0.03


def parse_tickers(raw_text: str):
    return [ticker.strip().upper() for ticker in raw_text.split(",") if ticker.strip()]


def analyze_stock(ticker, market_returns):
    close_prices = fetch_close_prices(ticker)
    if close_prices is None:
        return None, None

    daily_returns = calculate_daily_returns(close_prices)
    if daily_returns is None:
        return None, None

    average_return, daily_volatility, annualized_volatility = calculate_volatility(
        daily_returns
    )
    beta = calculate_beta(daily_returns, market_returns)
    var_5 = calculate_var(daily_returns)

    metrics = {
        "Ticker": ticker,
        "Data Points": len(close_prices),
        "Average Return": average_return,
        "Daily Volatility": daily_volatility,
        "Annual Volatility": annualized_volatility,
        "Beta": beta,
        "VaR (5%)": var_5,
    }
    return metrics, close_prices


def build_risk_insights(row):
    insights = []

    if row["Beta"] is not None and row["Beta"] > 1:
        insights.append("High market sensitivity")

    if (
        row["Annual Volatility"] is not None
        and row["Annual Volatility"] > HIGH_VOLATILITY_THRESHOLD
    ):
        insights.append("High risk")

    if row["VaR (5%)"] is not None and row["VaR (5%)"] < VERY_NEGATIVE_VAR_THRESHOLD:
        insights.append("High downside risk")

    if not insights:
        insights.append("Risk appears moderate based on current thresholds")

    return insights


def main():
    st.set_page_config(page_title="Indian Equity Risk Analyser (Beta, Var, Volatility)", layout="wide")
    st.title("Indian Equity Risk Analyser (Beta, Var, Volatility)")

    raw_symbols = st.text_input(
        "Enter stock symbols (comma separated)",
        value="RELIANCE.NS, TCS.NS, INFY.NS, HDFCBANK.NS",
    )
    run_analysis = st.button("Analyze")

    if not run_analysis:
        return

    tickers = parse_tickers(raw_symbols)
    if not tickers:
        st.warning("Please enter at least one valid stock symbol.")
        return

    market_prices = fetch_close_prices(MARKET_TICKER)
    if market_prices is None:
        st.error(f"Could not fetch market data for {MARKET_TICKER}.")
        return

    market_returns = calculate_daily_returns(market_prices)
    if market_returns is None:
        st.error(f"Could not calculate market returns for {MARKET_TICKER}.")
        return

    metrics_rows = []
    price_series = {}

    for ticker in tickers:
        metrics, close_prices = analyze_stock(ticker, market_returns)
        if metrics is None:
            st.warning(f"Skipping {ticker}: insufficient data.")
            continue
        metrics_rows.append(metrics)
        price_series[ticker] = close_prices

    if not metrics_rows:
        st.info("No stocks had enough data for analysis.")
        return

    results_df = pd.DataFrame(metrics_rows)
    results_df = results_df.sort_values("Annual Volatility")
    st.subheader("Risk Metrics")
    st.dataframe(
        results_df.style.format(
            {
                "Average Return": "{:.4%}",
                "Daily Volatility": "{:.4%}",
                "Annual Volatility": "{:.4%}",
                "Beta": "{:.4f}",
                "VaR (5%)": "{:.4%}",
            }
        ),
        use_container_width=True,
    )

    lowest_risk = results_df.iloc[0]
    highest_risk = results_df.iloc[-1]
    st.markdown(
        f"<span style='color:green;'><b>Lowest risk stock:</b> {lowest_risk['Ticker']} "
        f"({lowest_risk['Annual Volatility']:.4%} annual volatility)</span>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<span style='color:red;'><b>Highest risk stock:</b> {highest_risk['Ticker']} "
        f"({highest_risk['Annual Volatility']:.4%} annual volatility)</span>",
        unsafe_allow_html=True,
    )

    st.subheader("Risk Insights")
    for _, row in results_df.iterrows():
        insights = build_risk_insights(row)
        st.markdown(f"**{row['Ticker']}**: " + " | ".join(insights))

    prices_df = pd.DataFrame(price_series).sort_index()
    st.subheader("Stock Price Trend")
    st.line_chart(prices_df, use_container_width=True)


if __name__ == "__main__":
    main()
