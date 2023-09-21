class StockData:
    def __init__(self, ticker_name, start_date, end_date, interval_time):
        import plotly.graph_objects
        import yfinance
        OHLC = ["Open", "High", "Low", "Close"]
        if interval_time == "1h":
            candlestick_rangebreaks = [ 
                { 'values': ['2023-01-02', '2023-01-16', '2023-02-20', '2023-04-07', '2023-05-29', '2023-06-19', '2023-07-04', '2023-09-04']},
                { 'pattern': 'day of week', 'bounds': ['sat', 'mon']},
                { 'pattern': 'hour', 'bounds':[16,9.5]}
            ]
            line_rangebreaks = [ 
                { 'pattern': 'day of week', 'bounds': ['sat', 'mon']},
                { 'pattern': 'hour', 'bounds':[16,9.5]}
            ]
        elif interval_time == "1d":
            candlestick_rangebreaks = [ 
                { 'values': ['2023-01-02', '2023-01-16', '2023-02-20', '2023-04-07', '2023-05-29', '2023-06-19', '2023-07-04', '2023-09-04'] },
                { 'pattern': 'day of week', 'bounds': ['sat', 'mon']},
            ]
            line_rangebreaks = [ 
                { 'pattern': 'day of week', 'bounds': ['sat', 'mon']}
            ]
        
        self.history = yfinance.Ticker(ticker_name).history(
                start = start_date, 
                end = end_date,
                interval = interval_time
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
            rangebreaks=candlestick_rangebreaks
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
            rangebreaks=line_rangebreaks
        )