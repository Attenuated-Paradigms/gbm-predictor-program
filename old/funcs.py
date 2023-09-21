import pandas as pd
import numpy as np
import scipy as sc
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.ticker as tkr
from datetime import datetime

### Stock Simulation Processes with Geometric Brownian Motion
def stock_sim_process(mu, steps, T, sims, initial_price, sigma):
    #Instantiate an array with columns equal to the number of steps and rows equal to the number of simulations.
    stock_sim_array = np.zeros((sims, steps))
    dt = T/steps
    for sim in range(sims):
        for step in range(steps):
            if step == 0:
                current_price = initial_price
                stock_sim_array[sim, step] = current_price
            else:
                previous_price = stock_sim_array[sim, step - 1]
                current_price = previous_price*np.exp((mu-sigma**2/2)*dt + sigma*np.random.normal(0, np.sqrt(dt)))
                stock_sim_array[sim, step] = current_price
    return stock_sim_array

def plot_stock_sim_array(stock_sim_array, mu, steps, T, sigma):
    time_space = np.linspace(0, T, steps)
    initial_price = stock_sim_array[0, 0]
    for row in stock_sim_array:
        plt.plot(time_space, row)
    plt.xlabel("Trading Days $(t)$")
    plt.ylabel("Stock Price $(S_t)$")
    plt.title(
        "GBM Realizations\n $dS_t = \mu S_t dt + \sigma S_t dW_t$\n $S_0 = {0}, \mu = {1}, \sigma = {2}$".format(initial_price, mu, sigma)
    )
    plt.show()

### General stock data fetching and plotting

def get_real_prices_bytickers(tickers, date_range):
    stock_data_dict = {}
    for ticker in tickers:
        company = yf.Ticker(ticker)
        price_data = company.history(interval='30m', start=date_range[0], end=date_range[1])["Close"]
        stock_data_dict.update({ticker:price_data})
    return stock_data_dict

def plot_real_prices_bytickers(input_stock_data_dict):
    for ticker in input_stock_data_dict:
        ax = input_stock_data_dict[ticker].plot()
        ticklabels = input_stock_data_dict[ticker].index.strftime('%Y-%m-%d')
        ax.set_xticks(ax.get_xticks())
        ax.xaxis.set_major_formatter(tkr.FixedFormatter(ticklabels))
        ax.yaxis.set_major_formatter(tkr.FormatStrFormatter('%.2f'))
    plt.xlabel("Date")
    plt.ylabel("Stock Price $(S_t)$")
    plt.show()

### Processes related to obtaining stock data snippets for earnings

def get_past_earnings_periods(tickers, num_dates=10):
    past_earnings_dict = {}
    for ticker in tickers:
        ## Get past earnings dates
        company = yf.Ticker(ticker)
        earnings_dates = pd.to_datetime(company.get_earnings_dates(limit=num_dates).index)
        current_date = pd.Timestamp(datetime.now(), tz = 'America/New_York')
        
        #Some of these earnings dates are future dates, so we need to get the number and recalculate
        num_future_dates = len(earnings_dates <= current_date) - np.count_nonzero(earnings_dates <= current_date)

        #Re-doing the fetch to get the correct number of past dates
        corr_earnings_dates = pd.to_datetime(company.get_earnings_dates(limit=num_dates+num_future_dates).index)
        past_earnings = corr_earnings_dates[corr_earnings_dates <= current_date] #dtype='datetime64[ns, America/New_York]', name='Earnings Date'
        past_earnings_dict.update({ticker:past_earnings})
    return past_earnings_dict

def get_real_prices(ticker, date_range):
    granularity_attempts = ['30m', '1h', '1d']
    company = yf.Ticker(ticker)
    for granularity in granularity_attempts:
        price_data = company.history(interval=granularity, start=date_range[0], end=date_range[1])["Close"]
        if len(price_data) == 0:
            pass
        else:
            break
    return price_data, granularity

