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
    df['date'] = pd.to_datetime(df['date'])
    
    # 2) Process data by frequency
    if freq == 'year':
        df_processed = (
            df.sort_values('date')
              .groupby(df['date'].dt.year)
              .first()
        )
        df_processed.index.name = 'year'
        df_processed.index = df_processed.index.astype(str)

    elif freq == 'month':
        df_processed = (
            df.sort_values('date')
              .groupby(df['date'].dt.to_period('M'))
              .first()
        )
        df_processed.index = df_processed.index.astype(str)
        df_processed.index.name = 'month'

    elif freq == 'day':
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

    ax.set_ylabel(value_col, fontsize=15)
    ax.set_xlabel(freq)
    ax.set_xticks(x[::step])
    ax.set_xticklabels(x[::step], rotation=45, fontsize=10, fontstyle='italic')


if __name__ == "__main__":
    start, end = '2000-01-01', '2025-12-07'
    step = 100

    fig, ax = plt.subplots(figsize=(12, 5))

    fpth = 'data/EXCHANGE_day.xlsx'
    plot_data(fpth, freq='day', value_col='EXCHANGE',
            start=start, end=end,
            step=step, ax=ax, label='EXCHANGE[₩/$]')
    ax.set_ylabel('EXCHANGE')

    fpth = 'data/MARKET_INTEREST_day.xlsx'
    plot_data(fpth, freq='day', value_col='MARKET_INTEREST',
            start=start, end=end,
            step=step, ax=ax, label='MARKET_INTEREST[%]')
    
    ax.set_title('<EXCHANGE_RATE and MARKET_INTEREST>', fontsize=20)

    plt.show()