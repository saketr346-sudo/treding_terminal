def predict_stock_levels(ltp, sentiment_score):
    """
    Stock price, LTP, aur dynamic sentiment score ke adhar par 
    dynamic target, stop loss, aur potential upside calculate karta hai.
    """
    try:
        base_upside = (sentiment_score - 50) * 0.15 + 2.0
        potential_upside_pct = round(max(0.5, min(12.5, base_upside)), 2)
        target_price = round(ltp * (1 + (potential_upside_pct / 100)), 2)
        stop_loss_pct = round(potential_upside_pct / 2, 2)
        stop_loss = round(ltp * (1 - (stop_loss_pct / 100)), 2)
        entry_price = round(ltp, 2)

        return {
            "potential_upside": potential_upside_pct,
            "target_price": target_price,
            "stop_loss": stop_loss,
            "entry_price": entry_price
        }

    except Exception:
        return {
            "potential_upside": 2.5,
            "target_price": round(ltp * 1.025, 2),
            "stop_loss": round(ltp * 0.985, 2),
            "entry_price": ltp
        }
