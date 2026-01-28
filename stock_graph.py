from stock_stats import get_return, get_sharpe_ratio, get_sortino_ratio

import plotly.graph_objects as go
import yfinance as yf

CLOSE_COL = "Close"

valid_periods = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]


def get_price_data(symbols, period="2y"):
    tickers = yf.Tickers(symbols)
    price_data = tickers.history(period=period)
    # as there is no raise_errors option with multiple symbols, we'll check manually for missing data
    missing_symbols = []
    for symbol in symbols:
        if price_data[((CLOSE_COL, symbol))].isnull().all():
            missing_symbols.append(symbol)
    if len(missing_symbols) > 0:
        raise Exception(f"There is no data for {", ".join(missing_symbols)}. Check that the tickers are valid and that "
                        f"the stocks haven't been delisted.")
    return price_data


def get_stats(close_prices):
    high_price = max(close_prices)
    low_price = min(close_prices)
    return_val = get_return(close_prices)
    sharpe_ratio = get_sharpe_ratio(close_prices)
    sortino_ratio = get_sortino_ratio(close_prices)
    return {"high": high_price, "low": low_price, "return_val": return_val,
            "sharpe_ration": sharpe_ratio, "sortino_ratio": sortino_ratio}

def plot_data(price_data_list, symbols):
    fig = go.Figure()

    for i, (close_prices, symbol) in enumerate(zip(price_data_list, symbols)):
        stats = get_stats(close_prices)
        print(f"\n{symbol} Statistics:")
        print(f"High Price: ${stats['high']:.2f}")
        print(f"Low Price: ${stats['low']:.2f}")
        print(f"Return: {stats['return_val']:.2%}")
        print(f"Sharpe Ratio: {stats['sharpe_ration']:.2f}")
        print(f"Sortino Ratio: {stats['sortino_ratio']:.2f}")

        # Add trace for each stock
        fig.add_trace(go.Scatter(
            x=close_prices.index,
            y=close_prices.values,
            mode='lines',
            name=symbol,
            hovertemplate=f'<b>{symbol}</b><br>' +
                          'Date: %{x}<br>' +
                          'Price: $%{y:.2f}<br>' +
                          '<extra></extra>'
        ))

    fig.update_layout(
        title= {
            "text": f"Stock Price History: {' vs '.join(symbols)}",
            "xanchor": "center",
            'x': 0.5,
            'font': {'size': 25}
        },
        xaxis_title="Date",
        yaxis_title="Close Price ($)",
        hovermode='x unified'
    )

    fig.show()

def run_program():
    print("Enter first stock symbol:")
    symbol1 = input().upper()

    print("Enter second stock symbol (leave blank to plot only one stock):")
    symbol2 = input().upper()

    symbols = [symbol1]
    # if symbols are the same, treat it as if only one symbol was entered
    if symbol2 and symbol1!=symbol2:
        symbols.append(symbol2)

    time_period_prompt = "Enter a time period (leave blank for 2 years):"
    print(time_period_prompt)
    print(f"Valid time periods are {' '.join(valid_periods)}")
    time_period = input() or "2y"
    while time_period not in valid_periods:
        print(time_period_prompt)
        print("Enter a time period:")
        time_period = input() or "2y"

    price_df = get_price_data(symbols, time_period)
    price_data_list = []
    for symbol in symbols:
        # drop nans so calculations will be correct if prices are not available for the full time range.
        close_data = price_df[(CLOSE_COL, symbol)].dropna()
        print(close_data.shape)
        print(close_data.head().to_string())
        price_data_list.append(close_data)

    plot_data(price_data_list, symbols)

if __name__ == '__main__':
    run_program()