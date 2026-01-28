from stock_stats import get_return, get_sharpe_ratio, get_sortino_ratio

import yfinance as yf

CLOSE_COL = "Close"

valid_periods = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]


def get_price_data(symbols, period="2y"):
    if isinstance(symbols, str):
        symbols = [s for s in symbols.replace(",", " ").split() if s]
    symbols = [s.upper() for s in symbols]
    ticker_str = " ".join(symbols)
    tickers = yf.Tickers(ticker_str)
    price_data = tickers.history(period=period)

    if len(symbols) == 1:
        symbol = symbols[0]
        close_series = _extract_close_series(price_data, symbol)
        if close_series.isnull().all():
            raise Exception(
                f"There is no data for {symbol}. Check that the ticker is valid and that the stock hasn't been delisted."
            )
        return price_data

    missing_symbols = []
    for symbol in symbols:
        close_series = price_data[(CLOSE_COL, symbol)]
        if close_series.isnull().all():
            missing_symbols.append(symbol)
    if missing_symbols:
        missing_str = ", ".join(missing_symbols)
        raise Exception(
            f"There is no data for {missing_str}. Check that the tickers are valid and that the stocks haven't been delisted."
        )
    return price_data


def get_stats(close_prices):
    stat_prices = close_prices.reset_index(drop=True)
    high_price = stat_prices.max()
    low_price = stat_prices.min()
    return_val = get_return(stat_prices)
    sharpe_ratio = get_sharpe_ratio(stat_prices)
    sortino_ratio = get_sortino_ratio(stat_prices)
    return {
        "high": high_price,
        "low": low_price,
        "return_val": return_val,
        "sharpe_ration": sharpe_ratio,
        "sortino_ratio": sortino_ratio,
    }

def _extract_close_series(price_df, symbol):
    if hasattr(price_df.columns, "levels"):
        return price_df[(CLOSE_COL, symbol)]
    return price_df[CLOSE_COL]


def run_program():
    try:
        import tkinter as tk
        from tkinter import messagebox
        from tkinter.scrolledtext import ScrolledText

        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        from matplotlib.figure import Figure
    except Exception as e:
        raise SystemExit(f"Tkinter GUI dependencies are not available: {e}")

    class StockApp:
        def __init__(self, root):
            self.root = root
            self.root.title("Stock Analysis")

            self.symbol_vars = [tk.StringVar(), tk.StringVar(), tk.StringVar()]
            self.period_var = tk.StringVar(value="2y")

            root_frame = tk.Frame(root)
            root_frame.pack(fill="both", expand=True, padx=12, pady=12)

            controls = tk.Frame(root_frame)
            controls.pack(fill="x")

            for i in range(3):
                tk.Label(controls, text=f"Ticker {i + 1}:").grid(row=0, column=i * 2, sticky="w", padx=(0, 6))
                tk.Entry(controls, textvariable=self.symbol_vars[i], width=10).grid(
                    row=0, column=i * 2 + 1, padx=(0, 12)
                )

            tk.Label(controls, text="Period:").grid(row=0, column=6, sticky="w", padx=(0, 6))
            tk.OptionMenu(controls, self.period_var, *valid_periods).grid(row=0, column=7, padx=(0, 12))

            plot_btn = tk.Button(controls, text="Plot", command=self.on_plot)
            plot_btn.grid(row=0, column=8, sticky="e")

            controls.grid_columnconfigure(9, weight=1)

            lower = tk.PanedWindow(root_frame, orient="horizontal", sashrelief="raised")
            lower.pack(fill="both", expand=True, pady=(12, 0))

            left = tk.Frame(lower)
            right = tk.Frame(lower)
            lower.add(left, stretch="always")
            lower.add(right, stretch="always")

            self.stats_text = ScrolledText(left, width=40, height=24)
            self.stats_text.pack(fill="both", expand=True)

            self.figure = Figure(figsize=(7, 5), dpi=100)
            self.ax = self.figure.add_subplot(111)
            self.canvas = FigureCanvasTkAgg(self.figure, master=right)
            self.canvas.get_tk_widget().pack(fill="both", expand=True)

            root.bind("<Return>", lambda _event: self.on_plot())

        def on_plot(self):
            symbols = []
            seen = set()
            for var in self.symbol_vars:
                raw = var.get().strip().upper()
                if not raw:
                    continue
                if raw in seen:
                    continue
                seen.add(raw)
                symbols.append(raw)

            if not symbols:
                messagebox.showerror("Input Error", "Please enter at least one ticker symbol.")
                return

            if len(symbols) > 3:
                symbols = symbols[:3]

            period = self.period_var.get().strip()
            if period not in valid_periods:
                period = "2y"
                self.period_var.set(period)

            try:
                price_df = get_price_data(symbols, period)
                close_series_list = []
                for symbol in symbols:
                    close_series = _extract_close_series(price_df, symbol).dropna()
                    if close_series.empty:
                        raise Exception(f"No close price data returned for {symbol}.")
                    close_series_list.append(close_series)
            except Exception as e:
                self.stats_text.delete("1.0", tk.END)
                self.ax.clear()
                self.canvas.draw_idle()
                messagebox.showerror("Data Error", str(e))
                return

            self._render_stats(close_series_list, symbols)
            self._render_plot(close_series_list, symbols, period)

        def _render_stats(self, close_series_list, symbols):
            self.stats_text.delete("1.0", tk.END)
            blocks = []
            for close_prices, symbol in zip(close_series_list, symbols):
                stats = get_stats(close_prices)
                block = "\n".join(
                    [
                        f"{symbol} Statistics:",
                        f"High Price: ${stats['high']:.2f}",
                        f"Low Price: ${stats['low']:.2f}",
                        f"Return: {stats['return_val']:.2%}",
                        f"Sharpe Ratio: {stats['sharpe_ration']:.2f}",
                        f"Sortino Ratio: {stats['sortino_ratio']:.2f}",
                    ]
                )
                blocks.append(block)
            self.stats_text.insert(tk.END, "\n\n".join(blocks))

        def _render_plot(self, close_series_list, symbols, period):
            self.ax.clear()
            for close_prices, symbol in zip(close_series_list, symbols):
                self.ax.plot(close_prices.index, close_prices.values, label=symbol)

            self.ax.set_title(f"Stock Price History ({period}): {' vs '.join(symbols)}")
            self.ax.set_xlabel("Date")
            self.ax.set_ylabel("Close Price ($)")
            self.ax.legend()
            self.figure.autofmt_xdate()
            self.canvas.draw_idle()

    root = tk.Tk()
    StockApp(root)
    root.mainloop()

if __name__ == '__main__':
    run_program()
