import streamlit as st
import pandas as pd
import numpy as np
import urllib.request
import json

st.set_page_config(page_title="AI Crypto Bot - Legends Edition", layout="wide")
st.title("🧙‍♂️ Legends Edition: AI Crypto Trading Engine")
st.write("Professional-grade analysis system using institutional trend filters and strict entry metrics.")

st.sidebar.header("🔧 Institutional Settings")
symbol = st.sidebar.text_input("Crypto Coin (e.g., BTC, ETH, TRX):", value="BTC")
timeframe = st.sidebar.selectbox("Time Frame:", ["1h", "1d", "15m"])

def fetch_crypto_data(symbol, tf):
    try:
        clean_symbol = symbol.replace("USDT", "").replace("USD", "").replace("-", "").replace("/", "").upper()
        formatted_symbol = f"{clean_symbol}-USD"
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
    except Exception:
        return None

def calculate_rsi(df, periods=14):
    close_delta = df['Close'].diff()
    up = close_delta.clip(lower=0)
    down = -1 * close_delta.clip(upper=0)
    ma_up = up.ewm(com=periods - 1, adjust=True).mean()
    ma_down = down.ewm(com=periods - 1, adjust=True).mean()
    return 100 - (100 / (1 + (ma_up / ma_down)))

if st.sidebar.button("Execute Legends Analysis"):
    st.write(f"⚡ Processing institutional data stream for **{symbol}**...")
    df = fetch_crypto_data(symbol, timeframe)
    
    if df is not None and not df.empty:
        # Technical Indicators Setup
        df['EMA_Fast'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['EMA_Slow'] = df['Close'].ewm(span=21, adjust=False).mean()
        df['Trend_Filter'] = df['Close'].ewm(span=50, adjust=False).mean()
        df['RSI'] = calculate_rsi(df)
        
        # ATR Calculation for Dynamic Risk Placement
        high_low = df['High'] - df['Low']
        high_cp = np.abs(df['High'] - df['Close'].shift())
        low_cp = np.abs(df['Low'] - df['Close'].shift())
        true_range = np.max(pd.concat([high_low, high_cp, low_cp], axis=1), axis=1)
        latest_atr = true_range.rolling(window=14).mean().iloc[-1]
        
        latest_close = df['Close'].iloc[-1]
        latest_rsi = df['RSI'].iloc[-1]
        latest_fast = df['EMA_Fast'].iloc[-1]
        latest_slow = df['EMA_Slow'].iloc[-1]
        latest_filter = df['Trend_Filter'].iloc[-1]
        
        if pd.isna(latest_atr) or latest_atr == 0:
            latest_atr = latest_close * 0.02

        # --- LEGENDS INSTITUTIONAL CONFLUENCE LOGIC ---
        # Buy Setup: Price above 50 EMA + Fast EMA above Slow EMA + RSI not overbought
        if latest_close > latest_filter and latest_fast > latest_slow and 40 < latest_rsi < 68:
            signal = "🟢 INSTITUTIONAL BUY ENTRY"
            entry_price = latest_close
            target = entry_price + (latest_atr * 2.0)     # Strict 1:2 Risk-to-Reward Ratio
            stop_loss = entry_price - (latest_atr * 1.0)
            strategy = "High probability bullish breakout structure. Confluence filters confirmed."
            
        # Sell Setup: Price below 50 EMA + Fast EMA below Slow EMA + RSI not oversold
        elif latest_close < latest_filter and latest_fast < latest_slow and 32 < latest_rsi < 60:
            signal = "🔴 INSTITUTIONAL SHORT ENTRY"
            entry_price = latest_close
            target = entry_price - (latest_atr * 2.0)     # Strict 1:2 Risk-to-Reward Ratio
            stop_loss = entry_price + (latest_atr * 1.0)
            strategy = "High probability bearish breakdown structure. Downward momentum confirmed."
            
        # Neutral Setup: If conditions don't match, it means market is unsafe / choppy
        else:
            signal = "⚪ NO TRADE ZONE (High Risk / False Signal Filtered)"
            entry_price = latest_close
            target = latest_close
            stop_loss = latest_close
            strategy = "Market conditions do not meet strict institutional rules. Standing aside to protect capital."

        # Render Dashboard
        st.subheader("📊 Professional Trade Execution Panel")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Asset Valuation (Price)", f"${latest_close:,.4f}")
        c2.metric("Momentum Matrix (RSI)", f"{latest_rsi:.2f}")
        c3.metric("Macro Trend Structure", "BULLISH 📈" if latest_close > latest_filter else "BEARISH 📉")
        
        if "BUY" in signal:
            st.success(f"**Execution Signal:** {signal}")
        elif "SHORT" in signal:
            st.error(f"**Execution Signal:** {signal}")
        else:
            st.info(f"**Execution Signal:** {signal}")
            
        # Execution Price Mapping
        z1, z2, z3 = st.columns(3)
        with z1:
            st.info(f"🔑 **OPTIMAL ENTRY PRICE:**\n### ${entry_price:,.4f}")
        with z2:
            st.success(f"🎯 **LEGENDS TARGET (TP):**\n### ${target:,.4f}")
        with z3:
            st.error(f"🛑 **LEGENDS STOP LOSS (SL):**\n### ${stop_loss:,.4f}")
            
        st.warning(f"⏱️ **Strategic Roadmap:** {strategy}")
        
        st.subheader("📊 Multi-EMA Institutional Price Chart")
        chart_df = df.set_index('Timestamp')[['Close', 'EMA_Fast', 'EMA_Slow', 'Trend_Filter']]
        st.line_chart(chart_df)
    else:
        st.error("Data stream interrupted. Please refresh or verify the symbol input.")
