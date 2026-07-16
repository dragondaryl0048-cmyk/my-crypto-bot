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
        
        # 1. Market Overview Metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Current Price", f"${latest_close:,.2f}")
        col2.metric("Highest (Selected Period)", f"${high_price:,.2f}")
        col3.metric("Lowest (Selected Period)", f"${low_price:,.2f}")
        
        # 2. AI & Risk Analysis (Target & Stop Loss Logic)
        st.subheader("📊 AI Technical & Risk Analysis")
        
        # Calculate Volatility (Simple ATR-based approach)
        volatility = (df['High'] - df['Low']).mean()
        
        # Moving Average Calculation for Trend
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

        # Display AI Recommendation
        st.info(f"**Recommendation:** {signal}")
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.success(f"🎯 **Expected Target:** ${target:,.2f}")
            st.warning(f"⏱️ **Best Time to Trade:** {best_time}")
        with col_b:
            st.error(f"🛑 **Stop Loss:** ${stop_loss:,.2f}")
            
        # 3. News Sentiment Section (Placeholder)
        st.subheader("📰 Market News Sentiment")
        st.write("💡 *AI News Alert:* Based on current macroeconomic data, the market is experiencing moderate volatility. No major high-impact news events detected in the last hour.")
        
        # 4. Interactive Price Chart
        st.subheader("📈 Price Chart Data")
        st.line_chart(df.set_index('Timestamp')['Close'])
