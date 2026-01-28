import math

def get_return(prices):
    """
    Computers the return of a stock (last price compared to first price)
    :param prices: Pandas Series containing daily prices
    :return: Percent return (float)
    """
    return (prices[-1]-prices[0])/prices[0]

def get_sharpe_ratio(prices, rf=0):
    """
    Computes the Sharpe Ratio (performance after adjusting for risk)
    :param prices: Pandas Series containing daily prices.
    :param rf: Risk-free return rate
    :return: Sharpe Ratio
    """
    number_of_trading_days = 252
    daily_returns = prices.pct_change()
    mean_returns = daily_returns.mean() * number_of_trading_days
    volatility = daily_returns.std()
    annualized_volatility = volatility * math.sqrt(number_of_trading_days)
    return (mean_returns - rf)/annualized_volatility

def get_sortino_ratio(prices, rf=0):
    """
    Computes the Sortino Ratio (performance after adjusting for downside risk)
    :param prices: Pandas Series containing daily prices.
    :param rf: Risk-free return rate
    :return: Sortino Ratio
    """
    number_of_trading_days = 252
    daily_returns = prices.pct_change()
    mean_returns = daily_returns.mean() * number_of_trading_days
    negative_volatility = daily_returns[daily_returns<0].std()
    annualized_volatility = negative_volatility * math.sqrt(number_of_trading_days)
    return (mean_returns - rf)/annualized_volatility


