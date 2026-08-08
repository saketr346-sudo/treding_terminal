import plotly.graph_objects as go
import streamlit as st
from datetime import datetime
import time

from data_fetcher import get_stock_data, get_indices_data, get_nifty50_gainers_losers
from nlp_sentiment import analyze_news_sentiment
from ml_model import predict_stock_levels

# 1. Page Config & Dynamic Button Styling
st.set_page_config(page_title="Trading Terminal", layout="wide", page_icon="⚡")

st.markdown("""
<style>
    div[data-testid="stMetricValue"] { font-size: 25px !important; font-weight: 700 !important; }
    div[data-testid="stMetricLabel"] { font-size: 16px !important; font-weight: 600 !important; color: #8b949e !important; }
    div[data-testid="stMetricDelta"] { font-size: 15px !important; }
    .block-container { padding-top: 0.8rem !important; padding-bottom: 1rem !important; }
    
    .alert-box-buy {
        background-color: rgba(16, 185, 129, 0.15);
        border: 1px solid #10b981;
        color: #10b981;
        padding: 10px 14px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 14px;
        margin-bottom: 10px;
    }
    .alert-box-sell {
        background-color: rgba(239, 68, 68, 0.15);
        border: 1px solid #ef4444;
        color: #ef4444;
        padding: 10px 14px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 14px;
        margin-bottom: 10px;
    }
    
    /* Dynamic HTML Button Styling */
    .btn-buy {
        background-color: #10b981 !important;
        color: white !important;
        padding: 10px 20px;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
        font-size: 16px;
        cursor: pointer;
        display: block;
        text-decoration: none;
        border: none;
        box-shadow: 0px 4px 10px rgba(16, 185, 129, 0.3);
    }
    .btn-sell {
        background-color: #ef4444 !important;
        color: white !important;
        padding: 10px 20px;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
        font-size: 16px;
        cursor: pointer;
        display: block;
        text-decoration: none;
        border: none;
        box-shadow: 0px 4px 10px rgba(239, 68, 68, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# Session State
if "ticker_list" not in st.session_state:
    st.session_state.ticker_list = [
        "PAYTM.NS", "RELIANCE.NS", "TCS.NS", "INFY.NS",
        "HDFCBANK.NS", "TMPV.NS", "SBIN.NS", "ICICIBANK.NS"
    ]

# 2. Sidebar Navigation
with st.sidebar:
    st.title("Navigation bar")
    auto_refresh = st.toggle("Enable Live Auto-Refresh", value=True)
    refresh_interval = st.number_input("Refresh Interval (Seconds)", min_value=1, value=5, step=1)
    st.markdown("---")
    symbol = st.selectbox("▼ Select Asset / Search Ticker 🔽", options=st.session_state.ticker_list, index=0)
    st.markdown("---")
    custom_symbol = st.text_input("➕ Type New Ticker (e.g. WIPRO.NS)", value="", placeholder="Type and press Enter...")
    if custom_symbol:
        formatted_symbol = custom_symbol.strip().upper()
        if formatted_symbol not in st.session_state.ticker_list:
            st.session_state.ticker_list.insert(0, formatted_symbol)
            st.rerun()
        symbol = formatted_symbol

    timeframe = st.selectbox("Timeframe", ["1M", "3M", "6M", "1Y","3Y","5Y","10Y"], index=0)
    enable_alerts = st.toggle("Enable Real-Time Signals", value=True)
    
    col_t, col_sl = st.columns(2)
    with col_t: custom_target = st.number_input("Target (₹)", value=0.0, step=1.0)
    with col_sl: custom_sl = st.number_input("StopLoss (₹)", value=0.0, step=1.0)

# Fetch Stock Data
data = get_stock_data(symbol)

if data:
    ltp = data['ltp']
    hist = data["history"]
    
    # 1. Technical Calculations
    hist['MA20'] = hist['Close'].rolling(window=20).mean()
    ma20_curr = round(hist['MA20'].iloc[-1], 2)
    
    delta = hist['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    hist['RSI'] = 100 - (100 / (1 + rs))
    rsi_curr = round(hist['RSI'].iloc[-1], 2) if not hist['RSI'].empty else 50.0

    exp1 = hist['Close'].ewm(span=12, adjust=False).mean()
    exp2 = hist['Close'].ewm(span=26, adjust=False).mean()
    hist['MACD'] = exp1 - exp2
    hist['Signal_Line'] = hist['MACD'].ewm(span=9, adjust=False).mean()
    macd_curr = hist['MACD'].iloc[-1]
    macd_signal_curr = hist['Signal_Line'].iloc[-1]

    hist['STD20'] = hist['Close'].rolling(window=20).std()
    hist['Upper_Band'] = hist['MA20'] + (hist['STD20'] * 2)
    hist['Lower_Band'] = hist['MA20'] - (hist['STD20'] * 2)

    # Dynamic News & Sentiment Binding (Stock Change ke hisab se dynamically calculated)
    dynamic_sentiment_base = 50 + (data['percent_change'] * 5) + ((rsi_curr - 50) * 0.5)
    dynamic_sentiment_score = max(10, min(95, round(dynamic_sentiment_base, 1)))

    sample_news = [
        {"title": f"{symbol} price momentum tracking at {data['percent_change']}%.", "tag": "BULLISH" if data['percent_change'] >= 0 else "BEARISH", "score": dynamic_sentiment_score},
        {"title": f"Technical Indicators: RSI at {rsi_curr} & 20 MA at ₹{ma20_curr}.", "tag": "NEUTRAL", "score": 55},
    ]

    # Predict Stock Levels Dynamically
    predictions = predict_stock_levels(ltp, dynamic_sentiment_score)

    # Multi-Factor Confluence Checks
    is_ma_bull = ltp > ma20_curr
    is_rsi_bull = rsi_curr > 60
    is_macd_bull = macd_curr > macd_signal_curr
    is_nlp_bull = dynamic_sentiment_score > 60

    active_factors = sum([is_ma_bull, is_rsi_bull, is_macd_bull, is_nlp_bull])
    model_accuracy = round((active_factors / 4) * 100, 1)

    # Dynamic Signal Decision & Button Classes
    if is_ma_bull and is_rsi_bull and is_macd_bull:
        signal_type = "BUY"
        btn_class = "btn-buy"
        signal_class = "alert-box-buy"
        signal_msg = f" <b>STRONG BUY SIGNAL:</b> Price > 20 MA, RSI ({rsi_curr}) > 60 & MACD Crossover."
    elif ltp < ma20_curr or macd_curr < macd_signal_curr:
        signal_type = "SELL"
        btn_class = "btn-sell"
        signal_class = "alert-box-sell"
        signal_msg = f" <b>BEARISH SIGNAL:</b> Price below 20 MA / MACD Weak."
    else:
        signal_type = "HOLD / NEUTRAL"
        btn_class = "btn-sell"
        signal_class = "alert-box-buy"
        signal_msg = f"ℹ️ <b>CONSOLIDATION:</b> Mixed technical signals."

    st.caption(f"📡 Real-Time Data Sync | Last Refreshed: {datetime.now().strftime('%d %b %Y, %I:%M:%S %p IST')}")
    if enable_alerts:
        st.markdown(f"<div class='{signal_class}'>{signal_msg}</div>", unsafe_allow_html=True)

    # Market Indices Section
    st.markdown("##### index ")
    indices = get_indices_data()
    i1, i2, i3, i4, i5 = st.columns(5)
    for name, col in [("NIFTY 50", i1), ("SENSEX", i2), ("BANK NIFTY", i3), ("NIFTY IT", i4), ("GOLD", i5)]:
        item = indices.get(name, {"price": "24,500.00", "change": 120.50, "pct": 0.50})
        with col:
            with st.container(border=True):
                st.metric(label=name, value=f"₹{item['price']}", delta=f"{item['change']:+} ({item['pct']:+}%)")

    st.markdown("---")

    # Asset Metrics
    st.markdown(f"##### 📈 Stock: {symbol}")
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    with m1: st.metric(label="LTP", value=f"₹{ltp}")
    with m2: st.metric(label="Change", value=f"₹{data['change']}", delta=f"{data['percent_change']}%")
    with m3: st.metric(label="Day High", value=f"₹{data['day_high']}")
    with m4: st.metric(label="Day Low", value=f"₹{data['day_low']}")
    with m5: st.metric(label="52W High", value=f"₹{data['week_52_high']}")
    with m6: st.metric(label="52W Low", value=f"₹{data['week_52_low']}")

    st.markdown("<br>", unsafe_allow_html=True)

    # SECTION 3: ML + NLP Trade Setup & Top Gainers/Losers
    left_half, right_half = st.columns(2)

    with left_half:
        with st.container(border=True):
            st.subheader("Trade Setup")
            
            # Accuracy Badge
            st.markdown(f"""
            <div style="background-color: rgba(0, 102, 204, 0.15); border: 1px solid #0066cc; padding: 6px 12px; border-radius: 6px; font-size: 13px; font-weight: bold; margin-bottom: 12px;">
                🎯 Confluence Accuracy: <span style="color:#10b981;">{model_accuracy}%</span> | RSI: {rsi_curr} | MACD: {'Bullish' if is_macd_bull else 'Bearish'}
            </div>
            """, unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                st.caption("Potential Upside")
                st.markdown(f"<h2 style='color: #0066cc; margin:0; font-size:28px;'>▲ +{predictions['potential_upside']}%</h2>", unsafe_allow_html=True)
            with c2:
                st.caption("Current LTP")
                st.markdown(f"<h3 style='margin:0; font-size:24px;'>₹{data['ltp']}</h3>", unsafe_allow_html=True)
            
            st.progress(dynamic_sentiment_score / 100)
            
            p1, p2, p3 = st.columns(3)
            with p1:
                st.caption("Stop Loss")
                st.markdown(f"### ₹{predictions['stop_loss']}")
            with p2:
                st.caption("Entry Price")
                st.markdown(f"### ₹{predictions['entry_price']}")
            with p3:
                st.caption("Target")
                st.markdown(f"### ₹{predictions['target_price']}")

            st.markdown("<br>", unsafe_allow_html=True)

            # Dynamic Green/Red Execute Button Render
            st.markdown(f"""
                <button class='{btn_class}' onclick="window.location.reload();">
                    ⚡ Execute Signal ({signal_type})
                </button>
            """, unsafe_allow_html=True)

    with right_half:
        with st.container(border=True):
            st.subheader("📊 Market Top Gainers & Losers")
            tab_gainers, tab_losers = st.tabs(["🔥 TOP GAINERS", "🔻 TOP LOSERS"])
            gainers_data, losers_data = get_nifty50_gainers_losers()

            with tab_gainers:
                for stock_item in gainers_data:
                    c1, c2 = st.columns([2, 1])
                    with c1: st.markdown(f"**{stock_item['Symbol']}**")
                    with c2: st.markdown(f"<div style='text-align: right; color: #10b981; font-size: 13px;'><b>{stock_item['LTP']}</b><br>{stock_item['Change']}</div>", unsafe_allow_html=True)
                    st.markdown("<hr style='margin:2px 0;'>", unsafe_allow_html=True)

            with tab_losers:
                for stock_item in losers_data:
                    c1, c2 = st.columns([2, 1])
                    with c1: st.markdown(f"**{stock_item['Symbol']}**")
                    with c2: st.markdown(f"<div style='text-align: right; color: #ef4444; font-size: 13px;'><b>{stock_item['LTP']}</b><br>{stock_item['Change']}</div>", unsafe_allow_html=True)
                    st.markdown("<hr style='margin:2px 0;'>", unsafe_allow_html=True)

    st.markdown("---")
# -------------------------------------------------------------
    # SECTION 4: Price Action Chart (Groww Style) & Live Sentiment
    # -------------------------------------------------------------
    chart_col, news_col = st.columns([2, 1])

    # LEFT: Groww Terminal Styled Technical Chart
    with chart_col:
        with st.container(border=True):
            st.subheader("Technical Chart")
            
            from plotly.subplots import make_subplots
            
            # Groww style subplot layout: 80% Price Chart, 20% Volume Chart
            fig = make_subplots(
                rows=2, cols=1, 
                shared_xaxes=True, 
                vertical_spacing=0.02, 
                row_heights=[0.80, 0.20]
            )

            # 1. Groww Signature Candlestick Colors (#00D09C Green & #FF5353 Red)
            fig.add_trace(go.Candlestick(
                x=hist.index,
                open=hist['Open'],
                high=hist['High'],
                low=hist['Low'],
                close=hist['Close'],
                name="OHLC",
                increasing_line_color='#00D09C',
                increasing_fillcolor='#00D09C',
                decreasing_line_color='#FF5353',
                decreasing_fillcolor='#FF5353'
            ), row=1, col=1)

            # 2. 20-Period Moving Average (Clean Groww Cyan/Blue line)
            fig.add_trace(go.Scatter(
                x=hist.index, y=hist['MA20'], 
                mode='lines', name='20 MA',
                line=dict(color='#00B8D9', width=1.8)
            ), row=1, col=1)

            # 3. Bollinger Bands (Soft Subdued Bands)
            fig.add_trace(go.Scatter(
                x=hist.index, y=hist['Upper_Band'], 
                mode='lines', name='Upper Band',
                line=dict(color='rgba(0, 208, 156, 0.3)', width=1, dash='dash')
            ), row=1, col=1)

            fig.add_trace(go.Scatter(
                x=hist.index, y=hist['Lower_Band'], 
                mode='lines', name='Lower Band',
                line=dict(color='rgba(255, 83, 83, 0.3)', width=1, dash='dash'),
                fill='tonexty', fillcolor='rgba(255, 255, 255, 0.015)'
            ), row=1, col=1)

            # 4. Groww Style Volume Bars (Matching Candle Colors)
            volume_colors = ['#00D09C' if c >= o else '#FF5353' for c, o in zip(hist['Close'], hist['Open'])]
            fig.add_trace(go.Bar(
                x=hist.index, y=hist['Volume'],
                name='Volume',
                marker_color=volume_colors,
                opacity=0.6
            ), row=2, col=1)

            # Groww Dark Theme Canvas & Layout Options
            fig.update_layout(
                height=480,
                margin=dict(l=10, r=10, t=25, b=10),
                xaxis_rangeslider_visible=False,
                paper_bgcolor='#121418',
                plot_bgcolor='#121418',
                font=dict(color='#8C96A3', family='Inter, sans-serif'),
                hovermode="x unified",
                legend=dict(
                    orientation="h", 
                    yanchor="bottom", 
                    y=1.01, 
                    xanchor="right", 
                    x=1,
                    font=dict(size=12, color='#A3B1C2')
                )
            )

            # Groww Style Clean Grid Lines Setup
            fig.update_xaxes(
                showgrid=True, 
                gridcolor='#1E222D', 
                zeroline=False,
                showline=True, 
                linecolor='#1E222D'
            )
            fig.update_yaxes(
                showgrid=True, 
                gridcolor='#1E222D', 
                zeroline=False,
                showline=True, 
                linecolor='#1E222D',
                row=1, col=1
            )
            fig.update_yaxes(
                showgrid=False, 
                showticklabels=False, 
                row=2, col=1
            )

            st.plotly_chart(fig, use_container_width=True)
# News Feed
    with news_col:
        with st.container(border=True):
            st.subheader("📰News Sentiment Feed")
            st.write(f"**Overall Sentiment Score:** {dynamic_sentiment_score}% Bullish")
            st.progress(dynamic_sentiment_score / 100)
            for item in sample_news:
                st.markdown(f"**{item['title']}**")
                st.caption(f"Sentiment Impact: {item['tag']} ({item['score']}%)")
                st.markdown("<hr style='margin:2px 0;'>", unsafe_allow_html=True)

else:
    st.error("Invalid Stock Ticker or Data Unavailable.")

if 'auto_refresh' in locals() and auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()
