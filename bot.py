import streamlit as st
import pandas as pd
import numpy as np
import urllib.request
import json

st.set_page_config(page_title="AI Crypto Bot Dashboard", layout="wide")
st.title("🎯 Precision Crypto AI Trading Assistant")
st.write("This bot provides exact Entry, Target, and Stop Loss prices for your trades.")

st.sidebar.header("🔧 Bot Settings")
symbol = st.sidebar.text_input("Crypto Coin (e.g., BTC-USD, ETH-USD, TRX-USD):", value="BTC-USD")
timeframe = st.sidebar.selectbox("Time Frame:", ["1h", "1d", "15m"])

def fetch_data(symbol, tf):
    try:
        formatted_symbol = symbol.replace("USDT", "USD").replace("/", "-").upper()
        if "-" not in formatted_symbol:
            formatted_symbol = f"{formatted_symbol}-USD"

        data_range = "30d" if tf in ["1h", "15m"] else "180d"
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{formatted_symbol}?range={data_range}&interval={tf}"
        
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
        st.sidebar.error(f"Data Fetching Error: {e}. Use format like BTC-USD.")
        return None

def calculate_rsi(df, periods=14):
    close_delta = df['Close'].diff()
    up = close_delta.clip(lower=0)
    down = -1 * close_delta.clip(upper=0)
    ma_up = up.ewm(com=periods - 1, adjust=True).mean()
    ma_down = down.ewm(com=periods - 1, adjust=True).mean()
    rsi = ma_up / ma_down
    rsi = 100 - (100 / (1 + rsi))
    return rsi

if st.sidebar.button("Run AI Analysis"):
    st.write(f"🔍 Fetching global chart data stream for **{symbol}**...")
    df = fetch_data(symbol, timeframe)
    
    if df is not None and not df.empty:
        # Technical indicators
        df['EMA_10'] = df['Close'].ewm(span=10, adjust=False).mean()
        df['EMA_30'] = df['Close'].ewm(span=30, adjust=False).mean()
        df['RSI'] = calculate_rsi(df)
        
        latest_close = df['Close'].iloc[-1]
        latest_rsi = df['RSI'].iloc[-1]
        latest_ema10 = df['EMA_10'].iloc[-1]
        latest_ema30 = df['EMA_30'].iloc[-1]
        
        # Volatility Calculation using High and Low points
        volatility = (df['High'] - df['Low']).rolling(window=14).mean().iloc[-1]
        if pd.isna(volatility) or volatility == 0:
            volatility = latest_close * 0.02

        # Fixed Signal Output & Mathematical Trade Execution Points
        if latest_ema10 > latest_ema30:
            signal = "🟢 BUY SIGNAL (Bullish Trend)"
            entry_price = latest_close  # Current price is the immediate entry point
            target = entry_price + (volatility * 1.5)
            stop_loss = entry_price - (volatility * 1.2)
            action_plan = f"Enter trade at ${entry_price:,.4f}. Set your exit points accordingly."
        else:
            signal = "🔴 SELL / SHORT SIGNAL (Bearish Trend)"
            entry_price = latest_close
            target = entry_price - (volatility * 1.5)
            stop_loss = entry_price + (volatility * 1.2)
            action_plan = f"Market trend is down. Consider shorting at ${entry_price:,.4f} or wait on sidelines."

        # Visual Dashboard Custom Layout
        st.subheader("📊 AI Trade Execution Blueprint")
        
        # Row 1: Key Metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Current Market Price", f"${latest_close:,.4f}")
        m2.metric("RSI Momentum Indicator", f"{latest_rsi:.2f}")
        m3.metric("Trend Classification", "BULLISH 📈" if latest_ema10 > latest_ema30 else "BEARISH 📉")
        
        st.info(f"**AI Recommendation:** {signal}")
        
        # Row 2: Exact Price Zones for the User
        col_entry, col_target, col_sl = st.columns(3)
        
        with col_entry:
            st.info(f"🔑 **EXACT ENTRY PRICE:**\n### ${entry_price:,.4f}")
        with col_target:
            st.success(f"🎯 **TAKE PROFIT TARGET:**\n### ${target:,.4f}")
        with col_sl:
            st.error(f"🛑 **STRICT STOP LOSS:**\n### ${stop_loss:,.4f}")
            
        st.warning(f"⏱️ **Execution Strategy:** {action_plan}")
            
        st.subheader("📊 Visual Price Chart")
        chart_df = df.set_index('Timestamp')[['Close', 'EMA_10', 'EMA_30']]
        st.line_chart(chart_df)
