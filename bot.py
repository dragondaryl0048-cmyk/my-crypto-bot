import streamlit as st
import ccxt
import pandas as pd
import numpy as np

# Page Configuration
st.set_page_config(page_title="AI Crypto Bot Dashboard", layout="wide")
st.title("🤖 Multi-Coin AI Trading Assistant")
st.write("AI Bot for analyzing multi-coins and multi-timeframes")

# Sidebar - Configuration Settings
st.sidebar.header("🔧 Bot Settings")
symbol = st.sidebar.text_input("Crypto Coin (e.g., BTC/USDT, ETH/USDT):", value="BTC/USDT")
timeframe = st.sidebar.selectbox("Time Frame:", ["1m", "5m", "15m", "1h", "4h", "1d"])
limit = st.sidebar.slider("Historical Data Bars:", 50, 500, 200)

# Function to fetch data from Binance
def fetch_data(symbol, timeframe, limit):
    try:
        exchange = ccxt.binance()
        bars = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        df = pd.DataFrame(bars, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

# Trigger Analysis on Button Click
if st.sidebar.button("Run AI Analysis"):
    st.write(f"🔍 Analyzing **{symbol}** on **{timeframe}** chart...")
    
    df = fetch_data(symbol, timeframe, limit)
    
    if df is not None:
        # Latest Price Calculations
        latest_close = df['Close'].iloc[-1]
        high_price = df['High'].max()
        low_price = df['Low'].min()
        
        # 1. Market Overview Metri
