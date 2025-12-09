import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from utils import get_config

def plot_data(file_path, freq='day', value_col=None,
              start=None, end=None, step=1, ax=None,
              normalize=True, label=None):

    if ax is None:
        ax = plt.gca()

    # 1) Load data
    df = pd.read_excel(file_path)
    df['date'] = df['date'].astype(str) 

    # 2) frequency 별 처리
    if freq == 'year':
        df['date'] = pd.to_datetime(df['date'], format='%Y')
        # 이미 연 단위 데이터이므로 groupby 불필요
        df_processed = df.sort_values('date').set_index('date')

    elif freq == 'month':
        df['date'] = pd.to_datetime(df['date'])
        df_processed = (
            df.sort_values('date')
              .groupby(df['date'].dt.to_period('M'))
              .first()
        )
        df_processed.index = df_processed.index.to_timestamp()
        df_processed.index.name = 'month'

    elif freq == 'day':
        df['date'] = pd.to_datetime(df['date'])
        df_processed = df.sort_values('date').set_index('date')

    # 3) start / end 범위 자르기
    if start is not None:
        start = pd.to_datetime(start)
    if end is not None:
        end = pd.to_datetime(end)

    if start is not None or end is not None:
        df_processed = df_processed.loc[start:end]

    # 4) Plot
    x = df_processed.index          # DatetimeIndex
    y = df_processed[value_col]

    if label is None:
        label = value_col

    if normalize:
        y_min, y_max = y.min(), y.max()
        y_norm = (y - y_min) / (y_max - y_min)
        ax.plot(x, y_norm, label=label)

        # y축 눈금: 위치는 정규화 기준, 라벨은 원래 값
        yticks_orig = np.linspace(y_min, y_max, 5)
        yticks_pos = (yticks_orig - y_min) / (y_max - y_min)
        ax.set_yticks(yticks_pos)
        ax.set_yticklabels([f"{v:.2f}" for v in yticks_orig],
                           fontsize=13, fontstyle='italic')
    else:
        ax.plot(x, y, label=label)

    ax.set_ylabel(value_col, fontsize=15)
    ax.set_xlabel(freq)

    # x축 라벨 (연도/월을 문자열로 변환해서 사용)
    x_labels = x.astype(str)
    ax.set_xticks(x[::step])
    ax.set_xticklabels(x_labels[::step],
                       rotation=45, fontsize=10, fontstyle='italic')

    ax.legend()

    # 마우스 오버하면 값 보여주는 기능 (원하면 주석 해제)
    # mplcursors.cursor(ax.lines, hover=True)

if __name__ == "__main__":
    config = get_config()
    start, end = config.date["start"], config.date["end"]

    ####### ~EMPLOY #######
    fig, ax = plt.subplots(figsize=(12, 5))
    metric = '~EMPLOY'
    fpth = f'data/{metric}.xlsx'
    plot_data(fpth, freq='month', value_col=metric,
              start=start,end=end,
              normalize=False,step=5,
              ax=ax, label=metric
    )
    ax.set_ylabel(metric)
    plt.tight_layout()
    plt.title(f'{metric} over Time', fontsize=16)
    plt.savefig(f'plot/~EMPLOY.png', dpi=600)
    plt.show()

    ####### MARKET_INTEREST #######
    fig, ax = plt.subplots(figsize=(12, 5))
    fpth = f'data/MARKET_INTEREST.xlsx'
    plot_data(fpth, freq='day', value_col="MARKET_INTEREST",
              start=start,end=end,
              normalize=False,step=200,
              ax=ax, label="MARKET_INTEREST"
    )
    ax.set_ylabel("MARKET_INTEREST")
    plt.tight_layout()
    plt.title(f'MARKET_INTEREST over Time', fontsize=16)
    plt.savefig(f'plot/MARKET_INTEREST.png', dpi=600)
    plt.show()

    ####### EXCHANGE_RATE #######
    fig, ax = plt.subplots(figsize=(12, 5))
    fpth = f'data/EXCHANGE.xlsx'
    plot_data(fpth, freq='day', value_col="EXCHANGE",
              start=start,end=end,
              normalize=False,step=300,
              ax=ax, label="EXCHANGE"
    )
    ax.set_ylabel("EXCHANGE")
    plt.tight_layout()
    plt.title(f'EXCHANGE over day', fontsize=16)
    plt.savefig(f'plot/EXCHANGE.png', dpi=600)
    plt.show()

    ####### KOSPI #######
    fig, ax = plt.subplots(figsize=(12, 5))
    fpth = f'data/KOSPI/PRICE_day.xlsx'
    plot_data(fpth, freq='day', value_col="KOSPI",
              start=start,end=end,
              normalize=False,step=1,
              ax=ax, label="KOSPI"
    )
    ax.set_ylabel("KOSPI")
    plt.tight_layout()
    plt.title(f'KOSPI over day', fontsize=16)
    plt.savefig(f'plot/KOSPI.png', dpi=600)
    plt.show()