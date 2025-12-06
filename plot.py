import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def plot_data(file_path, freq='day', value_col=None, start=None, end=None, step=1):
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

    plt.plot(x, y)
    plt.xlabel(freq)
    plt.xticks(x[::step], rotation=45, fontsize=10, fontstyle='italic')
    plt.ylabel(value_col)
    plt.title(f'<{value_col} over {freq}>', fontsize=20)
    plt.show()

    return df_processed

fpth = 'data/ECOS_day.xlsx'
plot_data(fpth, freq='day', value_col='exchange_rate',
          start='2025-01-01', end='2025-12-07', step=5)