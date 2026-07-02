# recommend_exchange_dates.py

import pandas as pd
import torch
import matplotlib.pyplot as plt
import IPython.display as display


def recommend_exchange_dates(input_tensor, scaler_fx, model, start_date_str, end_date_str, top_k=5):
    """
    사용자가 입력한 여행 기간 동안의 환율을 예측하고,
    그 중 환율이 낮은 날짜를 추천합니다.

    Parameters:
    - input_tensor (torch.Tensor): (1, seq_len, 1) 형태의 모델 입력
    - scaler_fx (MinMaxScaler): 환율 역변환을 위한 스케일러
    - model: TEMPO 모델
    - start_date_str (str): 출국일, 형식 "YYYY-MM-DD"
    - end_date_str (str): 입국일, 형식 "YYYY-MM-DD"
    - top_k (int): 추천할 날짜 수

    Returns:
    - DataFrame: 추천 환율 낮은 날짜 목록
    """

    # 날짜 처리
    start_date = pd.to_datetime(start_date_str)
    end_date = pd.to_datetime(end_date_str)
    today = pd.to_datetime("today").normalize()

    # 유효성 검사
    if start_date < today:
        raise ValueError("출국일은 오늘 이후여야 합니다.")
    if end_date <= start_date:
        raise ValueError("입국일은 출국일보다 이후여야 합니다.")

    # 예측 일 수 계산
    pred_days = (end_date - today).days + 1

    # 모델 예측 수행
    with torch.no_grad():
        output, _ = model(input_tensor, pred_days, test=True)
        predicted_fx = scaler_fx.inverse_transform(output.reshape(-1, 1)).flatten()
        predicted_fx = predicted_fx[:pred_days]

    # 예측 결과 정리
    forecast_dates = pd.date_range(start=today, periods=pred_days)
    forecast_df = pd.DataFrame({
        "date": forecast_dates,
        "predicted_fx": predicted_fx
    })

    # 낮은 환율 추천 날짜
    recommended = forecast_df.sort_values('predicted_fx').head(top_k).sort_values('date')

    return forecast_df, recommended
