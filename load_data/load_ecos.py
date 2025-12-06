import requests
import json
import pandas as pd
from datetime import datetime
import os

base_url = "https://ecos.bok.or.kr/api"

APIkey = "5O3QUZG5ICSESDI650G2"  # API키
table_code = ["731Y001", "817Y002", "902Y016"]  # 환율(일별), 시장금리(일별), 국내총생산(연간)
table_name = ["EXCHANGE", "MARKET_INTEREST", "GDP"]
item_code  = ["0000001", "010210000", "KOR"]   # 달러/원, 10년국채금리, 한국
cycle      = ["D", "D", "A"]
start_date = "19900101"
end_date   = "20251205"

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)

    # 공통: 일수 계산 (일별용)
    start_dt = pd.to_datetime(start_date, format="%Y%m%d")
    end_dt   = pd.to_datetime(end_date,   format="%Y%m%d")
    delta_days = (end_dt - start_dt).days + 1

    for idx in range(len(table_code)):
        table_code_i = table_code[idx]
        item_code_i  = item_code[idx]
        table_name_i = table_name[idx]
        cycle_i      = cycle[idx]

        # === 1) 주기에 따라 요청 기간, 개수 설정 ===
        if cycle_i == "A":  # 연간 GDP
            start_param = start_date[:4]  # "1990"
            end_param   = end_date[:4]    # "2025"

            start_year = int(start_param)
            end_year   = int(end_param)
            n_rows     = end_year - start_year + 1
        else:               # 일별 데이터
            start_param = start_date      # "19900101"
            end_param   = end_date        # "20251205"
            n_rows      = delta_days

        start_request_num = 1
        end_request_num   = start_request_num + n_rows - 1

        url = (
            f"{base_url}/StatisticSearch/{APIkey}/json/kr/"
            f"{start_request_num}/{end_request_num}/"
            f"{table_code_i}/{cycle_i}/{start_param}/{end_param}/{item_code_i}"
        )

        response = requests.get(url)
        date_list, value_list = [], []

        if response.status_code == 200:
            try:
                data = response.json()
                # 에러 응답일 경우 대비
                if "StatisticSearch" not in data:
                    print("ECOS 오류 응답:", data)
                    continue

                rows = data["StatisticSearch"]["row"]

                for row in rows:
                    t = row["TIME"]

                    # === 2) 주기에 따라 TIME 파싱 다르게 ===
                    if cycle_i == "A":   # "1990"
                        date = datetime.strptime(t, "%Y").strftime("%Y")
                    else:                # "19900101"
                        date = datetime.strptime(t, "%Y%m%d").strftime("%Y-%m-%d")

                    value = row["DATA_VALUE"]

                    date_list.append(date)
                    value_list.append(value)
                    print(f"==== 날짜: {date}, {table_name_i}: {value} ====")

            except Exception as e:
                print("예외 발생:", repr(e))
                continue
        else:
            print("요청 실패, status_code =", response.status_code)
            continue

        # === 3) 엑셀 저장 ===
        df_ecos = pd.DataFrame({"date": date_list, table_name_i: value_list})
        df_ecos.to_excel(f"data/{table_name_i}.xlsx", index=False)
