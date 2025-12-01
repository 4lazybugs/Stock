import pandas as pd
import numpy as np

# 주가
df_price = pd.read_excel("data/010140/PRICE_day.xlsx") 
df_price['date'] = pd.to_datetime(df_price['date']) # str -> datetime

# 자기자본
df_equ = pd.read_excel("data/010140/EQU_month.xlsx") 
date_equ = pd.to_datetime(df_equ['date']) # str -> datetime
date_equ = date_equ.dt.strftime('%Y-%m').values # series -> numpy array

# 발행주식수
df_shs = pd.read_excel("data/010140/SHS_month.xlsx")
date_shs = pd.to_datetime(df_shs['date']) # str -> datetime
date_shs = date_shs.dt.strftime('%Y-%m').values # series -> numpy array

# PBR 
df_pbr = pd.DataFrame(columns=['date', 'PBR'])
df_pbr['date'] = df_price['date']

for i in range(len(df_price)):
    flag1, flag2 = False, False
    
    date_pbr = df_price['date'][i].strftime('%Y-%m')
    if date_pbr in date_equ:
        flag1 = True
        # i번째 equ 날짜 반환 : i번째 equ 날짜 ∈ {price의 날짜}
        idx_equ = np.where(date_equ == date_pbr)[0][0] # [0][0] : array[3,2] -> [3,2] -> 3  
    if date_pbr in date_shs:
        # i번째 shs 날짜 반환 : i번째 shs 날짜 ∈ {price의 날짜}
        flag2 = True
        idx_shs = np.where(date_shs == date_pbr)[0][0] # [0][0] : array[3,2] -> [3,2] -> 3    

    if flag1 and flag2:
        price = df_price.loc[i, 'Close']
        equ = df_equ.loc[idx_equ, 'EQU']
        shs = df_shs.loc[idx_shs, 'SHS']
        bvps = equ/shs # calc bvps
        df_pbr.loc[i, 'PBR'] = price / bvps # calc PBR

df_pbr['date'] = df_pbr['date'].dt.strftime('%Y-%m-%d') # datetime -> str
df_pbr = df_pbr.iloc[::-1] # 날짜 오름차순 정렬
df_pbr.to_excel("data/010140/PBR_day.xlsx", index=False) # save to excel