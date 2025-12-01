# load_dart.py
import os
import numpy as np
import pandas as pd
from datetime import date, timedelta
from models_DART import SHS, EQU, NI  # ✅ BaseMetric import 필요 없음

# 날짜 생성 유틸
# ----------------------------------------------------------------------------
def generate_dates(start, end, mode="day"):
    start_date = date.fromisoformat(start)
    end_date = date.fromisoformat(end)
    dates = []

    if mode == "day":
        current = start_date
        while current <= end_date:
            dates.append(current)
            current += timedelta(days=1)

    elif mode == "month":
        current = date(start_date.year, start_date.month, 1)
        while current <= end_date:
            dates.append(current)
            if current.month == 12:
                current = date(current.year + 1, 1, 1)
            else:
                current = date(current.year, current.month + 1, 1)

    elif mode == "year":
        current = date(start_date.year, 1, 1)
        while current <= end_date:
            dates.append(current)
            current = date(current.year + 1, 1, 1)
    else:
        raise ValueError("mode는 'day', 'month', 'year' 중 하나여야 합니다.")
    return dates
# -------------------------------------------------------------------------------

# datetime 객체 -> ISO 문자열("YYYY-MM-DD")
def row(metric, d: date):
    d_str = d.isoformat()
    v, _, _, _ = metric.fetch_with_fallback(corp_code, d)
    return (d_str, v)


if __name__ == "__main__":    
    API_KEY = "3957b81997e850b1a08e448a63e193dd0f630a25"
    stk_code, corp_code = "010140", "00126478"  # 삼성중공업 예시
    target_date_str = ["2016-01-01", "2025-12-01"]
    start_date, end_date = target_date_str[0], target_date_str[1]
    dates = generate_dates(start_date, end_date, mode="month")

    shs_metric = SHS(api_key=API_KEY)
    equ_metric = EQU(api_key=API_KEY)
    ni_metric = NI(api_key=API_KEY)
    
    os.makedirs("data", exist_ok=True)
    
    # SHS : 발행주식수 #
    # -----------------------------------------------------------------------------
    rows_sh = [row(shs_metric, d) for d in dates] # datetime -> 문자열
    df_sh = pd.DataFrame(rows_sh, columns=["date", SHS.label])
    df_sh[SHS.label] = df_sh[SHS.label].ffill() # 결측치는 직전 값으로 채우기
    df_sh = df_sh.iloc[::-1] # 날짜 오름차순 정렬
    df_sh.to_excel(f"data/{stk_code}/SHS_month.xlsx", index=False)
    # ---------------------------------------------------------------------------

    # EQUITY : 자기자본 #
    # ---------------------------------------------------------------------------
    rows_equ = [row(equ_metric, d) for d in dates] # datetime -> 문자열
    df_equ = pd.DataFrame(rows_equ, columns=["date", EQU.label])
    df_equ = df_equ.iloc[::-1] # 날짜 오름차순 정렬
    df_equ.to_excel(f"data/{stk_code}/EQU_month.xlsx", index=False)
    # ----------------------------------------------------------------------------

    # NI : 순이익 #
    # -----------------------------------------------------------------------------------------------------------------
    # NI YTD(분기누적순이익) column 생성
    rows_ni = [row(ni_metric, d) for d in dates] # datetime -> 문자열
    df_ni = pd.DataFrame(rows_ni, columns=["date", "NI_YTD"])
    df_ni['date'] = pd.to_datetime(df_ni['date'])

    # NI(분기순이익) column 생성
    m = df_ni['date'].dt.month
    base_month = next((mm for mm in (1, 2, 3) if (m == mm).any()), None) # 1,2,3 중에서 실제로 존재하는 첫 번째 달 찾기
    mask = (m == base_month) if base_month is not None else pd.Series(False, index=df_ni.index)
    df_ni[NI.label] = np.where(mask, df_ni["NI_YTD"], df_ni["NI_YTD"].diff()) # 선택된 달만 NI_YTD, 나머지는 diff() 사용    
    #df_ni[NI.label] = df_ni[NI.label].replace(0, float('nan')).ffill() # NaN -> NaN이 아닌 가장 최근값

    # NI_TTM(최근 4분기 합산 순이익) column 생성
    mask = df_ni[NI.label] != 0
    ni_nonzero = df_ni.loc[mask, NI.label]
    ni_ttm_nonzero = ni_nonzero.rolling(window=4, min_periods=4).sum() # 0이 아닌 값들만 따로 꺼내 rolling TTM 계산
    df_ni.loc[mask, 'NI_TTM'] = ni_ttm_nonzero.values # 원래 df_ni에 NI_TTM 컬럼 만들고, 0이 아닌 곳에만 값 채우기
    df_ni['NI_TTM'] = df_ni['NI_TTM'].ffill() # 0 -> "0이 아닌 값" 중 가장 최근
    # ------------------------------------------------------------------------------------------------------------------

    #df_ni = df_ni.dropna(subset=['NI_TTM']) # NI_TTM 결측치 행 제거 (자동으로 NI 결측행도 제거됨)
    df_ni['date'] = df_ni['date'].dt.strftime('%Y-%m-%d') # datetime -> 문자열
    df_ni = df_ni.iloc[::-1] # 날짜 오름차순 정렬
    df_ni.to_excel(f"data/{stk_code}/NI_month.xlsx", index=False)

    print("✅ 모든 DART 데이터 저장 완료.")
