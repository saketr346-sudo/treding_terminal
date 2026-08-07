def predict_stock_levels(ltp, sentiment_data):
    # Sentiment score from NLP (0 to 100 scale)
    sentiment_score = sentiment_data.get("score", 50) if isinstance(sentiment_data, dict) else 50
    
    # Combined Multiplier (50% Base ML + 50% NLP Weight)
    sentiment_factor = (sentiment_score - 50) / 100.0
    combined_growth_pct = round(3.5 + (sentiment_factor * 5.0), 2)
    
    target_price = round(ltp * (1 + combined_growth_pct / 100.0), 2)
    entry_price = round(ltp * 0.995, 2)
    stop_loss = round(ltp * 0.96, 2)
    
    return {
        "potential_upside": combined_growth_pct,
        "entry_price": entry_price,
        "target_price": target_price,
        "stop_loss": stop_loss,
        "sentiment_score": sentiment_score
    }