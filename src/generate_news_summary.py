# generate_news_summary.py

import google.generativeai as genai
import pandas as pd
import time
from datetime import datetime
from tqdm import tqdm

# ✅ config.py에서 API 키 및 파일명 가져오기
from src.config import API_KEY, NEWS_CSV_FILENAME

# 프롬프트 템플릿 함수
def build_prompt(year, month_name, country="Japan", currency1="KRW", currency2="JPY"):
    return f"""
Suppose you are living in {year}, can you summarize the key news events in {year}'s {month_name}
related to {country} and its impact on the exchange rate between {currency1} and {currency2}?
Please directly give me the answer limited to 2 sentences without apology.
""".strip()

# 뉴스 요약 생성 함수
def generate_news_summary(
    api_key,
    start_date="2020-07-01",
    end_date="2025-07-01",
    country="Japan",
    currency1="KRW",
    currency2="JPY",
    output_csv_path=NEWS_CSV_FILENAME
):
    # Gemini API 설정
    genai.configure(api_key=api_key)

    # 안전성 필터 완화
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "LOW"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "LOW"},
    ]

    # 모델 초기화
    model = genai.GenerativeModel("gemini-2.5-pro")

    # 날짜 범위 생성
    date_range = pd.date_range(start=start_date, end=end_date, freq='MS')
    results = []

    print(f"🔄 뉴스 요약 생성 중... ({len(date_range)}개월)")
    for dt in tqdm(date_range):
        year = dt.year
        month_name = dt.strftime("%B")
        prompt = build_prompt(year, month_name, country, currency1, currency2)

        try:
            response = model.generate_content(prompt, safety_settings=safety_settings)
            summary = response.text.strip()
        except Exception as e:
            summary = f"ERROR: {e}"

        print(f"{year}.{dt.month} - {summary}")

        results.append({
            "year": year,
            "month": month_name,
            "date": dt.strftime("%Y-%m-%d"),
            "prompt": prompt,
            "summary": summary
        })

        time.sleep(1.5)  # 요청 간 딜레이 (429 방지)

    news_df = pd.DataFrame(results)
    news_df.to_csv(output_csv_path, index=False)
    print(f"✅ 월별 뉴스 요약 저장 완료 → {output_csv_path}")


# 실행용 메인 함수
if __name__ == "__main__":
    generate_news_summary(
        api_key=API_KEY,
        output_csv_path=NEWS_CSV_FILENAME
    )
