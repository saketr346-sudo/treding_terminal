from datetime import datetime
import time
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from data_fetcher import (
    get_indices_data,
    get_nifty50_gainers_losers,
    get_stock_data,
)
from ml_model import predict_stock_levels

# 1. Page Config & CSS Updates
st.set_page_config(page_title="Terminal Dashbord", layout="wide", page_icon="⚡")

st.markdown(
    """
<style>
    div[data-testid="stMetricValue"] { font-size: 22px !important; font-weight: 700 !important; }
    div[data-testid="stMetricLabel"] { font-size: 14px !important; font-weight: 600 !important; color: #8b949e !important; }
    div[data-testid="stMetricDelta"] { font-size: 14px !important; }
    .block-container { padding-top: 2.5rem !important; padding-bottom: 1rem !important; }
    
    button[data-baseweb="tab"] {
        font-size: 18px !important;
        font-weight: 700 !important;
        padding: 10px 20px !important;
    }
    button[data-baseweb="tab"] p {
        font-size: 18px !important;
        font-weight: 700 !important;
    }

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
""",
    unsafe_allow_html=True,
)

# Session States Initializations
if "ticker_list" not in st.session_state:
  st.session_state.ticker_list = [
      "PAYTM.NS",
      "RELIANCE.NS",
      "TCS.NS",
      "INFY.NS",
      "HDFCBANK.NS",
      "TMPV.NS",
      "SBIN.NS",
      "ICICIBANK.NS",
  ]

if "watchlist" not in st.session_state:
  st.session_state.watchlist = ["RELIANCE.NS", "TCS.NS", "INFY.NS"]

if "selected_symbol" not in st.session_state:
  st.session_state.selected_symbol = "PAYTM.NS"

if "selected_timeframe" not in st.session_state:
  st.session_state.selected_timeframe = "1M"

if "virtual_balance" not in st.session_state:
  st.session_state.virtual_balance = 100000.0

if "portfolio" not in st.session_state:
  st.session_state.portfolio = []

# Live Header with Fixed Top Margin & JavaScript Live Clock
st.markdown("## ⚡ Terminal Dashboard")
st.components.v1.html(
    f"""
    <div style="font-family: sans-serif; font-size: 16px; font-weight: bold; color: #333;">
        <span style="color:#10b981;">LIVE STREAM</span> | 
         <span>{datetime.now().strftime('%d %b %Y')}</span> | 
         <span id="live-clock">--:--:-- --</span>
    </div>
    <script>
        function updateClock() {{
            const now = new Date();
            let hours = now.getHours();
            let minutes = now.getMinutes();
            let seconds = now.getSeconds();
            let ampm = hours >= 12 ? 'PM' : 'AM';
            hours = hours % 12;
            hours = hours ? hours : 12;
            minutes = minutes < 10 ? '0' + minutes : minutes;
            seconds = seconds < 10 ? '0' + seconds : seconds;
            let strTime = hours + ':' + minutes + ':' + seconds + ' ' + ampm + ' IST';
            document.getElementById('live-clock').innerHTML = strTime;
        }}
        setInterval(updateClock, 1000);
        updateClock();
    </script>
""",
    height=35,
)

# Auto Target / StopLoss Trigger Engine
if st.session_state.portfolio:
  updated_portfolio = []
  for pos in st.session_state.portfolio:
    stock_info = get_stock_data(pos["symbol"])
    if stock_info:
      curr_ltp = stock_info["ltp"]

      if pos["target"] > 0 and curr_ltp >= pos["target"]:
        returns = pos["capital_used"] + (
            (curr_ltp - pos["buy_price"]) * pos["quantity"]
        )
        st.session_state.virtual_balance += returns
        st.toast(
            f"🎯 TARGET HIT! Auto-Sold {pos['quantity']} shares of"
            f" {pos['symbol']} at ₹{curr_ltp}",
            icon="🎉",
        )

      elif pos["stop_loss"] > 0 and curr_ltp <= pos["stop_loss"]:
        returns = pos["capital_used"] + (
            (curr_ltp - pos["buy_price"]) * pos["quantity"]
        )
        st.session_state.virtual_balance += max(0, returns)
        st.toast(
            f"🛑 STOPLOSS HIT! Auto-Sold {pos['quantity']} shares of"
            f" {pos['symbol']} at ₹{curr_ltp}",
            icon="⚠️",
        )

      else:
        updated_portfolio.append(pos)
    else:
      updated_portfolio.append(pos)

  st.session_state.portfolio = updated_portfolio

