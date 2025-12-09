import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
from utils import get_config

def plot_data(file_path, freq='day', value_col=None, 
              start=None, end=None, step=1, ax=None, 
              normalize=True, label=None):
    if ax is None:
        ax = plt.gca()

    # 1) Load data
    df = pd.read_excel(file_path)
    df['date'] = df['date'].astype(str)
    
    # 2) Process data by frequency
    if freq == 'year':
        df['date'] = pd.to_datetime(df['date'], format='%Y')
        df_processed = (
            df.sort_values('date')
              .groupby(df['date'].dt.year)
              .first()
        )
        df_processed.index.name = 'year'
        df_processed.index = df_processed.index.astype(str)

    elif freq == 'month':
        df['date'] = pd.to_datetime(df['date'])
        df_processed = (
            df.sort_values('date')
              .groupby(df['date'].dt.to_period('M'))
              .first()
        )
        df_processed.index = df_processed.index.astype(str)
        df_processed.index.name = 'month'

    elif freq == 'day':
        df['date'] = pd.to_datetime(df['date'])
        df_processed = df.set_index('date')
        df_processed.index = df_processed.index.astype(str)

    # 3) start/end initialization
    df_processed = df_processed.loc[start:end]

    # 4) Plot
    x = df_processed.index
    y = df_processed[value_col]

    if label is None:
        label = value_col

    if normalize:
        y_min = y.min()
        y_max = y.max()
        y_norm = (y - y_min) / (y_max - y_min)   # 0~1 스케일

        ax.plot(x, y_norm, label=label)

        # y축 눈금: 위치는 정규화 기준, 라벨은 원래 값
        yticks_orig = np.linspace(y_min, y_max, 5)  # 원래 값 기준 5개 눈금
        yticks_pos = (yticks_orig - y_min) / (y_max - y_min)

        ax.set_yticks(yticks_pos)
        ax.set_yticklabels([f"{v:.2f}" for v in yticks_orig], fontsize=13, fontstyle='italic')
    
    else:
        ax.plot(x, y, label=label)

    ax.set_xlabel(freq)
    ax.set_xticks(x[::step])
    ax.set_xticklabels(x[::step], rotation=45, fontsize=10, fontstyle='italic')


if __name__ == "__main__":
    config = get_config()
    start, end = config.date['start'], config.date['end']
    step = 2

    fig, ax_left = plt.subplots(figsize=(12, 5))
    ax_right = ax_left.twinx()   # 오른쪽 y축 하나 생성

    '''
    fpth = 'data/000660/PER_day.xlsx'
    plot_data(fpth, freq='month', value_col=f'PER',
            start=start, end=end,
            step=step, ax=ax_left, label='PER')
    ax_left.set_ylabel('PER', fontsize=15)
    ax_left.set_title('<PER & PBR>', fontsize=20)

    fpth = 'data/삼성생명_032830/PRICE_day.xlsx'
    plot_data(fpth, freq='month', value_col=f'Close',
            start=start, end=end,
            step=step, ax=ax_left, label='Close')
    ax_left.set_ylabel('SK HY', fontsize=15)
    ax_left.set_title('<PBR & SK>', fontsize=20)

    fpth = 'data/삼성생명_032830/PBR_day.xlsx'
    plot_data(fpth, freq='month', value_col=f'PBR',
            start=start, end=end,
            step=step, ax=ax_right, label='PBR')
    ax_right.set_ylabel('PBR', fontsize=15)

    # 왼쪽/오른쪽 축에서 handle & label 합치기
    lines_left, labels_left = ax_left.get_legend_handles_labels()
    line_left = ax_left.get_lines()[0].set_color("C0")
    lines_right, labels_right = ax_right.get_legend_handles_labels()
    line_right = ax_right.get_lines()[0].set_color("C1")
    
    ax_left.legend(
        lines_left + lines_right, labels_left + labels_right,
        loc='lower left', fontsize=15
    )

    plt.tight_layout()
    plt.savefig(f'plot/CPI and MARKET_INTEREST.png', dpi=600)
    plt.show()
    '''

    '''
    fpth = 'data/CPI.xlsx'
    plot_data(fpth, freq='month', value_col=f'CPI',
            start=start, end=end,
            step=step, ax=ax_left, label='CPI')
    ax_left.set_ylabel('CPI', fontsize=15)
    ax_left.set_title('<CPI % Market Interest>', fontsize=20)
    '''

    ########### KOSPI & EXCHANGE_RATE ############
    fpth = 'data/EXCHANGE.xlsx'
    plot_data(fpth, freq='day', value_col=f'EXCHANGE',
            start=start, end=end,
            step=step, ax=ax_left, label='EXCHANGE[₩/$]')
    ax_left.set_ylabel('EXCHANGE', fontsize=15)
    ax_left.set_title('<EXCHANGE_RATE and KOSPI>', fontsize=20)

    fpth = 'data/KOSPI/PRICE_day.xlsx'
    plot_data(fpth, freq='day', value_col=f'KOSPI',
            start=start, end=end,
            step=step, ax=ax_right, label='KOSPI')
    ax_right.set_ylabel('KOSPI', fontsize=15)

    # 왼쪽/오른쪽 축에서 handle & label 합치기
    lines_left, labels_left = ax_left.get_legend_handles_labels()
    line_left = ax_left.get_lines()[0].set_color("C0")
    lines_right, labels_right = ax_right.get_legend_handles_labels()
    line_right = ax_right.get_lines()[0].set_color("C1")
    
    ax_left.legend(
        lines_left + lines_right, labels_left + labels_right,
        loc='lower left', fontsize=15
    )

    plt.tight_layout()
    fdir = 'plot/ecos_figs'
    os.makedirs(fdir, exist_ok=True)
    plt.savefig(f'{fdir}/EXCHANGE_RATE_&_KOSPI.png', dpi=600)
    plt.show()

    '''
    fpth = 'data/MARKET_INTEREST.xlsx'
    #fpth = 'data/MARKET_INTEREST_day.xlsx'
    plot_data(fpth, freq='month', value_col='MARKET_INTEREST',
            start=start, end=end,
            step=step, ax=ax_right, label='MARKET_INTEREST')
    ax_right.set_ylabel('MARKET_INTEREST', fontsize=15)
    '''