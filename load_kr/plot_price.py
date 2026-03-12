from load_price import crawl_price, ws_to_df
from utils import plot_with_sma

import matplotlib as mpl
mpl.rcParams["font.family"] = "NanumGothic"
#mpl.rcParams["font.family"] = "Malgun Gothic"
mpl.rcParams["axes.unicode_minus"] = False

import talib
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv() # .env 파일에 저장된 환경 변수를 로드
    corp_name, start_date, end_date = "삼성전자", "2025-02-02", "2026-03-10"

    price_ws = crawl_price(corp_name=corp_name, start_date=start_date, end_date=end_date)
    price_df = ws_to_df(price_ws)

    date = price_df['date']
    close = price_df['Close']
    
    close_sma5 = talib.SMA(close, timeperiod=5)
    close_sma20 = talib.SMA(close, timeperiod=20)
    close_sma60 = talib.SMA(close, timeperiod=60)

    price_df["Close_SMA5"] = close_sma5
    price_df["Close_SMA20"] = close_sma20
    price_df["Close_SMA60"] = close_sma60
    
    price_df.to_excel(f"data/{corp_name}_{start_date}_{end_date}/PRICE_day.xlsx", index=False)

    data_dict = {
        "corp_name": corp_name,
        "date": date,
        "close": close,
        "SMA5": close_sma5,
        "SMA20": close_sma20,
        "SMA60": close_sma60
    }

    plot_with_sma(data_dict=data_dict, start_date=start_date, end_date=end_date)