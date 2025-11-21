# load_dart.py
import os
import pandas as pd
from datetime import date, timedelta
from models_DART import SHS, EQU, NI  # ✅ BaseMetric import 필요 없음

# -----------------------
# 날짜 생성 유틸
# -----------------------
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


# ✅ BaseMetric import 없이 작동하도록 변경
def row(metric, d: date):
    d_str = d.isoformat() # 날짜를 ISO 문자열로 변환해 저장, "YYYY-MM-DD"
    v, _, _, _ = metric.fetch_with_fallback(corp_code, d)
    return (d_str, v)


if __name__ == "__main__":    
    API_KEY = "3957b81997e850b1a08e448a63e193dd0f630a25"
    stk_code, corp_code = "010140", "00126478"  # 삼성중공업 예시
    dates = generate_dates("2024-08-01", "2025-10-31", mode="month")

    shs_metric = SHS(api_key=API_KEY)
    equ_metric = EQU(api_key=API_KEY)
    ni_metric = NI(api_key=API_KEY)
    
    os.makedirs("data", exist_ok=True)

    
    # 1) 발행주식수
    rows_sh = [row(shs_metric, d) for d in dates]
    df_sh = pd.DataFrame(rows_sh, columns=["date", SHS.label])
    df_sh.to_excel(f"data/{stk_code}/SHS_month.xlsx", index=False)

    # 2) EQU
    rows_equ = [row(equ_metric, d) for d in dates]
    df_equ = pd.DataFrame(rows_equ, columns=["date", EQU.label]) 
    df_equ.to_excel(f"data/{stk_code}/EQU_month.xlsx", index=False)
    

    # 3) NI
    rows_ni = [row(ni_metric, d) for d in dates]
    df_ni = pd.DataFrame(rows_ni, columns=["date", NI.label]) 
    df_ni.to_excel(f"data/{stk_code}/NI_year.xlsx", index=False)

    print("✅ 모든 DART 데이터 저장 완료.")