def plot_real_prices(input_stock_data_dict, granularity):
    fig, ax = plt.subplots()
    ax.plot(range(len(input_stock_data_dict.index)), input_stock_data_dict.values.tolist())
    ticklabels = input_stock_data_dict.index.strftime('%Y-%m-%d')
        
    #ax.set_xticks(ax.get_xticks())
    #ax.xaxis.set_major_formatter(tkr.FixedFormatter(ticklabels))
    #ax.yaxis.set_major_formatter(tkr.FormatStrFormatter('%.2f'))

    plt.title("Stock price data from {} to {} ({} incr.)".format(ticklabels[0], ticklabels[len(ticklabels)-1], granularity))
    plt.xlabel("Trading days from {}".format(ticklabels[0]))
    plt.ylabel("Stock Price $(S_t)$")
    plt.show()

def earnings_dates2intervals(earnings_periods):
    earnings_interval_dict = {}
    for ticker in earnings_periods:
        start_end_array = []
        for index, dates in enumerate(earnings_periods[ticker]):
            if index != len(earnings_periods[ticker]) - 1: #Gotta get the proper ending limit (degrees of freedom), since arrays start at 0
                start_end_array.append([earnings_periods[ticker][index+1], earnings_periods[ticker][index]])
        earnings_interval_dict.update({ticker:start_end_array})
    return earnings_interval_dict

### Analysis of Return Ratio Normality and Estimation of Drift/Volatility

# cool_stocks = ['MSFT'] #, 'GOOG']
# cool_earnings_dates = get_past_earnings_periods(cool_stocks, num_dates=8)
# cool_earnings_intervals = earnings_dates2intervals(cool_earnings_dates)


for ticker in cool_earnings_intervals:
    for interval in cool_earnings_intervals[ticker]:
        interval_price_data, data_increments = get_real_prices(ticker, interval)
        plot_real_prices(interval_price_data, data_increments)

class StockData:
    def __init__(self, ticker_name, start_date, end_date):
        import plotly.graph_objects
        import yfinance
        OHLC = ["Open", "High", "Low", "Close"]
        self.history = yfinance.Ticker(ticker_name).history(
                start = start_date, 
                end = end_date,
                interval = '1d'
            )
        self.candlestick = plotly.graph_objects.Figure(
            data=[
                plotly.graph_objects.Candlestick(
                    x=self.history.index,
                    open=self.history['Open'],
                    high=self.history['High'],
                    low=self.history['Low'],
                    close=self.history['Close']
                )
            ]
        )
        self.candlestick.update_xaxes(
            rangebreaks=[ 
                { 'values': ['2023-01-02', '2023-01-16', '2023-02-20', '2023-04-07', '2023-05-29', '2023-06-19', '2023-07-04', '2023-09-04'] },
                { 'pattern': 'day of week', 'bounds': ['sat', 'mon']},
                #{ 'pattern': 'hour', 'bounds':[16,9.5]}
            ]
        )
        self.line = plotly.graph_objects.Figure(
            data=[
                plotly.graph_objects.Scatter(
                    x=self.history.index,
                    y=self.history['High'],
                    name = "High"
                ),
                plotly.graph_objects.Scatter(
                    x=self.history.index,
                    y=self.history['Low'],
                    name = "Low"
                    
                ),
                plotly.graph_objects.Scatter(
                    x=self.history.index,
                    y=self.history['Close'],
                    name = "Close"
                    
                )                
            ]
        )
        self.line.update_xaxes(
            rangebreaks=[ 
                { 'pattern': 'day of week', 'bounds': ['sat', 'mon']},
                #{ 'pattern': 'hour', 'bounds':[16,9.5]}
            ]
        )

#cool_stock_data = get_real_stock_prices(cool_stocks, ['2012-01-01', '2017-01-01'])
#plot_real_stock_price(cool_stock_data)

# drift_coef = 0.0 # drift coefficent
# total_time = 252 # time in days
# num_timesteps = total_time*13 # number of steps; 6.5 hours in a trading day; 30 minute resolution means 13 half-hours in a trading day
# num_sims = 30
# price = 100  # initial stock price
# volatility = 0.001 # volatility

# sim_1 = stock_sim_process(mu=drift_coef, steps=num_timesteps, T=total_time, sims=num_sims, initial_price=price, sigma=volatility)
# print(sim_1)
# plot_stock_sim_array(stock_sim_array=sim_1, mu=drift_coef, steps=num_timesteps, T=total_time, sigma=volatility)
