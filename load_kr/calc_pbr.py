import pandas as pd
import numpy as np
from utils import get_config, fetch_corp_codes
import os

if __name__ == "__main__":
    config = get_config()
    api_key = os.getenv("DART_API_KEY")
    start, end = config.date["start"], config.date["end"]
    target_corp_names = config.target_corp_names

    for target_corp_name in target_corp_names:
        corp_name, corp_code, stk_code = fetch_corp_codes(target_corp_name, api_key)

        # 주가
        df_price = pd.read_excel(f"data/{corp_name}_{stk_code}/PRICE_day.xlsx") 
        df_price['date'] = pd.to_datetime(df_price['date']) # str -> datetime

        # 자기자본
        df_equ = pd.read_excel(f"data/{corp_name}_{stk_code}/EQU_month.xlsx") 
        date_equ = pd.to_datetime(df_equ['date']) # str -> datetime
        date_equ = date_equ.dt.strftime('%Y-%m').values # series -> numpy array

        # 발행주식수
        df_shs = pd.read_excel(f"data/{corp_name}_{stk_code}/SHS_month.xlsx")
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
        df_pbr.to_excel(f"data/{corp_name}_{stk_code}/PBR_day.xlsx", index=False) # save to excel
        print(f"[{corp_name}] PBR_day.xlsx saved.")