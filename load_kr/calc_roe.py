import pandas as pd
import numpy as np

# 주가
df_price = pd.read_excel("data/010140/PRICE_day.xlsx") 
df_price['date'] = pd.to_datetime(df_price['date']) # str -> datetime

# 지배주주순이익
df_ni = pd.read_excel("data/010140/NI_month.xlsx") 
date_ni = pd.to_datetime(df_ni['date']) # str -> datetime
date_ni = date_ni.dt.strftime('%Y-%m').values # series -> numpy array

# 발행주식수
df_equ = pd.read_excel("data/010140/EQU_month.xlsx")
date_equ = pd.to_datetime(df_equ['date']) # str -> datetime
date_equ = date_equ.dt.strftime('%Y-%m').values # series -> numpy array

# roe
df_roe = pd.DataFrame(columns=['date', 'ROE'])
df_roe['date'] = df_price['date']

for i in range(len(df_price)):
    flag1, flag2 = False, False
    
    date_per = df_price['date'][i].strftime('%Y-%m')
    if date_per in date_ni:
        flag1 = True
        # i번째 ni 날짜 반환 : i번째 ni 날짜 ∈ {price의 날짜}
        idx_ni = np.where(date_ni == date_per)[0][0] # [0][0] : array[3,2] -> [3,2] -> 3  
    if date_per in date_equ:
        # i번째 equ 날짜 반환 : i번째 equ 날짜 ∈ {price의 날짜}
        flag2 = True
        idx_equ = np.where(date_equ == date_per)[0][0] # [0][0] : array[3,2] -> [3,2] -> 3    

    if flag1 and flag2:
        price = df_price.loc[i, 'Close']
        ni = df_ni.loc[idx_ni, 'NI_TTM']
        equ = df_equ.loc[idx_equ, 'EQU']
        roe = (ni/equ)*100 # calc roe
        df_roe.loc[i, 'ROE'] = roe # calc roe

# save to excel : roe
df_roe['date'] = df_roe['date'].dt.strftime('%Y-%m-%d') # datetime -> str
df_roe.to_excel("data/010140/ROE_day.xlsx", index=False) # save to excel