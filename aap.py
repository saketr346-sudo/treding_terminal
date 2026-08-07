import streamlit as st
import plotly.graph_objects as go
from datetime import datetime

from data_fetcher import get_stock_data, get_indices_data
from nlp_sentiment import analyze_news_sentiment
from ml_model import predict_stock_levels

# 1. Page Config & Professional Dark Theme Styling
st.set_page_config(page_title="Institutional Trading Terminal", layout="wide", page_icon="⚡")

st.markdown("""
<style>
    /* Global Typography & Font Adjustments */
    div[data-testid="stMetricValue"] {
        font-size: 20px !important;
        font-weight: 700 !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 13px !important;
        font-weight: 600 !important;
        color: #8b949e !important;
    }
    div[data-testid="stMetricDelta"] {
        font-size: 12px !important;
    }
    .block-container {
        padding-top: 0.8rem !important;
        padding-bottom: 1rem !important;
    }
    .stAlert {
        padding: 8px 12px !important;
    }
    /* Pro Alert Badge Styling */
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
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# SESSION STATE: Automatic History / Recently Selected Tickers
# -------------------------------------------------------------
if "ticker_list" not in st.session_state:
    st.session_state.ticker_list = [
        "PAYTM.NS",
        "RELIANCE.NS",
        "TCS.NS",
        "INFY.NS",
        "HDFCBANK.NS",
        "TMPV.NS",
        "SBIN.NS",
        "ICICIBANK.NS"
    ]
st.session_state.ticker_list = [
        "PAYTM.NS",
        "RELIANCE.NS",
        "TCS.NS",
        "INFY.NS",
        "HDFCBANK.NS",
        "TMPV.NS",
        "SBIN.NS",
        "ICICIBANK.NS"
    ]

# 2. Sidebar Navigation & Asset Selection
with st.sidebar:
    st.title("⚡ Pro Terminal Config")
    st.markdown("---")
    
    # Select Asset / Ticker Dropdown with Arrow & Dynamic Options
    symbol = st.selectbox(
        "▼ Select Asset / Search Ticker 🔽",
        options=st.session_state.ticker_list,
        index=0,
        help="Aap list se choose kar sakte hain ya custom ticker type kar sakte hain."
    )
    
    # Custom Ticker Add Section
    custom_symbol = st.text_input("➕ Type New Ticker (e.g. WIPRO.NS)", value="", placeholder="Type and press Enter...")
    if custom_symbol:
        formatted_symbol = custom_symbol.strip().upper()
        if formatted_symbol not in st.session_state.ticker_list:
            st.session_state.ticker_list.insert(0, formatted_symbol)
            st.rerun()
        symbol = formatted_symbol

    timeframe = st.selectbox("Timeframe", ["1M", "3M", "6M", "1Y"], index=0)
    
    st.markdown("---")
    st.subheader("🔔 Trade Alert Options")
    
    # Price Level Based Target & Stop Loss Alert Inputs
    enable_alerts = st.toggle("Enable Real-Time Signals", value=True)
    
    col_t, col_sl = st.columns(2)
    with col_t:
        custom_target = st.number_input("Target (₹)", value=0.0, step=1.0)
    with col_sl:
        custom_sl = st.number_input("StopLoss (₹)", value=0.0, step=1.0)
        
    audio_alert = st.checkbox("Enable Audio Notification", value=False)
    
    st.markdown("---")
    st.success("🟢 Terminal Active | Low Latency Feed")

# Fetch Core Stock Data
data = get_stock_data(symbol)

# Sample News & ML Predictions Setup
sample_news = [
    {"title": f"{symbol} reports strong quarterly earnings & revenue momentum.", "tag": "BULLISH", "score": 85},
    {"title": "Institutional volume surge observed in morning trade.", "tag": "BULLISH", "score": 75},
    {"title": "Sector momentum remains steady across indices.", "tag": "NEUTRAL", "score": 50}
]
sentiment = analyze_news_sentiment([item["title"] for item in sample_news])

if data:
    predictions = predict_stock_levels(data["ltp"], sentiment)

    # 3. Dynamic Trade Alert Engine
    current_time = datetime.now().strftime('%d %b %Y, %I:%M:%S %p IST')
    
    ltp = data['ltp']
    hist = data["history"]
    hist['MA20'] = hist['Close'].rolling(window=20).mean()
    ma20_curr = round(hist['MA20'].iloc[-1], 2)
    
    # Price Target Check
    price_alert_msg = ""
    if custom_target > 0 and ltp >= custom_target:
        price_alert_msg = f" 🎯 <b>CUSTOM TARGET HIT!</b> Target Price ₹{custom_target} reached."
    elif custom_sl > 0 and ltp <= custom_sl:
        price_alert_msg = f" 🚨 <b>STOP LOSS HIT!</b> Price dropped below ₹{custom_sl}."

    # Indicator Signal Logic
    if ltp > ma20_curr and predictions['potential_upside'] > 3.0:
        signal_type = "BUY CALL ACTIVE"
        signal_class = "alert-box-buy"
        signal_msg = f"🔥 <b>STRONG BULLISH SIGNAL:</b> LTP (₹{ltp}) traded above 20 MA (₹{ma20_curr}) with high sentiment (+{predictions['potential_upside']}% Target).{price_alert_msg}"
    elif ltp < ma20_curr and predictions['potential_upside'] < 0:
        signal_type = "SELL / SHORT CALL ACTIVE"
        signal_class = "alert-box-sell"
        signal_msg = f"⚠️ <b>BEARISH SIGNAL:</b> LTP (₹{ltp}) broken below 20 MA (₹{ma20_curr}). Strict Stop-Loss recommended.{price_alert_msg}"
    else:
        signal_type = "NEUTRAL / HOLD"
        signal_class = "alert-box-buy"
        signal_msg = f"ℹ️ <b>CONSOLIDATION:</b> Stock trading near average levels.{price_alert_msg}"

    # Top Header & Trade Alert Display
    st.caption(f"📡 Real-Time Data Sync | Last Refreshed: {current_time}")
    
    if enable_alerts:
        st.markdown(f"""
        <div class='{signal_class}'>
            {signal_msg}
        </div>
        """, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # SECTION 1: MARKET INDICES
    # -------------------------------------------------------------
    st.markdown("##### 📊 Market Indices Summary")
    indices = get_indices_data()
    i1, i2, i3, i4, i5 = st.columns(5)
    indices_list = [("NIFTY 50", i1), ("SENSEX", i2), ("BANK NIFTY", i3), ("AUTO INDEX", i4), ("MIDCAP 100", i5)]

    for name, col in indices_list:
        item = indices.get(name, {"price": "24,500.00", "change": 120.50, "pct": 0.50})
        with col:
            with st.container(border=True):
                st.metric(
                    label=name, 
                    value=f"₹{item['price']}", 
                    delta=f"{item['change']:+} ({item['pct']:+}%)"
                )

    st.markdown("---")

    # -------------------------------------------------------------
    # SECTION 2: STOCK METRICS WITH PERCENTAGE & SYMBOLS
    # -------------------------------------------------------------
    st.markdown(f"##### 📈 Asset Metrics: {symbol}")
    
    day_high_pct = round(((data['day_high'] - ltp) / ltp) * 100, 2)
    day_low_pct = round(((ltp - data['day_low']) / data['day_low']) * 100, 2)
    w52_high_pct = round(((data['week_52_high'] - ltp) / ltp) * 100, 2)
    w52_low_pct = round(((ltp - data['week_52_low']) / data['week_52_low']) * 100, 2)

    m1, m2, m3, m4, m5, m6 = st.columns(6)
    
    with m1:
        with st.container(border=True):
            st.metric(label="LTP", value=f"₹{ltp}")
    with m2:
        with st.container(border=True):
            chg_symbol = "▲" if data['change'] >= 0 else "▼"
            st.metric(label="Change", value=f"₹{data['change']}", delta=f"{chg_symbol} {data['percent_change']}%")
    with m3:
        with st.container(border=True):
            st.metric(label="Day High", value=f"₹{data['day_high']}", delta=f"▲ +{day_high_pct}%")
    with m4:
        with st.container(border=True):
            st.metric(label="Day Low", value=f"₹{data['day_low']}", delta=f"▼ -{day_low_pct}%", delta_color="inverse")
    with m5:
        with st.container(border=True):
            st.metric(label="52W High", value=f"₹{data['week_52_high']}", delta=f"▲ +{w52_high_pct}%")
    with m6:
        with st.container(border=True):
            st.metric(label="52W Low", value=f"₹{data['week_52_low']}", delta=f"▼ -{w52_low_pct}%", delta_color="inverse")

    st.markdown("<br>", unsafe_allow_html=True)

    # -------------------------------------------------------------
    # SECTION 3: HALF-HALF (ML+NLP Prediction | Top Gainers & Losers)
    # -------------------------------------------------------------
    left_half, right_half = st.columns(2)

    # LEFT HALF: Combined ML + NLP Prediction Card
    with left_half:
        with st.container(border=True):
            st.subheader("🧠 ML + NLP Predictive Trade Setup")
            
            c1, c2 = st.columns(2)
            with c1:
                st.caption("Potential Upside")
                st.markdown(f"<h2 style='color: #0066cc; margin:0; font-size:28px;'>▲ +{predictions['potential_upside']}%</h2>", unsafe_allow_html=True)
            with c2:
                st.caption("Current LTP")
                st.markdown(f"<h3 style='margin:0; font-size:24px;'>₹{data['ltp']}</h3>", unsafe_allow_html=True)
            
            st.progress(predictions['sentiment_score'] / 100)
            
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

            st.button(f"⚡ Execute Signal ({signal_type.split()[0]})", type="primary", use_container_width=True)

    # RIGHT HALF: Top Gainers & Top Losers
    with right_half:
        with st.container(border=True):
            st.subheader("📊 Market Top Gainers & Losers")
            tab_gainers, tab_losers = st.tabs(["🔥 TOP GAINERS", "🔻 TOP LOSERS"])
            
            gainers_data = [
                {"Symbol": "Siemens Ener.Ind", "LTP": "₹3,643.50", "Change": "▲ +402.60 (+12.03%)"},
                {"Symbol": "Samvardh. Mothe.", "LTP": "₹166.11", "Change": "▲ +11.13 (+7.17%)"},
                {"Symbol": "Travel Food", "LTP": "₹1,415.80", "Change": "▲ +76.80 (+5.88%)"},
                {"Symbol": "Welspun Living", "LTP": "₹168.02", "Change": "▲ +9.07 (+5.51%)"}
            ]
            
            losers_data = [
                {"Symbol": "Paytm", "LTP": "₹712.40", "Change": "▼ -32.10 (-4.31%)"},
                {"Symbol": "Vodafone Idea", "LTP": "₹12.80", "Change": "▼ -0.55 (-4.12%)"},
                {"Symbol": "Indus Towers", "LTP": "₹342.10", "Change": "▼ -12.40 (-3.50%)"},
                {"Symbol": "Tata Steel", "LTP": "₹148.20", "Change": "▼ -4.80 (-3.14%)"}
            ]

            with tab_gainers:
                for stock_item in gainers_data:
                    c1, c2 = st.columns([2, 1])
                    with c1:
                        st.markdown(f"**{stock_item['Symbol']}**")
                    with c2:
                        st.markdown(f"<div style='text-align: right; color: #10b981; font-size: 13px;'><b>{stock_item['LTP']}</b><br>{stock_item['Change']}</div>", unsafe_allow_html=True)
                    st.markdown("<hr style='margin:2px 0;'>", unsafe_allow_html=True)

            with tab_losers:
                for stock_item in losers_data:
                    c1, c2 = st.columns([2, 1])
                    with c1:
                        st.markdown(f"**{stock_item['Symbol']}**")
                    with c2:
                        st.markdown(f"<div style='text-align: right; color: #ef4444; font-size: 13px;'><b>{stock_item['LTP']}</b><br>{stock_item['Change']}</div>", unsafe_allow_html=True)
                    st.markdown("<hr style='margin:2px 0;'>", unsafe_allow_html=True)

    st.markdown("---")

    # -------------------------------------------------------------
    # SECTION 4: Price Action Chart & Live NLP News Sentiment Feed
    # -------------------------------------------------------------
    chart_col, news_col = st.columns([2, 1])

    # LEFT: Technical Price Action Chart
    with chart_col:
        with st.container(border=True):
            st.subheader("📈 Institutional Technical Chart")
            
            fig = go.Figure()
            fig.add_trace(go.Candlestick(
                x=hist.index,
                open=hist['Open'],
                high=hist['High'],
                low=hist['Low'],
                close=hist['Close'],
                name="OHLC"
            ))
            fig.add_trace(go.Scatter(
                x=hist.index, y=hist['MA20'], 
                mode='lines', name='20 MA Signal',
                line=dict(color='#0066cc', width=1.5)
            ))
            fig.update_layout(
                height=380,
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis_rangeslider_visible=False,
                template="plotly_dark"
            )
            st.plotly_chart(fig, use_container_width=True)

    # RIGHT: Live NLP News & Social Sentiment Feed
    with news_col:
        with st.container(border=True):
            st.subheader("📰 NLP News Sentiment Feed")
            st.write(f"**Overall Sentiment Score:** {predictions['sentiment_score']}% Bullish")
            st.progress(predictions['sentiment_score'] / 100)
            
            for item in sample_news:
                st.markdown(f"**{item['title']}**")
                st.caption(f"Sentiment Impact: {item['tag']} ({item['score']}%)")
                st.markdown("<hr style='margin:2px 0;'>", unsafe_allow_html=True)

else:
    st.error("Invalid Stock Ticker or Data Unavailable.")