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
    # 연도 데이터니까 이렇게 쓰는 게 자연스러움
    start, end = '2000-01-01', '2025-12-31'
    step = 1

    fig, ax = plt.subplots(figsize=(12, 5))

    metric = 'ROE'
    fpth = f'data/010140/{metric}_day.xlsx'

    plot_data(fpth, freq='month', value_col=metric,
              start=start,end=end,
              normalize=False,step=step,
              ax=ax, label=metric
    )
    ax.set_ylabel(metric)

    # 먼저 저장, 그 다음 보여주기 (취향 따라 순서 바꿔도 큰 문제는 없음)
    plt.tight_layout()
    plt.savefig(f'plot/{metric}.png', dpi=600)
    plt.show()
