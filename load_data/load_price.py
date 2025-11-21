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

for code in codes:
    print(f"\n📈 크롤링 시작: {code}")
    wb = Workbook()
    ws = wb.active
    ws.title = code
    ws.append(["date", "Close", "Open", "High", "Low", "Volume"])
    
    START_PAGE, MAX_PAGES = 20, 30
    for page in range(START_PAGE, MAX_PAGES + 1):
        url = f"https://finance.naver.com/item/sise_day.naver?code={code}&page={page}"
        r = session.get(url, timeout=10)
        r.encoding = "euc-kr"
        soup = BeautifulSoup(r.text, "html.parser")

        table = soup.select_one("table.type2")
        if not table:
            break

        rows_with_data = 0
        for row in table.select("tr"):
            tds = [td.get_text(strip=True) for td in row.find_all("td")]
            if len(tds) == 7 and tds[0]:
                trade_date, close, _, open_, high, low, volume = tds
                dt = datetime.strptime(trade_date, "%Y.%m.%d").date()
                date_str = dt.isoformat()  # 'YYYY-MM-DD'
                ws.append([date_str,
                        int(close.replace(",", "")),
                        int(open_.replace(",", "")),
                        int(high.replace(",", "")),
                        int(low.replace(",", "")),
                        int(volume.replace(",", ""))])
                rows_with_data += 1

        if rows_with_data == 0:
            break
        print(f"  페이지 {page}: {rows_with_data}개 데이터 수집")
        time.sleep(0.5)

    # ✅ 종목별로 개별 파일 저장
    save_dir = f'../data/{code}'
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, f"PRICE_day.xlsx")
    wb.save(save_path)
    print(f"✅ 저장 완료: {save_path}")
