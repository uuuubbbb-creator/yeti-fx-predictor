import pandas as pd
import numpy as np
import torch
from sklearn.preprocessing import MinMaxScaler
from src.config import IMPACT_SCORE_CSV_FILENAME, EXCHANGE_RATE_CSV


def prepare_input_tensor(seq_len=336):
    # 1. 데이터 불러오기 (config에서 경로 참조)
    news_df = pd.read_csv(IMPACT_SCORE_CSV_FILENAME)
    fx_df = pd.read_csv(EXCHANGE_RATE_CSV)

    # 2. 날짜 및 숫자 전처리
    fx_df = fx_df.rename(columns={"변환": "date", "원자료": "exchange_rate"})
    fx_df["date"] = pd.to_datetime(fx_df["date"])
    fx_df["exchange_rate"] = fx_df["exchange_rate"].astype(str).str.replace(",", "").astype(float)

    news_df["date"] = pd.to_datetime(news_df["date"])

    # 3. 월 단위 정렬 및 병합
    fx_df["year_month"] = fx_df["date"].dt.to_period("M")
    news_df["year_month"] = news_df["date"].dt.to_period("M")

    merged_df = pd.merge(
        fx_df,
        news_df[["year_month", "impact_score"]],
        on="year_month",
        how="left"
    ).dropna(subset=["impact_score"])

    # 4. 정규화 및 가중합
    scaler_fx = MinMaxScaler()
    scaler_impact = MinMaxScaler()

    merged_df["scaled_fx"] = scaler_fx.fit_transform(merged_df[["exchange_rate"]])
    merged_df["scaled_impact"] = scaler_impact.fit_transform(merged_df[["impact_score"]])

    merged_df["combined"] = (
        merged_df["scaled_fx"] * 0.9 +
        merged_df["scaled_impact"] * 0.1
    )

    # 5. 텐서 생성 (최근 seq_len일 기준)
    series = merged_df["combined"].values
    if len(series) < seq_len:
        padded = np.pad(series, (seq_len - len(series), 0), 'constant')
    else:
        padded = series[-seq_len:]

    input_tensor = torch.FloatTensor(padded).unsqueeze(0).unsqueeze(2)  # (1, seq_len, 1)

    return input_tensor, scaler_fx, merged_df