# Top Navigation Controls
with st.container(border=True):
  opt1, opt2, opt3, opt4 = st.tabs([
      "🔍Search & Timeframe",
      "🔄Live Refresh",
      "⭐Watchlist",
      "🏧Virtual Money Trading",
  ])

  with opt1:
    with st.form(key="top_search_form"):
      c1, c2, c3, c4 = st.columns([2, 2, 1.5, 1.5])
      with c1:
        current_idx = (
            st.session_state.ticker_list.index(st.session_state.selected_symbol)
            if st.session_state.selected_symbol in st.session_state.ticker_list
            else 0
        )
        dropdown_stock = st.selectbox(
            "Select Stock",
            options=st.session_state.ticker_list,
            index=current_idx,
        )
      with c2:
        custom_stock = st.text_input(
            "Or Type Ticker", value="", placeholder="e.g. SUZLON"
        )
      with c3:
        selected_tf = st.selectbox(
            "Timeframe",
            ["1M", "3M", "6M", "1Y", "3Y", "5Y", "10Y"],
            index=0,
        )
      with c4:
        st.write("")
        btn_search = st.form_submit_button(
            label="🔍 Search Stock", use_container_width=True
        )

    if btn_search:
      if custom_stock.strip():
        raw_symbol = custom_stock.strip().upper()
        formatted_symbol = (
            f"{raw_symbol}.NS"
            if not (raw_symbol.endswith(".NS") or raw_symbol.endswith(".BO"))
            else raw_symbol
        )
        if formatted_symbol not in st.session_state.ticker_list:
          st.session_state.ticker_list.insert(0, formatted_symbol)
        st.session_state.selected_symbol = formatted_symbol
      else:
        st.session_state.selected_symbol = dropdown_stock

      st.session_state.selected_timeframe = selected_tf
      st.rerun()

  with opt2:
    r_c1, r_c2 = st.columns(2)
    with r_c1:
      auto_refresh = st.toggle("Enable Live Auto-Refresh", value=True)
    with r_c2:
      refresh_interval = st.number_input(
          "Refresh Interval (Seconds)", min_value=1, value=5, step=1
      )

  with opt3:
    w_c1, w_c2 = st.columns([2.5, 1.5])
    with w_c1:
      st.caption("Quick Select from Watchlist:")
      wl_cols = st.columns(4)
      for idx, w_stock in enumerate(st.session_state.watchlist):
        if wl_cols[idx % 4].button(
            f"📈 {w_stock}", key=f"top_wl_{w_stock}", use_container_width=True
        ):
          st.session_state.selected_symbol = w_stock
          st.rerun()
    with w_c2:
      add_wl = st.text_input(
          "Add Stock to Watchlist", placeholder="e.g. ZOMATO", key="add_wl_top"
      )
      if st.button("➕ Add", use_container_width=True):
        if add_wl.strip():
          formatted_wl = add_wl.strip().upper()
          if not (formatted_wl.endswith(".NS") or formatted_wl.endswith(".BO")):
            formatted_wl = f"{formatted_wl}.NS"
          if formatted_wl not in st.session_state.watchlist:
            st.session_state.watchlist.append(formatted_wl)
            st.success("Added!")
            st.rerun()

  with opt4:
    st.markdown(
        f"💰 Available Cash Balance:"
        f" **₹{st.session_state.virtual_balance:,.2f}**"
    )
    v_left, v_right = st.columns([1, 1])

    with v_left:
      st.markdown("##### 📥 Order Execution Panel")
      v_stock = st.selectbox(
          "Stock to Trade",
          options=st.session_state.ticker_list,
          index=(
              st.session_state.ticker_list.index(
                  st.session_state.selected_symbol
              )
              if st.session_state.selected_symbol in st.session_state.ticker_list
              else 0
          ),
      )

      c_q, c_m = st.columns(2)
      with c_q:
        v_qty = st.number_input("Quantity", min_value=1, value=10, step=1)
      with c_m:
        v_margin = st.selectbox(
            "Margin",
            ["1x (Delivery)", "2x (Intraday)", "5x (Super Margin)"],
            index=0,
        )

      c_sl, c_tg = st.columns(2)
      with c_sl:
        v_sl = st.number_input("Stop Loss Price (₹)", value=0.0, step=1.0)
      with c_tg:
        v_target = st.number_input("Target Price (₹)", value=0.0, step=1.0)

      temp_data = get_stock_data(v_stock)
      v_ltp = temp_data["ltp"] if temp_data else 100.0
      leverage = 1 if "1x" in v_margin else (2 if "2x" in v_margin else 5)
      req_amount = round((v_ltp * v_qty) / leverage, 2)

      st.caption(
          f"Required Margin: **₹{req_amount:,.2f}** | Current LTP:"
          f" **₹{v_ltp}**"
      )

      btn_buy_col, btn_sell_col = st.columns(2)
      with btn_buy_col:
        if st.button(f"🟢 BUY {v_stock}", use_container_width=True):
          if st.session_state.virtual_balance >= req_amount:
            st.session_state.virtual_balance -= req_amount
            st.session_state.portfolio.append({
                "symbol": v_stock,
                "buy_price": v_ltp,
                "quantity": v_qty,
                "target": v_target,
                "stop_loss": v_sl,
                "margin": v_margin,
                "capital_used": req_amount,
            })
            st.success(f"Bought {v_qty} shares of {v_stock}!")
            st.rerun()
          else:
            st.error("Insufficient Cash Balance!")

      with btn_sell_col:
        if st.button(f"🔴 SELL {v_stock}", use_container_width=True):
          holdings = [
              p for p in st.session_state.portfolio if p["symbol"] == v_stock
          ]
          if holdings:
            recovered_cash = sum([
                p["capital_used"] + ((v_ltp - p["buy_price"]) * p["quantity"])
                for p in holdings
            ])
            st.session_state.virtual_balance += recovered_cash
            st.session_state.portfolio = [
                p for p in st.session_state.portfolio if p["symbol"] != v_stock
            ]
            st.success(f"Closed positions for {v_stock}!")
            st.rerun()
          else:
            st.warning("No positions to sell!")

    with v_right:
      st.markdown("##### 💼 Live Portfolio Details")
      if st.session_state.portfolio:
        tot_invested = sum(
            [p["capital_used"] for p in st.session_state.portfolio]
        )
        st.caption(f"Total Margin Employed: **₹{tot_invested:,.2f}**")

        for idx, pos in enumerate(st.session_state.portfolio):
          curr_data = get_stock_data(pos["symbol"])
          curr_p = curr_data["ltp"] if curr_data else pos["buy_price"]
          pnl = (curr_p - pos["buy_price"]) * pos["quantity"]
          pnl_color = "#10b981" if pnl >= 0 else "#ef4444"

          with st.container(border=True):
            col_p1, col_p2 = st.columns([2, 1])
            with col_p1:
              st.markdown(
                  f"**{pos['symbol']}** | Qty: {pos['quantity']} |"
                  f" {pos['margin']}"
              )
              st.caption(
                  f"Buy: ₹{pos['buy_price']} | SL: ₹{pos['stop_loss']} | Target:"
                  f" ₹{pos['target']}"
              )
            with col_p2:
              st.markdown(
                  f"<div style='text-align:right;'>LTP: <b>₹{curr_p}</b><br><span"
                  f" style='color:{pnl_color};"
                  f" font-weight:bold;'>₹{pnl:,.2f}</span></div>",
                  unsafe_allow_html=True,
              )
      else:
        st.info("No active holdings in your Virtual Portfolio.")

