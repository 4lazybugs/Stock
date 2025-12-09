import argparse
import yaml
import os
import requests
import zipfile
import io
from xml.etree import ElementTree as ET
from dotenv import load_dotenv

############ load config.yaml ########################
def load_yaml(path='load_kr/config.yaml'):
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
def fetch_corp_codes(target_corp_name, api_key):
    api_key = os.getenv("DART_API_KEY")
    url = f"https://opendart.fss.or.kr/api/corpCode.xml?crtfc_key={api_key}"
    
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()

    # 반환은 ZIP 압축된 바이너리
    z = zipfile.ZipFile(io.BytesIO(resp.content))
    # 압축 파일 안에 CORPCODE.xml 파일 있음
    with z.open("CORPCODE.xml") as f:
        tree = ET.parse(f)
        root = tree.getroot()

        for item in root.iter("list"):
            corp_code = item.findtext("corp_code")
            corp_name = item.findtext("corp_name")
            stock_code = item.findtext("stock_code")

            if corp_name == target_corp_name:
                    return corp_name, corp_code, stock_code
        
    return None, None, None