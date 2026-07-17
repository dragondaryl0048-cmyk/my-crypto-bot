import streamlit as st
import pandas as pd
import numpy as np
import urllib.request
import json

st.set_page_config(page_title="Smart AI Crypto Bot Dashboard", layout="wide")
st.title("🧠 Smart AI Crypto Trading Engine (Advanced Decision Maker)")
st.write("Next-Gen AI Bot using Dynamic Market Filters, Volatility Tracking, and Trend Strength Assessment.")

st.sidebar.header("🔧 Bot Settings")
symbol = st.sidebar.text_input("Crypto Coin (e.g., BTC-USD, ETH-USD):", value="BTC-USD")
timeframe = st.sidebar.selectbox("Time Frame:", ["1d", "4h", "1h", "15m"])

def fetch_data(symbol, tf):
    try:
        formatted_symbol = symbol.replace("USDT", "USD").replace("/", "-").upper()
        if "-" not in formatted_symbol:
            formatted_symbol = f"{formatted_symbol}-USD"

        # Dynamically set data range based on timeframe
        if tf == "1d":
            data_range = "180d"
        elif tf == "4h":
            data_range = "60d"
            tf = "1h" # Fallback mapped to 1h for stable granularity
        else:
            data_range = "30d"
        
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

# Advanced ATR (Average True Range) for Smart SL/TP
def calculate_atr(df, period=14):
    high_low = df['High'] - df['Low']
    high_cp = np.abs(df['High'] - df['Close'].shift())
    low_cp = np.abs(df['Low'] - df['Close'].shift())
    df_tr = pd.concat([high_low, high_cp, low_cp], axis=1)
    true_range = np.max(df_tr, axis=1)
    atr = true_range.rolling(window=period).mean()
    return atr

if st.sidebar.button("Run Smart AI Analysis"):
    st.write(f"🔍 Fetching global chart data stream for **{symbol}**...")
    df = fetch_data(symbol, timeframe)
    
    if df is not None and not df.empty:
        # Technical Calculations
        df['EMA_10'] = df['Close'].ewm(span=10, adjust=False).mean()
        df['EMA_30'] = df['Close'].ewm(span=30, adjust=False).mean()
        df['RSI'] = calculate_rsi(df)
        df['ATR'] = calculate_atr(df)
        
        # Smart Volume Filter (Comparing current volume with 20-period average volume)
        df['Vol_MA'] = df['Volume'].rolling(window=20).mean()
        
        # Trend Strength Filter (Dynamically tracking price swings to spot low-activity sideways traps)
        df['Price_Range'] = (df['High'].rolling(10).max() - df['Low'].rolling(10).min()) / df['Close']
        avg_range = df['Price_Range'].rolling(20).mean().iloc[-1]
        
        # Latest Values
        latest_close = df['Close'].iloc[-1]
        latest_rsi = df['RSI'].iloc[-1]
        latest_ema10 = df['EMA_10'].iloc[-1]
        latest_ema30 = df['EMA_30'].iloc[-1]
        latest_atr = df['ATR'].iloc[-1]
        latest_vol = df['Volume'].iloc[-1]
        avg_vol = df['Vol_MA'].iloc[-1]
        current_range = df['Price_Range'].iloc[-1]

        if pd.isna(latest_atr) or latest_atr == 0:
            latest_atr = latest_close * 0.015

        # Trend and Volume Strength Analysis
        strong_trend = current_range > (avg_range * 0.8)  # True if market is actually moving, False if in a tight flat range
        healthy_volume = latest_vol > (avg_vol * 0.9)     # True if volume supports the move

        # Visual Dashboard Metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Current Price", f"${latest_close:,.4f}")
        col2.metric("Latest RSI (14)", f"{latest_rsi:.2f}")
        
        if strong_trend:
            col3.metric("Market State", "Trending 🔥", delta="Active")
        else:
            col3.metric("Market State", "Sideways 💤", delta="Low Volatility")
            
        if latest_ema10 > latest_ema30:
            col4.metric("Direction", "Bullish (Up)", delta_color="normal")
        else:
            col4.metric("Direction", "Bearish (Down)", delta_color="inverse")

        st.subheader("📊 AI Smart Trading Decision")
        
        # --- NEXT-GEN DYNAMIC TRADING LOGIC ---
        
        # Block entries if the market is stuck in a low-volatility range (Preventing false signals)
        if not strong_trend:
            signal = "⚪ NO TRADE / WAIT (Sideways Market Trap)"
            target = latest_close
            stop_loss = latest_close
            best_time = "The market is flat. Indicated crossovers are likely false. Wait for a breakout."
            st.info(f"**Recommendation:** {signal}")
            
        # 1. Smart Buy Signal
        elif latest_ema10 > latest_ema30 and latest_rsi < 65 and healthy_volume:
            signal = "🟢 SMART BUY SIGNAL (Trend Confirmed by Volume)"
            target = latest_close + (latest_atr * 2.0)      # Risk-Reward 1:2 Setup
            stop_loss = latest_close - (latest_atr * 1.0)
            best_time = "Healthy breakout with supportive volume. Good entry window."
            st.success(f"**Recommendation:** {signal}")
            
        # 2. Overbought State (Risk Reduction)
        elif latest_rsi >= 70:
            signal = "⚠️ RISK WARNING (Overbought Market)"
            target = latest_close + (latest_atr * 0.5)
            stop_loss = latest_close - (latest_atr * 1.2)
            best_time = "RSI is extremely high. Trend might reverse shortly. Avoid buying here."
            st.warning(f"**Recommendation:** {signal}")
            
        # 3. Smart Sell Signal
        elif latest_ema10 < latest_ema30 and latest_rsi > 35:
            signal = "🔴 SMART SELL SIGNAL (Bearish Trend Expansion)"
            target = latest_close - (latest_atr * 2.0)      # Risk-Reward 1:2 Setup
            stop_loss = latest_close + (latest_atr * 1.0)
            best_time = "Sell/Short momentum has begun. Avoid long entries."
            st.error(f"**Recommendation:** {signal}")
            
        # 4. Fallback Neutral
        else:
            signal = "⚪ NEUTRAL (Consolidation Phase)"
            target = latest_close
            stop_loss = latest_close
            best_time = "Volume or trend structure is weak. Best to wait for clear market direction."
            st.info(f"**Recommendation:** {signal}")

        # Target and SL Output
        if signal != "⚪ NO TRADE / WAIT (Sideways Market Trap)":
            col_a, col_b = st.columns(2)
            with col_a:
                st.success(f"🎯 **Smart Target:** ${target:,.4f}")
                st.warning(f"⏱️ **AI Action Plan:** {best_time}")
            with col_b:
                st.error(f"🛑 **Smart Stop Loss:** ${stop_loss:,.4f}")
        else:
            st.warning(f"**AI Action Plan:** {best_time}")
            
        st.subheader("📊 Price Chart (EMA Trend Visualization)")
        chart_df = df.set_index('Timestamp')[['Close', 'EMA_10', 'EMA_30']]
        st.line_chart(chart_df)
