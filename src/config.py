# config.py

import os
API_KEY = os.getenv("GEMINI_API_KEY", "")

# 공통 파일명
NEWS_CSV_FILENAME = "data/monthly_news.csv"
IMPACT_SCORE_CSV_FILENAME = "data/news_with_impact_score.csv"
EXCHANGE_RATE_CSV = "data/주요국 통화의 대원화환율_30133713.csv"
