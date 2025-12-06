import requests
import json
import pandas as pd
from datetime import datetime

base_url = "https://ecos.bok.or.kr/api"

# params : https://ecos.bok.or.kr/api/#/DevGuide/StatisticalCodeSearch 참고
APIkey = "5O3QUZG5ICSESDI650G2" # API키
table_code = ["731Y001", "817Y002"]  # 환율(일별), 시장금리(일별)
table_name = ["EXCHANGE", "MARKET_INTEREST"]
item_code = ["0000001", "010210000"]   # 달러/원
cycle = "D"   
start_date = "19900101"
end_date = "20251205"

if __name__ == "__main__":
    start_date_dt = pd.to_datetime(start_date, format="%Y%m%d") # 문자열 -> datetime
    end_date_dt = pd.to_datetime(end_date, format="%Y%m%d") # 문자열 -> datetime
    delta = end_date_dt - start_date_dt #차이 계산

    for i in range(len(table_code)):
        table_code_i = table_code[i]
        item_code_i = item_code[i]
        table_name_i = table_name[i]
        start_request_num = 1
        end_request_num = start_request_num + delta.days

        url = (
            f"{base_url}/StatisticSearch/{APIkey}/json/kr/"
            f"{start_request_num}/{end_request_num}/"
            f"{table_code_i}/{cycle}/{start_date}/{end_date}/{item_code_i}"
        )

        response = requests.get(url)
        date_list, value_list = [], []

        if response.status_code == 200:
            try:
                #print("=== response.json() ===")
                data = response.json()
                #print(json.dumps(data, indent=2, ensure_ascii=False))
                for i in range(len(data["StatisticSearch"]["row"])):
                    date = data["StatisticSearch"]["row"][i]["TIME"]
                    date = datetime.strptime(date, "%Y%m%d").strftime("%Y-%m-%d")  # str -> datetime
                    date_list.append(date)
                    value = data["StatisticSearch"]["row"][i]["DATA_VALUE"]
                    value_list.append(value)
                    print(f"==== 날짜: {date}, {table_name_i}: {value} ====")
            except Exception as e:
                print("JSON 디코딩 에러:", str(e))
            else:
                print("요청 실패, status_code =", response.status_code)

            df_ecos = pd.DataFrame({"date": date_list, table_name_i: value_list})
            df_ecos.to_excel(f"data/{table_name_i}_day.xlsx", index=False)