# derive_metrics.py
import os
import glob
import pandas as pd

class DataStore:
    """폴더 내 xlsx를 파일 '스텀(stem)'으로 속성화: PRICE.xlsx -> .PRICE, NI_001234.xlsx -> .NI"""
    def __init__(self, folder):
        for f in glob.glob(os.path.join(folder, "*.xlsx")):
            base = os.path.basename(f)                 # 'PRICE.xlsx'
            stem = os.path.splitext(base)[0]           # 'PRICE'
            name = stem.split('_')[0].upper()          # 'PRICE' 또는 'NI'/'EPS' 등
            setattr(self, name, pd.read_excel(f))      # self.PRICE, self.NI, self.EPS, self.SHS, self.EQU ...

def asof_merge(base, target, col):
    """date 기준으로 가장 가까운 과거값 매칭"""
    return pd.merge_asof(
        base.sort_values("date"),
        target.sort_values("date").rename(columns={target.columns[1]: col}),
        on="date",
        direction="backward"
    )

def last_of_quarter(df, cols):
    """
    일별(df)에서 분기 말 기준으로 각 분기의 '마지막 관측치'를 뽑아온다.
    cols: ['NI', 'SHS'] 등 보존할 컬럼 리스트
    반환: 분기 말 날짜와 지정 컬럼만 가진 DataFrame
    """
    tmp = df.copy()
    tmp["q"] = tmp["date"].dt.to_period("Q")  # Q-DEC 기준 (회계연도 12월 가정)
    # 분기별 마지막 행 인덱스(날짜 기준) 잡기
    idx = tmp.groupby("q")["date"].idxmax()
    qdf = tmp.loc[idx].sort_values("date").reset_index(drop=True)
    keep = ["date"] + cols
    return qdf[keep]

if __name__ == "__main__":
    corp_code = "010140"              # 폴더 이름과 일치해야 함 (load_price / load_dart 저장 규칙)
    start, end = "20200101", "20221231"
    folder = f"../data/{corp_code}"

    data = DataStore(folder)

    # 가격(필수)
    if not hasattr(data, "PRICE"):
        raise FileNotFoundError(f"{folder}/PRICE.xlsx 가 필요합니다.")
    base = data.PRICE.rename(columns={data.PRICE.columns[1]: "CLOSE"})
    base["date"] = pd.to_datetime(base["date"])

    # -------------------------
    # DART 데이터 머지 (EQU, SHS, + NI 로드)
    # -------------------------
    # EQU, SHS는 그대로 asof 머지
    for name in ["EQU", "SHS"]:
        if hasattr(data, name):
            df = getattr(data, name).copy()
            df["date"] = pd.to_datetime(df["date"])
            base = asof_merge(base, df, name)

    # NI 원천 찾기: NI.xlsx 우선, 없으면 EPS.xlsx를 NI로 간주(폴백)
    ni_source_name = None
    if hasattr(data, "NI"):
        ni_df_raw = data.NI.copy()
        ni_source_name = "NI"
    elif hasattr(data, "EPS"):
        ni_df_raw = data.EPS.copy()   # 폴백: EPS 파일을 NI로 간주
        ni_source_name = "EPS-as-NI"
    else:
        raise FileNotFoundError(f"{folder} 에 NI.xlsx 또는 EPS.xlsx 파일이 필요합니다.")

    ni_df_raw["date"] = pd.to_datetime(ni_df_raw["date"])

    # 머지(원시 NI 값 한 번 붙여두면 디버깅 편함) — 컬럼명 'NI_RAW'
    base = asof_merge(base, ni_df_raw, "NI_RAW")

    # -------------------------
    # 분기별 NI/SHS로 TTM EPS 계산
    # -------------------------
    # 분기 말(last-of-quarter) 관측치 추출
    #  - NI_RAW: 분기 순이익(전처리 단계에서 '분기' 값임을 가정; 누적이라면 전처리에서 분기화 필요)
    #  - SHS: 발행주식수 (분기말 보정용)
    if "SHS" not in base.columns:
        raise ValueError("SHS(발행주식수) 데이터가 필요합니다. SHS.xlsx를 생성/저장하세요.")

    qbase = base[["date", "NI_RAW", "SHS"]].dropna(subset=["NI_RAW", "SHS"]).copy()
    q = last_of_quarter(qbase, ["NI_RAW", "SHS"]).rename(columns={"NI_RAW": "NI_Q"})

    # TTM(최근 4개 분기 합)
    q["NI_TTM"] = q["NI_Q"].rolling(window=4, min_periods=4).sum()
    q["EPS_TTM"] = q["NI_TTM"] / q["SHS"]

    # 일별로 asof 머지: 각 일자에 대해 직전 분기의 TTM EPS가 매칭됨
    base = asof_merge(base, q[["date", "EPS_TTM"]], "EPS")

    # -------------------------
    # 파생지표 계산
    # -------------------------
    # BPS = EQU / SHS
    # PBR = CLOSE / BPS
    # MKT = CLOSE * SHS
    equ = base.get("EQU")
    shs = base.get("SHS")

    base["BPS"] = equ / shs
    base["PBR"] = base["CLOSE"] / (base["BPS"] + 1e-6)
    base["MKT"] = base["CLOSE"] * shs

    # (선택) PER도 보고 싶으면 주석 해제
    # base["PER"] = base["CLOSE"] / (base["EPS"] + 1e-6)

    os.makedirs(f"../data/{corp_code}", exist_ok=True)
    out = f"../data/{corp_code}/merged.xlsx"
    base.to_excel(out, index=False)
    print(f"✅ 계산 및 저장 완료: {out}  | NI source = {ni_source_name}")
