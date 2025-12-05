import requests
import json

base_url = "https://ecos.bok.or.kr/api"

# params : https://ecos.bok.or.kr/api/#/DevGuide/StatisticalCodeSearch 참고
APIkey = "5O3QUZG5ICSESDI650G2" # API키
table_code = "731Y001"  # 통계표코드
cycle = "D"
start = "20240101"
end = "20240110"
item_code = "0000001"   # 달러/원
start_request_num = 1
end_request_num = 10

url = (
    f"{base_url}/StatisticSearch/{APIkey}/json/kr/"
    f"{start_request_num}/{end_request_num}/"
    f"{table_code}/{cycle}/{start}/{end}/{item_code}/?/?/?"
)

response = requests.get(url)

print("요청 URL:", response.url)
print("status_code:", response.status_code)

if response.status_code == 200:
    try:
        #print("=== response.json() ===")
        data = response.json()
        #print(json.dumps(data, indent=2, ensure_ascii=False))
        for i in range(len(data["StatisticSearch"]["row"])):
            date = data["StatisticSearch"]["row"][i]["TIME"]
            value = data["StatisticSearch"]["row"][i]["DATA_VALUE"]
            print(f"==== 날짜: {date}, 환율: {value} ====")
    except Exception as e:
        print("JSON 디코딩 에러:", str(e))
else:
    print("요청 실패, status_code =", response.status_code)