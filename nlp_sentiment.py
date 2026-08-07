from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

def analyze_news_sentiment(headlines):
    if not headlines:
        return 0.0
    
    total_score = 0
    for text in headlines:
        score = analyzer.polarity_scores(text)['compound']
        total_score += score
        
    avg_score = total_score / len(headlines)
    return round(avg_score, 2)