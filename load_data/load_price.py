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

########### 특정 날짜가 네이버 금융 일일시세 어느 페이지에 있는지 탐색하는 함수 ##################
def date_to_page(session, code, start_date_str, end_date_str):
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

    page= 1
    results = []
    flag_stop = False

    while True:
        url = f"https://finance.naver.com/item/sise_day.naver?code={code}&page={page}"
        r = session.get(url, timeout=10)
        r.encoding = "euc-kr"
        soup = BeautifulSoup(r.text, "html.parser")

        # 일일시세 테이블 선택
        table = soup.select_one("table.type2")
        if not table:
            print(f"⚠️ {code} - {page} 페이지에 table이 없음. 종료.")
            break

        # 테이블 내 모든 데이터 행(tr) 추출
        rows = table.select("tr")
        if not rows:
            print(f"⚠️ {code} - {page} 페이지에 row가 없음. 종료.")
            break
        
        for row in rows:
            tds = [td.get_text(strip=True) for td in row.find_all("td")]
            if len(tds) != 7 or not tds[0]: # 데이터 유효성 체크
                continue

            trade_date_str = tds[0] 
            trade_date = datetime.strptime(trade_date_str, "%Y.%m.%d").date()

            if trade_date > end_date: continue # 너무 최근(끝 날짜보다 더 최신)이면 그냥 건너뛰고 다음 row
            if trade_date < start_date: # 시작 날짜보다 더 옛날이 나오면 이 페이지 이후로는 볼 필요 없음
                print(f"{code} - {page} 페이지에서 시작 날짜보다 더 옛날 데이터 발견 → 크롤링 종료")
                flag_stop = True
                break

            # 네이버 일일시세 컬럼 순서: (0: 날짜, 1: 종가, 2: 전일비, 3: 시가, 4: 고가, 5: 저가, 6: 거래량)
            close, _, open_, high, low, volume = tds[1:7]
            results.append((trade_date_str, close, open_, high, low, volume))
            print(f"{code} - {page} 페이지에서 {trade_date_str} 날짜 데이터 크롤링 완료")

        page += 1
        time.sleep(0.1)
        
        if flag_stop: break

    return results
############################################################################

if __name__ == "__main__":
    codes = [
        #'042660',  # 한화오션
        #'009540',  # HD한국조선해양
        '010140',  # 삼성중공업
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
        ws.append(["date", "Close", "Open", "High", "Low", "Volume"])

        data_rows = date_to_page(session, code, start_date, end_date)

        # 날짜 오름차순 정렬 (과거 → 최신)
        data_rows = sorted(
            data_rows,
            key=lambda x: datetime.strptime(x[0], "%Y.%m.%d")
        )

        # 엑셀에 쓰기
        for trade_date, close, open_, high, low, volume in data_rows:
            ws.append([
                trade_date,
                int(close.replace(",", "")),
                int(open_.replace(",", "")),
                int(high.replace(",", "")),
                int(low.replace(",", "")),
                int(volume.replace(",", "")) if volume != "" else 0,
            ])

        # ✅ 종목별로 개별 파일 저장
        save_dir = f"data/{code}"
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, "PRICE_day.xlsx")
        wb.save(save_path)
        print(f"✅ 저장 완료: {save_path}")
