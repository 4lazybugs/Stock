import argparse
import yaml
import os
import requests
import zipfile
import io
from xml.etree import ElementTree as ET
from dotenv import load_dotenv
from requests.exceptions import Timeout, RequestException
import time

############ load config.yaml ########################
def load_yaml(path='config.yaml'):
    with open(path, 'r', encoding='utf-8') as f:
        raw_config = yaml.safe_load(f)

    # 환경 변수 치환 처리
    config = {}
    for k, v in raw_config.items():
        if isinstance(v, str):
            config[k] = os.path.expandvars(v)
        else:
            config[k] = v

    return config

############### get config ##########################
def get_config():
    default_cfg = load_yaml()

    parser = argparse.ArgumentParser()
    parser.add_argument("--target_corp_names", type=str, default=default_cfg.get('target_corp_names'))
    parser.add_argument("--date", type=str, default=default_cfg.get('date'))
    parser.add_argument("--step", type=str, default=default_cfg.get('step'))

    args = parser.parse_args()
    return args

############## 기업 코드 로드 ###########################
load_dotenv()
def fetch_corp_codes(target_corp_name, api_key=None):
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