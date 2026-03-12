from openai import OpenAI
import pandas as pd
import tabulate

from openai import OpenAI
import pandas as pd

if __name__ == "__main__":
    corp_name, start_date, end_date = "삼성전자", "2025-02-02", "2026-03-10"
    df = pd.read_excel(f"data/{corp_name}_{start_date}_{end_date}/PRICE_day.xlsx")

    # df를 md로 변환
    df_md = df.to_markdown(index=False)
    print(df_md)
    
    client = OpenAI(
        base_url="http://127.0.0.1:8000/v1",
        api_key="EMPTY",
    )

    response = client.chat.completions.create(
        model="mistralai/Mistral-Nemo-Instruct-FP8-2407",
        temperature=0,
        messages=[
            {"role": "system", "content": "You are a stock analyst. Always respond in Korean."},
            {"role": "user",
            "content": f"""다음은 종가 데이터입니다: {df_md}
                            이 데이터를 분석해서 다음을 한국말로 알려주세요:
                            1. 현재 추세 (상승/하락/횡보)

                            2. 지지선/저항선

                            3. 매수/매도/관망 추천"""}],
                            )

    print(response.choices[0].message.content)