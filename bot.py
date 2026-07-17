import streamlit as st
import pandas as pd
import numpy as np
import urllib.request
import json

st.set_page_config(page_title="AI Crypto Bot Dashboard", layout="wide")
st.title("🤖 Multi-Coin AI Trading Assistant (Binance Live)")
st.write("AI Bot for analyzing multi-coins and multi-timeframes via Binance Data")

st.sidebar.header("🔧 Bot Settings")
symbol = st.sidebar.text_input("Crypto Coin (e.g., BTCUSDT, ETHUSDT):", value="BTCUSDT")
timeframe = st.sidebar.selectbox("Time Frame:", ["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"])
limit = st.sidebar.slider("Historical Data Bars:", 50, 500, 200)

def fetch_data(symbol, timeframe, limit):
    try:
        # Standardizing symbol name for Binance API (e.g., BTC/USDT to BTCUSDT)
        formatted_symbol = symbol.replace("/", "").upper()
        
        # Using Binance Public API directly to avoid CCXT region blocks
        url = f"https://api.binance.com/api/v3/klines?symbol={formatted_symbol}&interval={timeframe}&limit={limit}"
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            bars = json.loads(response.read().decode())
            
        # Extracting data: Timestamp, Open, High, Low, Close, Volume
        data = []
        for b in bars:
            data.append([
                b[0],           # Open time
                float(b[1]),    # Open
                float(b[2]),    # High
                float(b[3]),    # Low
                float(b[4]),    # Close
                float(b[5])     # Volume
            ])
            
        df = pd.DataFrame(data, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
        return df
    except Exception as e:
        st.error(f"Error fetching data from Binance API: {e}")
        return None

if st.sidebar.button("Run AI Analysis"):
    st.write(f"🔍 Analyzing **{symbol}** on **{timeframe}** chart via Binance...")
    df = fetch_data(symbol, timeframe, limit)
    if df is not None:
        latest_close = df['Close'].iloc[-1]
        high_price = df['High'].max()
        low_price = df['Low'].min()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Current Price", f"${latest_close:,.4f}")
        col2.metric("Highest (Selected Period)", f"${high_price:,.4f}")
        col3.metric("Lowest (Selected Period)", f"${low_price:,.4f}")
        
        st.subheader("📊 AI Technical & Risk Analysis")
        
        # Accurate Volatility Calculation using High-Low difference
        volatility = (df['High'] - df['Low']).mean()
        if volatility == 0:
            volatility = latest_close * 0.02 # Fallback if volatility calculation gets stuck
            
        short_ma = df['Close'].rolling(window=10).mean().iloc[-1]
        
        if latest_close > short_ma:
            signal = "🟢 BUY SIGNAL (Trend is Bullish)"
            target = latest_close + (volatility * 1.5)
            stop_loss = latest_close - (volatility * 1.2)
            best_time = "Enter immediately via Market Order or on a minor price dip."
        else:
            signal = "🔴 SELL / WAIT SIGNAL (Trend is Bearish)"
            target = latest_close - (volatility * 1.5)
            stop_loss = latest_close + (volatility * 1.2)
            best_time = "Do not enter now. Wait until the market stabilizes."

        st.info(f"**Recommendation:** {signal}")
        col_a, col_b = st.columns(2)
        with col_a:
            st.success(f"🎯 **Expected Target:** ${target:,.4f}")
            st.warning(f"⏱️ **Best Time to Trade:** {best_time}")
        with col_b:
            st.error(f"🛑 **Stop Loss:** ${stop_loss:,.4f}")
            
        st.subheader("📊 Price Chart Data")
        st.line_chart(df.set_index('Timestamp')['Close'])
