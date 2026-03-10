import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook
import time
from datetime import datetime
import os
import requests
import zipfile
import io
import xml.etree.ElementTree as ET
import pandas as pd

__all__ = ["date_to_page", "fetch_code", "crawl_price", "ws_to_array"]

headers = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/124.0.0.0 Safari/537.36"),
    "Referer": "https://finance.naver.com/",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
}

session = requests.Session()
session.headers.update(headers)
api_key = os.getenv("DART_API_KEY")

########### 특정 날짜가 네이버 금융 일일시세 어느 페이지에 있는지 탐색하는 함수 ##################
def date_to_page(session, code, start_date_str, end_date_str):
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

    page = 1
    results = []
    flag_stop = False
    max_page = None

    while True:

        url = f"https://finance.naver.com/item/sise_day.naver?code={code}&page={page}"
        r = session.get(url, timeout=10)
        r.encoding = "euc-kr"
        soup = BeautifulSoup(r.text, "html.parser")

        # 마지막 페이지 탐색
        if max_page is None:
            pg_rr = soup.select_one("td.pgRR a")
            if pg_rr and "page=" in pg_rr["href"]:
                try:
                    max_page = int(pg_rr["href"].split("page=")[-1])
                except ValueError:
                    max_page = page
            else:
                max_page = page

        table = soup.select_one("table.type2")
        if not table:
            break

        rows = table.select("tr")

        for row in rows:

            tds = [td.get_text(strip=True) for td in row.find_all("td")]

            if len(tds) != 7 or not tds[0]:
                continue

            trade_date_str = tds[0]
            trade_date = datetime.strptime(trade_date_str, "%Y.%m.%d").date()

            if trade_date > end_date:
                continue

            if trade_date < start_date:
                flag_stop = True
                break

            close, _, open_, high, low, volume = tds[1:7]

            results.append(
                (trade_date_str, close, open_, high, low, volume)
            )

        if flag_stop:
            break

        if max_page is not None and page >= max_page:
            break

        page += 1
        time.sleep(0.1)

    return results
############################################################################


############## 기업 코드 로드 ###########################
def fetch_code(target_corp_name, api_key=None):
    # 인자로 api_key 안 넘기면 환경변수에서 가져오도록 (기존 코드 유지 느낌)
    if api_key is None:
        api_key = os.getenv("DART_API_KEY")

    url = f"https://opendart.fss.or.kr/api/corpCode.xml?crtfc_key={api_key}"
    
    # 🔁 재시도 설정 (모든 예외에 대해 재시도)
    last_exc = None
    max_retry = 10000
    retry_delay = 0.1  # 초

    root = None  # XML 루트 노드

    for attempt in range(1, max_retry + 1):
        try:
            # 1) 네트워크 요청
            resp = requests.get(url, timeout=0.5)
            resp.raise_for_status()

            # 2) ZIP 열기
            z = zipfile.ZipFile(io.BytesIO(resp.content))

            # 3) ZIP 안의 CORPCODE.xml 파싱
            with z.open("CORPCODE.xml") as f:
                tree = ET.parse(f)
                root = tree.getroot()

            # 여기까지 문제 없으면 루프 성공 종료
            break

        except Exception as e:
            # Timeout, HTTPError, ConnectionError, BadZipFile, ParseError 등
            last_exc = e
            print(
                f"[corpCode Retry] attempt {attempt}/{max_retry} "
                f"→ {retry_delay}초 후 재시도 (err={type(e).__name__})"
            )

            if attempt == max_retry:
                # 마지막 시도까지 실패하면 마지막 예외를 그대로 올림
                raise last_exc

            time.sleep(retry_delay)

    # 여기까지 왔다면 root는 정상적으로 파싱된 상태
    for item in root.iter("list"):
        corp_code = item.findtext("corp_code")
        corp_name = item.findtext("corp_name")
        stock_code = item.findtext("stock_code")

        if corp_name == target_corp_name:
            return corp_name, corp_code, stock_code

    # 찾는 회사가 없으면 None 반환 (이건 네트워크/파싱 에러가 아니므로 재시도 대상 아님)
    return None, None, None
############################################################################


def crawl_price(corp_name, start_date, end_date, save_dir = "data"):
    """
    특정 종목의 주가 데이터를 크롤링하고 엑셀로 저장
    """
    print(f"\n📈 크롤링 시작: {corp_name}")

    # 엑셀 파일 생성
    wb = Workbook()

    # 시트 생성 및 제목 행 추가
    ws = wb.active
    ws.title = corp_name ## 시트 이름을 종목명으로 설정
    ws.append(["date", "Close", "Open", "High", "Low", "Volume"]) ## 제목 행 추가

    corp_name, corp_code, stk_code = fetch_code(corp_name, api_key)
    data_rows = date_to_page(session, stk_code, start_date, end_date)

    data_rows = sorted(
        data_rows,
        key=lambda x: datetime.strptime(x[0], "%Y.%m.%d")
    )

    for trade_date, close, open_, high, low, volume in data_rows:

        ws.append([
            trade_date,
            int(close.replace(",", "")),
            int(open_.replace(",", "")),
            int(high.replace(",", "")),
            int(low.replace(",", "")),
            int(volume.replace(",", "")) if volume != "" else 0,
        ])

    save_path_dir = f"../{save_dir}/{corp_name}_{start_date}_{end_date}"
    os.makedirs(save_path_dir, exist_ok=True)

    save_path = os.path.join(save_path_dir, "PRICE_day.xlsx")

    wb.save(save_path)

    print(f"✅ 저장 완료: {save_path}")

    return ws

def ws_to_df(ws):
    rows = list(ws.values)
    columns = rows[0]
    data = rows[1:]
    df = pd.DataFrame(data, columns=columns)
    return df