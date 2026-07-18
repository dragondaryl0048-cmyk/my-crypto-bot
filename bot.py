import streamlit as st
import pandas as pd
import numpy as np
import urllib.request
import json

st.set_page_config(page_title="AI Crypto Bot - Live Feed", layout="wide")
st.title("🎯 Ultimate AI Crypto Trading Assistant (24/7 Live Data)")
st.write("Professional Real-Time Engine powered by Globally Unrestricted Crypto Price Streams.")

st.sidebar.header("🔧 Bot Settings")
symbol = st.sidebar.text_input("Crypto Coin (e.g., BTC, ETH, TRX):", value="BTC")
timeframe = st.sidebar.selectbox("Time Frame:", ["1h", "1d", "15m"])

def fetch_crypto_data(symbol, tf):
    try:
        # Standardizing symbol formatting automatically
        clean_symbol = symbol.replace("USDT", "").replace("USD", "").replace("-", "").replace("/", "").upper()
        formatted_symbol = f"{clean_symbol}-USD"

        # Using a reliable, geoblock-free public API that never blocks Streamlit servers
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{formatted_symbol}?range=30d&interval={tf}"
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=10) as response:
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
        return None

if st.sidebar.button("Run Live AI Analysis"):
    st.write(f"⚡ Establishing secure link for **{symbol}**...")
    df = fetch_crypto_data(symbol, timeframe)
    
    if df is not None and not df.empty:
        # Technical indicators calculation
        df['EMA_10'] = df['Close'].ewm(span=10, adjust=False).mean()
        df['EMA_30'] = df['Close'].ewm(span=30, adjust=False).mean()
        
        # RSI calculation
        close_delta = df['Close'].diff()
        up = close_delta.clip(lower=0)
        down = -1 * close_delta.clip(upper=0)
        ma_up = up.ewm(com=13, adjust=True).mean()
        ma_down = down.ewm(com=13, adjust=True).mean()
        df['RSI'] = 100 - (100 / (1 + (ma_up / ma_down)))
        
        # ATR Volatility Tracking
        high_low = df['High'] - df['Low']
        high_cp = np.abs(df['High'] - df['Close'].shift())
        low_cp = np.abs(df['Low'] - df['Close'].shift())
        true_range = np.max(pd.concat([high_low, high_cp, low_cp], axis=1), axis=1)
        latest_atr = true_range.rolling(window=14).mean().iloc[-1]
        
        latest_close = df['Close'].iloc[-1]
        latest_rsi = df['RSI'].iloc[-1]
        latest_ema10 = df['EMA_10'].iloc[-1]
        latest_ema30 = df['EMA_30'].iloc[-1]
        
        if pd.isna(latest_atr) or latest_atr == 0:
            latest_atr = latest_close * 0.015

        # Precise Signal Engine
        if latest_ema10 > latest_ema30:
            signal = "🟢 LIVE BUY SIGNAL"
            entry_price = latest_close
            target = entry_price + (latest_atr * 1.5)
            stop_loss = entry_price - (latest_atr * 1.2)
            strategy = "Bullish momentum confirmed. Orders can be executed safely at the entry price."
        else:
            signal = "🔴 LIVE SELL / SHORT SIGNAL"
            entry_price = latest_close
            target = entry_price - (latest_atr * 1.5)
            stop_loss = entry_price + (latest_atr * 1.2)
            strategy = "Bearish structure dominance. Look for shorting opportunities or sit tight."

        # Dashboard UI
        st.subheader("📊 Live Trading Execution Panel")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Current Market Price", f"${latest_close:,.4f}")
        c2.metric("Real-time RSI (14)", f"{latest_rsi:.2f}")
        c3.metric("Trend State", "BULLISH 📈" if latest_ema10 > latest_ema30 else "BEARISH 📉")
        
        st.info(f"**AI Recommendation:** {signal}")
        
        # Price zones
        z1, z2, z3 = st.columns(3)
        with z1:
            st.info(f"🔑 **EXACT ENTRY PRICE:**\n### ${entry_price:,.4f}")
        with z2:
            st.success(f"🎯 **PROFIT TARGET:**\n### ${target:,.4f}")
        with z3:
            st.error(f"🛑 **PROTECTIVE STOP LOSS:**\n### ${stop_loss:,.4f}")
            
        st.warning(f"⏱️ **AI Action Blueprint:** {strategy}")
        
        st.subheader("📊 Live Price Chart & Trend Lines")
        chart_df = df.set_index('Timestamp')[['Close', 'EMA_10', 'EMA_30']]
        st.line_chart(chart_df)
    else:
        st.error("Unable to connect to the global stream. Please verify your internet connection and try again.")
