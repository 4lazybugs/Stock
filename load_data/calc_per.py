import pandas as pd
import numpy as np

# 주가
df_price = pd.read_excel("data/010140/PRICE_day.xlsx") 
df_price['date'] = pd.to_datetime(df_price['date']) # str -> datetime

# 자기자본
df_ni = pd.read_excel("data/010140/NI_month.xlsx") 
date_ni = pd.to_datetime(df_ni['date']) # str -> datetime
date_ni = date_ni.dt.strftime('%Y-%m').values # series -> numpy array

# 발행주식수
df_shs = pd.read_excel("data/010140/SHS_month.xlsx")
date_shs = pd.to_datetime(df_shs['date']) # str -> datetime
date_shs = date_shs.dt.strftime('%Y-%m').values # series -> numpy array

# per 
df_per = pd.DataFrame(columns=['date', 'PER'])
df_per['date'] = df_price['date']

# EPS
df_eps = pd.DataFrame(columns=['date', 'EPS'])
df_eps['date'] = df_price['date']

for i in range(len(df_price)):
    flag1, flag2 = False, False
    
    date_per = df_price['date'][i].strftime('%Y-%m')
    if date_per in date_ni:
        flag1 = True
        # i번째 ni 날짜 반환 : i번째 ni 날짜 ∈ {price의 날짜}
        idx_ni = np.where(date_ni == date_per)[0][0] # [0][0] : array[3,2] -> [3,2] -> 3  
    if date_per in date_shs:
        # i번째 shs 날짜 반환 : i번째 shs 날짜 ∈ {price의 날짜}
        flag2 = True
        idx_shs = np.where(date_shs == date_per)[0][0] # [0][0] : array[3,2] -> [3,2] -> 3    

    if flag1 and flag2:
        price = df_price.loc[i, 'Close']
        ni = df_ni.loc[idx_ni, 'NI_TTM']
        shs = df_shs.loc[idx_shs, 'SHS']
        eps = ni/shs # calc eps
        df_eps.loc[i, 'EPS'] = eps # calc eps
        df_per.loc[i, 'PER'] = price / eps # calc per

# save to excel : eps
df_eps['date'] = df_eps['date'].dt.strftime('%Y-%m-%d') # datetime -> str
df_eps.to_excel("data/010140/EPS_day.xlsx", index=False) # save to excel

# save to excel : per
df_per['date'] = df_per['date'].dt.strftime('%Y-%m-%d') # datetime -> str
df_per.to_excel("data/010140/PER_day.xlsx", index=False) # save to excel