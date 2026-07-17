import streamlit as st
import pandas as pd
import numpy as np
import urllib.request
import json

st.set_page_config(page_title="AI Crypto Bot Dashboard - Pro+", layout="wide")
st.title("🤖 Advanced AI Crypto Trading Assistant (Pro+)")
st.write("Professional Bot for analyzing multi-coins with EMA, RSI, MACD, and ATR indicators.")

st.sidebar.header("🔧 Bot Settings")
symbol = st.sidebar.text_input("Crypto Coin (e.g., BTC-USD, ETH-USD, SOL-USD):", value="BTC-USD")
timeframe = st.sidebar.selectbox("Time Frame:", ["1h", "1d", "15m"])

def fetch_data(symbol, tf):
    try:
        # Standardizing format for Yahoo Finance Binance mirror (e.g., BTCUSDT -> BTC-USD)
        formatted_symbol = symbol.replace("USDT", "USD").replace("/", "-").upper()
        if "-" not in formatted_symbol:
            formatted_symbol = f"{formatted_symbol}-USD"

        # Dynamically set range based on timeframe for sufficient historical data
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
        st.sidebar.error(f"Data Fetching Error: {e}. Please use formats like BTC-USD.")
        return None

# Advanced RSI Calculation
def calculate_rsi(df, periods=14):
    close_delta = df['Close'].diff()
    up = close_delta.clip(lower=0)
    down = -1 * close_delta.clip(upper=0)
    ma_up = up.ewm(com=periods - 1, adjust=True).mean()
    ma_down = down.ewm(com=periods - 1, adjust=True).mean()
    rsi = ma_up / ma_down
    rsi = 100 - (100 / (1 + rsi))
    return rsi

# Advanced MACD Calculation
def calculate_macd(df):
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    return macd, signal

# Advanced ATR (Average True Range) for accurate Volatility & Stop Loss
def calculate_atr(df, period=14):
    high_low = df['High'] - df['Low']
    high_cp = np.abs(df['High'] - df['Close'].shift())
    low_cp = np.abs(df['Low'] - df['Close'].shift())
    df_tr = pd.concat([high_low, high_cp, low_cp], axis=1)
    true_range = np.max(df_tr, axis=1)
    atr = true_range.rolling(window=period).mean()
    return atr

if st.sidebar.button("Run Advanced AI Analysis"):
    st.write(f"🔍 Fetching global chart data stream for **{symbol}**...")
    df = fetch_data(symbol, timeframe)
    
    if df is not None and not df.empty:
        # Technical Calculations
        df['EMA_10'] = df['Close'].ewm(span=10, adjust=False).mean()
        df['EMA_30'] = df['Close'].ewm(span=30, adjust=False).mean()
        df['RSI'] = calculate_rsi(df)
        df['MACD'], df['MACD_Signal'] = calculate_macd(df)
        df['ATR'] = calculate_atr(df)
        
        # Latest Values
        latest_close = df['Close'].iloc[-1]
        latest_rsi = df['RSI'].iloc[-1]
        latest_ema10 = df['EMA_10'].iloc[-1]
        latest_ema30 = df['EMA_30'].iloc[-1]
        latest_macd = df['MACD'].iloc[-1]
        latest_macd_sig = df['MACD_Signal'].iloc[-1]
        latest_atr = df['ATR'].iloc[-1]
        
        # Fallback if ATR is not calculated yet
        if pd.isna(latest_atr) or latest_atr == 0:
            latest_atr = latest_close * 0.015

        # Visual Metrics Dashboard
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Current Price", f"${latest_close:,.4f}")
        col2.metric("Latest RSI (14)", f"{latest_rsi:.2f}")
        col3.metric("Trend (EMA Crossover)", "BULLISH 📈" if latest_ema10 > latest_ema30 else "BEARISH 📉")
        col4.metric("MACD Momentum", "BUY FOCUS" if latest_macd > latest_macd_sig else "SELL FOCUS")
        
        st.subheader("📊 AI Technical & Risk Analysis")
        
        # --- Multi-Indicator Pro Trading Logic ---
        # 1. Bullish Entry (EMA crossover is positive, RSI is healthy, MACD confirms momentum)
        if latest_ema10 > latest_ema30 and latest_rsi < 65 and latest_macd > latest_macd_sig:
            signal = "🟢 STRONG BUY SIGNAL (Strong Bullish Convergence)"
            target = latest_close + (latest_atr * 2.0)     # Target based on ATR volatility
            stop_loss = latest_close - (latest_atr * 1.5)  # Stop loss set safely below ATR volatility
            best_time = "RSI & MACD confirm solid momentum. Enter immediately or on minor pullback."
            
        # 2. Overbought State (High Risk)
        elif latest_rsi >= 70:
            signal = "⚠️ WATCH OUT / TAKE PROFIT (Market is Overbought)"
            target = latest_close + (latest_atr * 0.5)
            stop_loss = latest_close - (latest_atr * 1.2)
            best_time = "Buying pressure is exhausting. Do not chase. Consider taking profits."
            
        # 3. Bearish Trend (EMA is negative or MACD indicates selling pressure)
        elif latest_ema10 < latest_ema30 or latest_macd < latest_macd_sig:
            signal = "🔴 STRONG SELL / WAIT (Bearish Structure Detected)"
            target = latest_close - (latest_atr * 2.0)
            stop_loss = latest_close + (latest_atr * 1.5)
            best_time = "Trend is down. Stay on sidelines or focus on shorting opportunities."
            
        # 4. Neutral Sideways Market
        else:
            signal = "⚪ NEUTRAL / WAIT (No Clear Trend)"
            target = latest_close
            stop_loss = latest_close
            best_time = "Market is moving sideways. High risk of getting chopped. Best to wait."

        # Output Results
        st.info(f"**Recommendation:** {signal}")
        col_a, col_b = st.columns(2)
        with col_a:
            st.success(f"🎯 **Expected Target (Volatility-Adjusted):** ${target:,.4f}")
            st.warning(f"⏱️ **Trading Action:** {best_time}")
        with col_b:
            st.error(f"🛑 **Stop Loss (Volatility-Adjusted):** ${stop_loss:,.4f}")
            
        st.subheader("📊 Advanced Price Chart (with EMA 10 & 30 Overlay)")
        # Displaying the Price together with EMA lines on the chart
        chart_df = df.set_index('Timestamp')[['Close', 'EMA_10', 'EMA_30']]
        st.line_chart(chart_df)
