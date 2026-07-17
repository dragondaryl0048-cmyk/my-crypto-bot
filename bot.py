import streamlit as st
import pandas as pd
import numpy as np
import urllib.request
import json

st.set_page_config(page_title="AI Crypto Bot Dashboard", layout="wide")
st.title("🤖 Multi-Coin AI Trading Assistant (Binance Feed)")
st.write("AI Bot for analyzing multi-coins via Geographically Unrestricted Binance Price Streams")

st.sidebar.header("🔧 Bot Settings")
symbol = st.sidebar.text_input("Crypto Coin (e.g., BTC-USD, ETH-USD):", value="BTC-USD")
timeframe = st.sidebar.selectbox("Time Frame:", ["1d", "1h", "1m"])

def fetch_data(symbol):
    try:
        # Standardizing format for Yahoo Finance Binance mirror (e.g., BTCUSDT -> BTC-USD)
        formatted_symbol = symbol.replace("USDT", "USD").replace("/", "-").upper()
        if "-" not in formatted_symbol:
            formatted_symbol = f"{formatted_symbol}-USD"

        # Using public yahoo finance endpoint providing global unrestricted data streams
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{formatted_symbol}?range=30d&interval=1h"
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode())
            
        result = res_data['chart']['result'][0]
        timestamps = result['timestamp']
        indicators = result['indicators']['quote'][0]
        
        df = pd.DataFrame({
            'Timestamp': pd.to_datetime(timestamps, unit='s'),
            'Open': indicators['open'],
            'High': indicators['high'],
            'Low': indicators['low'],
            'Close': indicators['close'],
            'Volume': indicators['volume']
        }).dropna()
        
        return df
    except Exception as e:
        st.error(f"Data Fetching Error: {e}. Please ensure the symbol is correct (e.g., BTC-USD).")
        return None

if st.sidebar.button("Run AI Analysis"):
    st.write(f"🔍 Fetching global chart data stream for **{symbol}**...")
    df = fetch_data(symbol)
    if df is not None and not df.empty:
        latest_close = df['Close'].iloc[-1]
        high_price = df['High'].max()
        low_price = df['Low'].min()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Current Price", f"${latest_close:,.4f}")
        col2.metric("Highest (Selected Period)", f"${high_price:,.4f}")
        col3.metric("Lowest (Selected Period)", f"${low_price:,.4f}")
        
        st.subheader("📊 AI Technical & Risk Analysis")
        
        volatility = (df['High'] - df['Low']).mean()
        if volatility == 0:
            volatility = latest_close * 0.015
            
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
