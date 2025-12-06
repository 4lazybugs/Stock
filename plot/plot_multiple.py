import matplotlib.pyplot as plt
import mplcursors
import numpy as np
import pandas as pd

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

    # plot_data 함수 내부 수정: ax.plot에 label 인수를 추가합니다.
    if normalize:
        y_min = y.min()
        y_max = y.max()
        y_norm = (y - y_min) / (y_max - y_min)   # 0~1 스케일

        # ⭐ 수정 1: label=label 추가
        ax.plot(x, y_norm, label=label) 

        # y축 눈금은 모두 정규화된 0~1 스케일을 공유하므로 주석 처리된 상태로 둡니다.
        # ax.set_yticks(yticks_pos)
        # ax.set_yticklabels([f"{v:.2f}" for v in yticks_orig], fontsize=13, fontstyle='italic')
    
    else:
        # ⭐ 수정 1: label=label 추가
        ax.plot(x, y, label=label)

    ax.set_xlabel(freq)
    ax.set_xticks(x[::step])
    ax.set_xticklabels(x[::step], rotation=45, fontsize=10, fontstyle='italic')


if __name__ == "__main__":
    start, end = '2000-01-01', '2025-12-07'
    step = 100

    fig, ax = plt.subplots(figsize=(12, 5))

    # ⭐ 수정 2: GDP의 freq를 'year'에서 'day'로 변경하여 X축 스케일 통일
    fpth = 'data/GDP.xlsx'
    plot_data(fpth, freq='day', value_col='GDP',
               start=start, end=end,
               step=step, ax=ax, label='GDP')

    fpth = 'data/EXCHANGE.xlsx'
    plot_data(fpth, freq='day', value_col='EXCHANGE',
               start=start, end=end,
               step=step, ax=ax, label='EXCHANGE[₩/$]')

    fpth = 'data/MARKET_INTEREST.xlsx'
    plot_data(fpth, freq='day', value_col='MARKET_INTEREST',
               start=start, end=end,
               step=step, ax=ax, label='MARKET_INTEREST[%]')
    
    # Y축 레이블 추가 (모두 0~1로 정규화되었음을 명시)
    ax.set_ylabel('Normalized Value (0 to 1)', fontsize=15) 

    ax.set_title('market interest & exchange & GDP', fontsize=20)
    
    # ⭐ 수정 3: 수동 범례 대신 ax.legend()를 사용하여 플롯된 라인의 레이블을 자동으로 가져옵니다.
    # plot_data에서 label 인수를 넘겼으므로 이제 자동으로 범례를 만들 수 있습니다.
    ax.legend(fontsize=15) 

    mplcursors.cursor(hover=True)

    plt.savefig(f'plot/EXCHANGE_RATE and KOSPI.png', dpi=600)
    plt.show()