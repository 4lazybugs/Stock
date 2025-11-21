import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def plot_data(df: pd.DataFrame, x_col: str, y_col: str, title: str = "Data Plot"):
    plt.figure(figsize=(10, 6))
    plt.plot(df[x_col], df[y_col], marker='o')
    plt.title(title)
    plt.xlabel(x_col)
    plt.ylabel(y_col)
    plt.grid(True)
    plt.show()

df = pd.read_excel('../data/010140/merged.xlsx')
plot_data(df, x_col='date', y_col='PBR', title='PBR Over Time')
plot_data(df, x_col='date', y_col='ROE', title='ROE Over Time')
