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

        # 지배주주 순이익
        df_ni = pd.read_excel(f"data/{corp_name}_{stk_code}/NI_month.xlsx") 
        date_ni = pd.to_datetime(df_ni['date']) # str -> datetime
        date_ni = date_ni.dt.strftime('%Y-%m').values # series -> numpy array

        # 총자산
        df_ast = pd.read_excel(f"data/{corp_name}_{stk_code}/AST_month.xlsx")
        date_ast = pd.to_datetime(df_ast['date']) # str -> datetime
        date_ast = date_ast.dt.strftime('%Y-%m').values # series -> numpy array

        # roa
        df_roa = pd.DataFrame(columns=['date', 'ROA'])
        df_roa['date'] = df_price['date']

        for i in range(len(df_price)):
            flag1, flag2 = False, False
            
            date_per = df_price['date'][i].strftime('%Y-%m')
            if date_per in date_ni:
                flag1 = True
                # i번째 ni 날짜 반환 : i번째 ni 날짜 ∈ {price의 날짜}
                idx_ni = np.where(date_ni == date_per)[0][0] # [0][0] : array[3,2] -> [3,2] -> 3  
            if date_per in date_ast:
                # i번째 equ 날짜 반환 : i번째 equ 날짜 ∈ {price의 날짜}
                flag2 = True
                idx_ast = np.where(date_ast == date_per)[0][0] # [0][0] : array[3,2] -> [3,2] -> 3    

            if flag1 and flag2:
                price = df_price.loc[i, 'Close']
                ni = df_ni.loc[idx_ni, 'NI_TTM']
                ast = df_ast.loc[idx_ast, 'AST']
                roa = (ni/ast)*100 # calc roa
                df_roa.loc[i, 'ROA'] = roa # calc roa

        # save to excel : roa
        df_roa['date'] = df_roa['date'].dt.strftime('%Y-%m-%d') # datetime -> str
        df_roa.to_excel(f"data/{corp_name}_{stk_code}/ROA_day.xlsx", index=False) # save to excel