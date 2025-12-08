import requests
import json
import pandas as pd
from datetime import datetime
import os

base_url = "https://ecos.bok.or.kr/api"

APIkey = "5O3QUZG5ICSESDI650G2"
table_code = ["731Y001", "817Y002", "902Y016", "901Y027", "901Y009"] # 환율, 금리, GDP, 실업률
table_name = ["EXCHANGE", "MARKET_INTEREST", "GDP", "~EMPLOY", "CPI"] 
item_code1  = ["0000001", "010210000", "KOR", "I61BC", "0"] # 원/달러, 시장금리, GDP, 실업률, 소비자물가지수, 총지수 
itme_code2  = ["", "", "", "I28B", ""] # _,_,_,실업률
cycle       = ["D", "D", "A", "M", "M"]
start_date  = "1990-01-01"
end_date    = "2025-12-05"

param_fmt = {"A": "%Y", "M": "%Y%m", "D": "%Y%m%d"}
time_in_fmt = {"A": "%Y", "M": "%Y%m", "D": "%Y%m%d"}
time_out_fmt = {"A": "%Y", "M": "%Y-%m", "D": "%Y-%m-%d"}

if __name__ == "__main__":
    start_dt = pd.to_datetime(start_date, format="%Y-%m-%d")
    end_dt   = pd.to_datetime(end_date,   format="%Y-%m-%d")

    for idx in range(len(table_code)):
        table_code_i = table_code[idx]
        item_code1_i = item_code1[idx]
        item_code2_i = itme_code2[idx]
        table_name_i = table_name[idx]
        cycle_i      = cycle[idx]

        if cycle_i == "A":
            delta_rows = end_dt.year - start_dt.year
        elif cycle_i == "M":
            delta_rows = (end_dt.year - start_dt.year) * 12 + (end_dt.month - start_dt.month)
        elif cycle_i == "D":
            delta_rows = (end_dt - start_dt).days

        start_param = start_dt.strftime(param_fmt[cycle_i])
        end_param   = end_dt.strftime(param_fmt[cycle_i])

        start_request_num = 1
        end_request_num   = start_request_num + delta_rows

        url = (
            f"{base_url}/StatisticSearch/{APIkey}/json/kr/"
            f"{start_request_num}/{end_request_num}/"
            f"{table_code_i}/{cycle_i}/{start_param}/{end_param}/{item_code1_i}/{item_code2_i}"
        )

        response = requests.get(url)
        date_list, value_list = [], []

        if response.status_code == 200:
            data = response.json()
            if "StatisticSearch" not in data:
                print("ECOS 오류 응답:", data)
                continue

            rows = data["StatisticSearch"]["row"]

            for row in rows:
                t = row["TIME"]
                v = row["DATA_VALUE"]

                dt = datetime.strptime(t, time_in_fmt[cycle_i])
                date = dt.strftime(time_out_fmt[cycle_i])

                date_list.append(date)
                value_list.append(v)
                print(f"==== 날짜: {date}, {table_name_i}: {v} ====")

        else:
            print("요청 실패, status_code =", response.status_code)
            continue

        df_ecos = pd.DataFrame({"date": date_list, table_name_i: value_list})
        save_path = f"data/{table_name_i}.xlsx"
        df_ecos.to_excel(save_path, index=False)
        print(f"[저장 완료] {save_path}")
