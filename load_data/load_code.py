import requests
import zipfile
import io
from xml.etree import ElementTree as ET

def fetch_corp_codes(api_key: str):
    url = f"https://opendart.fss.or.kr/api/corpCode.xml?crtfc_key={api_key}"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    # 반환은 ZIP 압축된 바이너리
    z = zipfile.ZipFile(io.BytesIO(resp.content))
    # 압축 파일 안에 CORPCODE.xml 파일 있음
    with z.open("CORPCODE.xml") as f:
        tree = ET.parse(f)
        root = tree.getroot()
        corp_list = []
        for item in root.iter("list"):
            corp_code = item.findtext("corp_code")
            corp_name = item.findtext("corp_name")
            stock_code = item.findtext("stock_code")
            # stock_code는 비상장기업은 빈 문자열일 수 있음
            corp_list.append({
                "corp_code": corp_code,
                "corp_name": corp_name,
                "stock_code": stock_code
            })
        return corp_list

if __name__ == "__main__":
    API_KEY = "3957b81997e850b1a08e448a63e193dd0f630a25"
    corps = fetch_corp_codes(API_KEY)
    # 예시: 상위 10개만 출력
for c in corps:
    if c['corp_name'] == '삼성중공업':
        print(f"회사명: {c['corp_name']}, corp_code: {c['corp_code']}, 주식코드: {c['stock_code']}")
