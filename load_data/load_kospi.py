import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook
import time
from datetime import datetime
import os

headers = {
"User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"),
"Referer": "https://finance.naver.com/",
"Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
}

session = requests.Session()
session.headers.update(headers)

##### 코스피 지수 일일시세 크롤링 함수 ##############################################
def get_kospi(session, code, start_date_str, end_date_str):
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    end_date   = datetime.strptime(end_date_str, "%Y-%m-%d").date()

    page = 1
    results = []
    stop_flag = False

    while True:
        url = f"https://finance.naver.com/sise/sise_index_day.naver?code={code}&page={page}"
        r = session.get(url, timeout=10)
        r.encoding = "euc-kr"
        soup = BeautifulSoup(r.text, "html.parser")
        
        # ✅ 일별 시세 테이블
        table = soup.select_one("div.box_type_m > table.type_1")
        if not table:
            print(f"⚠️ {code} - {page} 페이지에 table 없음 → 종료")
            break

        rows = table.select("tr")
        if not rows:
            print(f"⚠️ {code} - {page} 페이지에 tr 없음 → 종료")
            break

        page_has_data = False
        for row in rows:
            tds = row.find_all("td")
            # 데이터가 아닌 공백/구분선/헤더 행 걸러내기
            if len(tds) != 6:
                continue

            trade_date_str = tds[0].get_text(strip=True) # 0: 날짜
            if not trade_date_str:
                continue

            # 날짜 파싱
            trade_date = datetime.strptime(trade_date_str, "%Y.%m.%d").date()

            # 날짜 필터링
            if trade_date > end_date:
                # 너무 최근 데이터 → 다음 row
                continue
            if trade_date < start_date:
                print(f"{code} - {page} 페이지에서 시작 날짜보다 더 옛날 데이터 발견 → 크롤링 종료")
                stop_flag = True
                break

            close = tds[1].get_text(strip=True).replace(",", "") # 1: 체결가(종가) number_1

            change_span = tds[2].select_one("span") # 2: 전일비 rate_up / rate_down 안의 span
            change = change_span.get_text(strip=True).replace(",", "") if change_span else ""

            rate_span = tds[3].select_one("span") # 3: 등락률 number_1 안의 span
            rate = rate_span.get_text(strip=True).replace(",", "") if rate_span else ""

            volume = tds[4].get_text(strip=True).replace(",", "") # 4: 거래량 number_1
            money  = tds[5].get_text(strip=True).replace(",", "") # 5: 거래대금 number_1

            # ✅ 사진 순서대로 저장: 날짜, 체결가, 전일비, 등락률, 거래량, 거래대금
            results.append((trade_date_str, close, change, rate, volume, money))
            page_has_data = True
            print(f"{code} - {page} 페이지: {trade_date_str} 데이터 수집 완료")

        page += 1
        time.sleep(0.1)

        if stop_flag: break

    return results
######################################################################################

if __name__ == "__main__":
    codes = [
        #'042660',  # 한화오션
        #'009540',  # HD한국조선해양
        'KOSPI',  # 코스피 지수
        #'010620',  # 현대미포조선
        #'329180',  # 현대중공업
        #'097230',  # HJ중공업
        #'238490',  # 현대힘스
        #'077970',  # STX엔진
        #'267250',  # HD현대마린엔진
    ]
    
    # 크롤링 날짜 설정
    target_date_str = ["2023-12-01", "2025-12-01"]
    start_date, end_date = target_date_str[0], target_date_str[1]

    for code in codes:
        print(f"\n📈 크롤링 시작: {code}")

        # 엑셀 워크북/시트 생성
        wb = Workbook()
        ws = wb.active
        ws.title = code
        ws.append(["date", "KOSPI", "Change", "Change_rate", "Volume", "Trading Value"])

        # ✅ 코스피 지수용 크롤링
        data_rows = get_kospi(session, code, start_date, end_date)

        # 날짜 오름차순 정렬
        data_rows = sorted(
            data_rows,
            key=lambda x: datetime.strptime(x[0], "%Y.%m.%d")
        )

        # (date, close, change, rate, volume, money)
        for trade_date, close, change, rate, volume, money in data_rows:
            close_val = float(close) if close != "" else 0.0
            open_val  = close_val
            high_val  = close_val
            low_val   = close_val
            vol_val   = int(volume) if volume != "" else 0

            ws.append([
                trade_date,
                close_val,
                open_val,
                high_val,
                low_val,
                vol_val,
            ])


        # ✅ 종목별로 개별 파일 저장
        save_dir = f"data/{code}"
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, "PRICE_day.xlsx")
        wb.save(save_path)
        print(f"✅ 저장 완료: {save_path}")