# Selected Stock Processing
symbol = st.session_state.selected_symbol
timeframe = st.session_state.selected_timeframe

data = get_stock_data(symbol)

if data:
  ltp = float(data["ltp"])
  hist = data["history"]

  if len(hist) >= 2:
    prev_close = float(hist["Close"].iloc[-2])
  else:
    prev_close = float(hist["Close"].iloc[-1]) if len(hist) > 0 else ltp

  change_val = round(ltp - prev_close, 2)
  pct_val = (
      round(((ltp - prev_close) / prev_close) * 100, 2)
      if prev_close != 0
      else 0.0
  )

  hist["MA20"] = hist["Close"].rolling(window=20).mean()
  ma20_curr = round(hist["MA20"].iloc[-1], 2)

  delta = hist["Close"].diff()
  gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
  loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
  rs = gain / loss
  hist["RSI"] = 100 - (100 / (1 + rs))
  rsi_curr = round(hist["RSI"].iloc[-1], 2) if not hist["RSI"].empty else 50.0

  exp1 = hist["Close"].ewm(span=12, adjust=False).mean()
  exp2 = hist["Close"].ewm(span=26, adjust=False).mean()
  hist["MACD"] = exp1 - exp2
  hist["Signal_Line"] = hist["MACD"].ewm(span=9, adjust=False).mean()
  macd_curr = hist["MACD"].iloc[-1]
  macd_signal_curr = hist["Signal_Line"].iloc[-1]

  hist["STD20"] = hist["Close"].rolling(window=20).std()
  hist["Upper_Band"] = hist["MA20"] + (hist["STD20"] * 2)
  hist["Lower_Band"] = hist["MA20"] - (hist["STD20"] * 2)

  dynamic_sentiment_base = 50 + (pct_val * 5) + ((rsi_curr - 50) * 0.5)
  dynamic_sentiment_score = max(10, min(95, round(dynamic_sentiment_base, 1)))

  sample_news = [
      {
          "title": f"{symbol} price momentum tracking at {pct_val:+.2f}%.",
          "tag": "BULLISH" if pct_val >= 0 else "BEARISH",
          "score": dynamic_sentiment_score,
      },
      {
          "title": (
              f"Technical Indicators: RSI at {rsi_curr} & 20 MA at"
              f" ₹{ma20_curr}."
          ),
          "tag": "NEUTRAL",
          "score": 55,
      },
  ]

  predictions = predict_stock_levels(ltp, dynamic_sentiment_score)

  is_ma_bull = ltp > ma20_curr
  is_rsi_bull = rsi_curr > 60
  is_macd_bull = macd_curr > macd_signal_curr
  is_nlp_bull = dynamic_sentiment_score > 60

  active_factors = sum([is_ma_bull, is_rsi_bull, is_macd_bull, is_nlp_bull])
  model_accuracy = round((active_factors / 4) * 100, 1)

  if is_ma_bull and is_rsi_bull and is_macd_bull:
    signal_type = "BUY"
    btn_class = "btn-buy"
  elif ltp < ma20_curr or macd_curr < macd_signal_curr:
    signal_type = "SELL"
    btn_class = "btn-sell"
  else:
    signal_type = "HOLD / NEUTRAL"
    btn_class = "btn-sell"

  # Market Indices Section
  st.markdown("##### Market Overview")
  indices = get_indices_data()
  i1, i2, i3, i4, i5 = st.columns(5)
  for name, col in [
      ("NIFTY 50", i1),
      ("SENSEX", i2),
      ("BANK NIFTY", i3),
      ("NIFTY IT", i4),
      ("GOLD", i5),
  ]:
    item = indices.get(
        name, {"price": "24,500.00", "change": 120.50, "pct": 0.50}
    )
    with col:
      with st.container(border=True):
        st.metric(
            label=name,
            value=f"₹{item['price']}",
            delta=f"{item['change']:+} ({item['pct']:+}%)",
        )

  st.markdown("---")

  # Stock Metrics Section
  st.markdown(f"##### 📈 Stock: {symbol}")
  m1, m2, m3, m4, m5, m6 = st.columns(6)

  with m1:
    with st.container(border=True):
      st.metric(label="LTP", value=f"₹{ltp}")
  with m2:
    with st.container(border=True):
      st.metric(
          label="Change", value=f"₹{change_val:+}", delta=f"{pct_val:+.2f}%"
      )
  with m3:
    with st.container(border=True):
      st.metric(label="Day High", value=f"₹{data['day_high']}")
  with m4:
    with st.container(border=True):
      st.metric(label="Day Low", value=f"₹{data['day_low']}")
  with m5:
    with st.container(border=True):
      st.metric(label="52W High", value=f"₹{data['week_52_high']}")
  with m6:
    with st.container(border=True):
      st.metric(label="52W Low", value=f"₹{data['week_52_low']}")

  st.markdown("<br>", unsafe_allow_html=True)

  # Trade Setup Engine
  left_half, right_half = st.columns(2)

  with left_half:
    with st.container(border=True):
      st.subheader("Trade Setup")

      st.markdown(
          f"""
            <div style="background-color: rgba(0, 102, 204, 0.15); border: 1px solid #0066cc; padding: 6px 12px; border-radius: 6px; font-size: 13px; font-weight: bold; margin-bottom: 12px;">
                🎯 Confluence Accuracy: <span style="color:#10b981;">{model_accuracy}%</span> | RSI: {rsi_curr} | MACD: {'Bullish' if is_macd_bull else 'Bearish'}
            </div>
            """,
          unsafe_allow_html=True,
      )

      c1, c2 = st.columns(2)
      with c1:
        st.caption("Potential Upside")
        st.markdown(
            "<h2 style='color: #0066cc; margin:0;"
            f" font-size:28px;'>▲ +{predictions['potential_upside']}%</h2>",
            unsafe_allow_html=True,
        )
      with c2:
        st.caption("Current LTP")
        st.markdown(
            f"<h3 style='margin:0; font-size:24px;'>₹{data['ltp']}</h3>",
            unsafe_allow_html=True,
        )

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

      st.markdown(
          f"""
                <button class='{btn_class}' onclick="window.location.reload();">
                    ⚡ Execute Signal ({signal_type})
                </button>
            """,
          unsafe_allow_html=True,
      )

  with right_half:
    with st.container(border=True):
      st.subheader("📊 Market Top Gainers & Losers")
      tab_gainers, tab_losers = st.tabs(["🔥 TOP GAINERS", "🔻 TOP LOSERS"])
      gainers_data, losers_data = get_nifty50_gainers_losers()

      with tab_gainers:
        for stock_item in gainers_data:
          c1, c2 = st.columns([2, 1])
          with c1:
            st.markdown(f"**{stock_item['Symbol']}**")
          with c2:
            st.markdown(
                "<div style='text-align: right; color: #10b981; font-size:"
                f" 13px;'><b>{stock_item['LTP']}</b><br>{stock_item['Change']}</div>",
                unsafe_allow_html=True,
            )
          st.markdown(
              "<hr style='margin:2px 0;'>", unsafe_allow_html=True
          )

      with tab_losers:
        for stock_item in losers_data:
          c1, c2 = st.columns([2, 1])
          with c1:
            st.markdown(f"**{stock_item['Symbol']}**")
          with c2:
            st.markdown(
                "<div style='text-align: right; color: #ef4444; font-size:"
                f" 13px;'><b>{stock_item['LTP']}</b><br>{stock_item['Change']}</div>",
                unsafe_allow_html=True,
            )
          st.markdown(
              "<hr style='margin:2px 0;'>", unsafe_allow_html=True
          )

  st.markdown("---")

  # Technical Chart & News Feed
  chart_col, news_col = st.columns([2, 1])

  with chart_col:
    with st.container(border=True):
      st.subheader("Technical Chart")

      fig = make_subplots(
          rows=2,
          cols=1,
          shared_xaxes=True,
          vertical_spacing=0.02,
          row_heights=[0.80, 0.20],
      )

      fig.add_trace(
          go.Candlestick(
              x=hist.index,
              open=hist["Open"],
              high=hist["High"],
              low=hist["Low"],
              close=hist["Close"],
              name="OHLC",
              increasing_line_color="#00D09C",
              increasing_fillcolor="#00D09C",
              decreasing_line_color="#FF5353",
              decreasing_fillcolor="#FF5353",
          ),
          row=1,
          col=1,
      )

      fig.add_trace(
          go.Scatter(
              x=hist.index,
              y=hist["MA20"],
              mode="lines",
              name="20 MA",
              line=dict(color="#00B8D9", width=1.8),
          ),
          row=1,
          col=1,
      )
      fig.add_trace(
          go.Scatter(
              x=hist.index,
              y=hist["Upper_Band"],
              mode="lines",
              name="Upper Band",
              line=dict(color="rgba(0, 208, 156, 0.3)", width=1, dash="dash"),
          ),
          row=1,
          col=1,
      )
      fig.add_trace(
          go.Scatter(
              x=hist.index,
              y=hist["Lower_Band"],
              mode="lines",
              name="Lower Band",
              line=dict(color="rgba(255, 83, 83, 0.3)", width=1, dash="dash"),
              fill="tonexty",
              fillcolor="rgba(255, 255, 255, 0.015)",
          ),
          row=1,
          col=1,
      )

      volume_colors = [
          "#00D09C" if c >= o else "#FF5353"
          for c, o in zip(hist["Close"], hist["Open"])
      ]
      fig.add_trace(
          go.Bar(
              x=hist.index,
              y=hist["Volume"],
              name="Volume",
              marker_color=volume_colors,
              opacity=0.6,
          ),
          row=2,
          col=1,
      )

      fig.update_layout(
          height=480,
          margin=dict(l=10, r=10, t=25, b=10),
          xaxis_rangeslider_visible=False,
          paper_bgcolor="#121418",
          plot_bgcolor="#121418",
          font=dict(color="#8C96A3"),
          hovermode="x unified",
      )
      st.plotly_chart(fig, use_container_width=True)

  with news_col:
    with st.container(border=True):
      st.subheader("📰 News Sentiment Feed")
      st.write(
          f"**Overall Sentiment Score:** {dynamic_sentiment_score}% Bullish"
      )
      st.progress(dynamic_sentiment_score / 100)
      for item in sample_news:
        st.markdown(f"**{item['title']}**")
        st.caption(f"Sentiment Impact: {item['tag']} ({item['score']}%)")
        st.markdown(
            "<hr style='margin:2px 0;'>", unsafe_allow_html=True
        )

else:
  st.error("Invalid Stock Ticker or Data Unavailable.")

if "auto_refresh" in locals() and auto_refresh:
  time.sleep(refresh_interval)
  st.rerun()
