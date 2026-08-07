import numpy as np

def predict_stock_levels(ltp, sentiment_score):
    """
    Stock price, LTP, aur dynamic sentiment score ke adhar par 
    dynamic target, stop loss, aur potential upside calculate karta hai.
    """
    try:
        # 1. Dynamic Potential Upside Calculation (Sentiment + Volatility Factor)
        # Low sentiment -> lower potential upside (ya negative downside)
        # High sentiment -> higher potential upside
        base_upside = (sentiment_score - 50) * 0.15 + 2.0  # Dynamic percentage formula
        
        # Min +0.5% aur Max +12.5% tak bound karein
        potential_upside_pct = round(max(0.5, min(12.5, base_upside)), 2)

        # 2. Dynamic Target Price Based on Upside %
        target_price = round(ltp * (1 + (potential_upside_pct / 100)), 2)

        # 3. Dynamic Stop Loss Calculation (1:2 Risk-Reward Ratio)
        stop_loss_pct = round(potential_upside_pct / 2, 2)
        stop_loss = round(ltp * (1 - (stop_loss_pct / 100)), 2)

        # 4. Entry Price (Current LTP with minor spread)
        entry_price = round(ltp, 2)

        return {
            "potential_upside": potential_upside_pct,
            "target_price": target_price,
            "stop_loss": stop_loss,
            "entry_price": entry_price
        }

    except Exception as e:
        # Fallback values
        return {
            "potential_upside": 2.5,
            "target_price": round(ltp * 1.025, 2),
            "stop_loss": round(ltp * 0.985, 2),
            "entry_price": ltp
        }
