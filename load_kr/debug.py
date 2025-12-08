'''
# test_full_response.py
import requests
import json

API_KEY = "3957b81997e850b1a08e448a63e193dd0f630a25"
CORP_CODE = "00126478"  # 삼성중공업
BSNS_YEAR = "2025"
REPRT_CODE = "11014"  

url = "https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json"
params = {"crtfc_key": API_KEY,
          "corp_code": CORP_CODE,
          "bsns_year": BSNS_YEAR,
          "reprt_code": REPRT_CODE,
          "fs_div": "CFS"}

TARGET_ACCOUNT_IDS = [
    # 지배기업 소유주지분
    "ifrs-full_ProfitLossAttributableToOwnersOfParent",
    "ifrs_ProfitLossAttributableToOwnersOfParent",
]

response = requests.get(url, params=params)
data = response.json()

if data.get("status") == "000":
    rows = data.get("list") or []


    # 당기순이익 필터링
    for it in rows:
        if it.get("sj_div") == "IS" and it.get("account_id") in TARGET_ACCOUNT_IDS:
            found_owners_profit = True
            print(json.dumps(it, indent=2, ensure_ascii=False))

else:
    print(data.get("status"), data.get("message"))

'''
# test_full_response.py
import requests
import json

YEARS = range(2016, 2026)  # 2015 ~ 2025
REPRT_CODES = ["11011", "11012", "11013", "11014"]  # 사업, 반기, 3분기, 1분기

API_KEY = "3957b81997e850b1a08e448a63e193dd0f630a25"
CORP_CODE = "00164779"  # SK하이닉스

url = "https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json"
TARGET_ACCOUNTS = ("지배기업소유주지분")

for year in YEARS:
    for reprt_code in REPRT_CODES:
        params = {
            "crtfc_key": API_KEY,
            "corp_code": CORP_CODE,
            "bsns_year": year,
            "reprt_code": reprt_code,
            "fs_div": "CFS",
        }

        response = requests.get(url, params=params)
        data = response.json()

        status = data.get("status")
        message = data.get("message")

        # 1) API 자체가 실패한 경우 먼저 출력
        if status != "000":
            print(
                f"[API_FAIL] year={year}, reprt_code={reprt_code} -> "
                f"status={status}, message={message}"
            )
            continue

        rows = data.get("list") or []

        # 2) 순이익 row가 있는지 찾기
        found_owners_profit = False

        # 지배기업 소유주지분
        TARGET_ACCOUNT_IDS = ["ifrs-full_ProfitLossAttributableToOwnersOfParent",
                              "ifrs_ProfitLossAttributableToOwnersOfParent"]
        for it in rows:
            if (it.get("sj_div") in ("IS", "CIS") or
               it.get("account_id") in TARGET_ACCOUNT_IDS and
               it.get("account_nm") in ("지배기업 소유주지분", "지배기업소유주지분", 
                                        "지배기업의 소유주에게 귀속되는 당기순이익(손실)")):
                found_owners_profit = True
                break  

        # 3) 순이익 row가 하나도 없을 때만 출력
        if not found_owners_profit:
            print(
                f"[NO_NET_INCOME] year={year}, reprt_code={reprt_code} -> "
                f"status={status}, message={message}"
            )
            print(json.dumps(it, indent=2, ensure_ascii=False))
