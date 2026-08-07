import yfinance as yf

def get_indices_data():
    indices_tickers = {
        "NIFTY 50": "^NSEI",
        "SENSEX": "^BSESN",
        "BANK NIFTY": "^NSEBANK",
        "AUTO INDEX": "^CNXAUTO",
        "MIDCAP 100": "^NSEMDCP100"
    }
    indices_result = {}
    for name, ticker in indices_tickers.items():
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="2d")
            if len(hist) >= 2:
                curr = hist['Close'].iloc[-1]
                prev = hist['Close'].iloc[-2]
                chg = curr - prev
                pct = (chg / prev) * 100
                indices_result[name] = {
                    "price": round(curr, 2),
                    "change": round(chg, 2),
                    "pct": round(pct, 2)
                }
            else:
                indices_result[name] = {"price": "--", "change": 0.0, "pct": 0.0}
        except Exception:
            indices_result[name] = {"price": "--", "change": 0.0, "pct": 0.0}
            
    return indices_result

def get_stock_data(ticker_symbol="PAYTM.NS"):
    try:
        stock = yf.Ticker(ticker_symbol)
        hist = stock.history(period="1y", interval="1d")
        
        if hist.empty:
            return None
        
        current_price = round(hist['Close'].iloc[-1], 2)
        previous_close = round(hist['Close'].iloc[-2], 2)
        change = round(current_price - previous_close, 2)
        percent_change = round((change / previous_close) * 100, 2)
        
        day_high = round(hist['High'].iloc[-1], 2)
        day_low = round(hist['Low'].iloc[-1], 2)
        
        week_52_high = round(hist['High'].max(), 2)
        week_52_low = round(hist['Low'].min(), 2)
        
        return {
            "ticker": ticker_symbol,
            "ltp": current_price,
            "change": change,
            "percent_change": percent_change,
            "day_high": day_high,
            "day_low": day_low,
            "week_52_high": week_52_high,
            "week_52_low": week_52_low,
            "history": hist.tail(30)
        }
    except Exception:
        return None