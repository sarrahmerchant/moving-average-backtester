import yfinance as yf
import matplotlib.pyplot as plt
import streamlit as st
import datetime
import pandas as pd

@st.cache_data(show_spinner="Loading data...")
def load_ticker_data(ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date, interval="1d", auto_adjust=False)
    # Flatten MultiIndex columns from yfinance
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    data = data.dropna().copy()
    return data

def buy(capital, price):
    bought = capital // price
    return bought, bought * price 

def sell(shares, price):
    return 0, shares * price



st.title("Moving Average Backtester")

st.sidebar.title("Settings")
ticker = st.sidebar.text_input("Ticker", "AAPL")
initial_capital = st.sidebar.number_input("Initial Capital", value=100000, min_value=1000, max_value=1000000)
start_date = st.sidebar.date_input("Start Date", datetime.date(2020, 1, 1))
end_date = st.sidebar.date_input("End Date", datetime.date(2020, 12, 31))
short_window = st.sidebar.number_input("Short Window", value=20, min_value=1, max_value=100)
long_window = st.sidebar.number_input("Long Window", value=50, min_value=1, max_value=100)
signal_threshold = st.sidebar.number_input("Signal Threshold", value=0.05, min_value=0.0, max_value=1.0)
run_button = st.sidebar.button("Run Backtest")


if run_button:
    shares = 0
    capital = initial_capital
    trade_log = []
    equity_curve = []
    data = load_ticker_data(ticker, start_date, end_date)
    st.write(data.tail())
    price_series = data["Adj Close"]

    fast_ma = price_series.rolling(window=short_window).mean()
    slow_ma = price_series.rolling(window=long_window).mean()
    st.write(fast_ma.tail(10))
    st.write(slow_ma.tail(10))

    signal = (fast_ma > slow_ma).astype(int)  
    signal_change = signal.diff()
    print(signal_change.tail(10))

    buy_signal = signal_change.eq(1)
    sell_signal = signal_change.eq(-1)

    st.write("Buy signals:", int(buy_signal.sum()))
    st.write("Sell signals:", int(sell_signal.sum()))

    for i in range(len(data) - 1):

        today = data.iloc[i]
        date = data.index[i]
        tomorrow = data.iloc[i + 1]
        today_close = today["Adj Close"]
        tomorrow_open = tomorrow["Open"]
        equity = capital + shares * today_close
        equity_curve.append({
        "date": today.name,
        "equity": equity,
        "capital": capital,
        "shares": shares
        })

       
        if buy_signal.iloc[i] == True and shares == 0:
            shares = capital // tomorrow_open
            capital = capital - shares * tomorrow_open
            trade_log.append({"date": today.name, "action": "buy", "shares": shares, "price": tomorrow_open, "capital": capital})
        elif sell_signal.iloc[i] == True and shares > 0:
            capital = capital + shares * tomorrow_open
            shares = 0
            trade_log.append({
            "date": date,
            "action": "SELL",
            "shares": shares,
            "price": tomorrow_open,
            "capital": capital
        })

    equity_df = pd.DataFrame(equity_curve)
    equity_df.set_index("date", inplace=True)


    st.subheader("Equity Log")
    st.write(equity_df.tail(10))

    st.subheader("Equity Curve")
    st.line_chart(equity_df["equity"])

    st.write("Final capital:", capital)
    st.write("Final shares:", shares)
    st.write("Final equity:", equity_df["equity"].iloc[-1])
    st.write("Num trades:", len(trade_log))










    
