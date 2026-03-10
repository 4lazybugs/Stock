import argparse
import yaml
import os
from xml.etree import ElementTree as ET
import numpy as np
import pandas as pd

import matplotlib as mpl
import matplotlib.pyplot as plt
mpl.rcParams["font.family"] = "Malgun Gothic"
mpl.rcParams["axes.unicode_minus"] = False

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
    parser.add_argument("--corp", type=str, default=default_cfg.get('corp'))
    parser.add_argument("--date", type=str, default=default_cfg.get('date'))
    parser.add_argument("--step", type=str, default=default_cfg.get('step'))

    args = parser.parse_args()
    return args


############### plot with SMA ##########################
def plot_with_sma(data_dict, start_date, end_date):
    corp_name = data_dict["corp_name"]

    # 1. 딕셔너리 내 Series들을 하나로 묶어서 관리 (정렬/필터링 편의성)
    df = pd.DataFrame({k: v for k, v in data_dict.items() if k != "corp_name"})
    
    # 2. 날짜 변환 및 전체 정렬 (이거 한 줄이면 싹 다 정렬됨)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)

    # 3. 기간 필터링 (mask)
    mask = (df['date'] >= pd.to_datetime(start_date)) & (df['date'] <= pd.to_datetime(end_date))
    plot_df = df[mask].reset_index(drop=True)

    # 4. 시각화 시작
    plt.figure(figsize=(12, 7))
    plt.plot(plot_df['date'], plot_df['close'], label="Close", linewidth=2)

    # SMA로 시작하는 컬럼들만 찾아서 플롯
    sma_keys = [col for col in plot_df.columns if col.startswith("SMA")]
    for key in sma_keys:
        plt.plot(plot_df['date'], plot_df[key], label=key)

    # 5. 눈금 계산 (정확히 10개 추출)
    idx = np.unique(np.linspace(0, len(plot_df) - 1, 10, dtype=int))
    
    # 날짜 포맷 적용하여 x축 출력
    plt.xticks(plot_df['date'].iloc[idx], 
               labels=[d.strftime('%Y-%m-%d') for d in plot_df['date'].iloc[idx]], 
               rotation=45, fontsize=16)
    plt.yticks(fontsize=16)

    plt.title(f"<{corp_name} 주가와 이동평균선>", fontsize=20)
    plt.legend(fontsize=20, loc="upper left")
    plt.grid(False)
    plt.tight_layout()
    plt.show()