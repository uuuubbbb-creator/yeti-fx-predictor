# run_pipeline.py

import sys
import os

# TEMPO 내부 모듈 경로 등록
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "TEMPO")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "TEMPO", "tempo")))

from src.generate_news_summary import generate_news_summary
from src.generate_impact_score import generate_impact_scores
from src.prepare_input_tensor import prepare_input_tensor
from src.recommend_exchange_dates import recommend_exchange_dates
from rule_based_classifier.classifier import classify_customer_sensitivity_interactive_with_tiered_reason_score

from tempo.models.TEMPO import TEMPO
import torch
from src.config import API_KEY

import pandas as pd
import matplotlib.pyplot as plt


def main():
    # 1. Seed 고정
    import random
    import numpy as np
    import torch

    def set_seed(seed: int = 42):
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)

    set_seed(42)

    # 2. 월별 뉴스 요약 생성
    print("📌 Step 1: 뉴스 요약 생성")
    generate_news_summary(api_key=API_KEY)

    # 3. 뉴스 영향력 점수 생성
    print("📌 Step 2: 영향력 점수 생성")
    generate_impact_scores()

    # 4. 시계열 입력 텐서 생성
    print("📌 Step 4: 시계열 입력 텐서 생성")
    input_tensor, scaler_fx, merged_df = prepare_input_tensor()

    # 5. TEMPO 모델 불러오기
    print("📌 Step 5: TEMPO 모델 불러오기")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = TEMPO.load_pretrained_model(
        device=device,
        repo_id="Melady/TEMPO",
        filename="TEMPO-80M_v1.pth",
        cache_dir="./checkpoints/TEMPO_checkpoints"
    )
    model.to(device).eval()

    # 7. 사용자 입력 & 예측 + 추천
    print("📌 Step 6: 여행 날짜 입력 및 환율 추천")
    출국일 = input("출국일을 입력하세요 (예: 2025-08-01): ")
    입국일 = input("입국일을 입력하세요 (예: 2025-08-10): ")

    forecast_df, 추천결과 = recommend_exchange_dates(input_tensor, scaler_fx, model, 출국일, 입국일, top_k=5)
    
    # 7. 시각화
    print("\n📊 환율 예측 결과 시각화 중...")
    plt.figure(figsize=(12, 5))
    plt.plot(forecast_df["date"], forecast_df["predicted_fx"], marker='o', color='blue')
    plt.title("💱 환율 예측 결과")
    plt.xlabel("Date")
    plt.ylabel("Predicted KRW/JPY")
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("forecast_plot.png")
    plt.show()
    plt.close()
    
    # 8. 결과 출력
    print("\n📅 오늘 날짜 기준:", pd.to_datetime("today").strftime("%Y-%m-%d"))
    print("💱 환율이 낮아 환전을 추천하는 날짜:")
    print(추천결과.to_string(index=False))

    # 9. 사용자 민감도 분류 수행
    print("\n🧑 사용자 환율 민감도 분석 시작")
    group = classify_customer_sensitivity_interactive_with_tiered_reason_score()

    if group == '고민감 그룹':
        print("👉 전략 제안: 환율이 낮은 날짜에 분할 환전을 고려하세요.")
    else:
        print("👉 전략 제안: 환율 민감도가 낮으므로 일괄 환전도 무방합니다.")


if __name__ == "__main__":
    main()
