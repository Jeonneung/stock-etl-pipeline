import pandas as pd

# 하나의 데이터로 만드는 작업
class ExtractData:
    def extract_with_excel(stock_file, pbr_file):
        # data/전종목시세_20260125.xlsx
        stock = pd.read_excel(stock_file)
        # data/PER:PBR:배당수익률_20260125.xlsx
        pbr = pd.read_excel(pbr_file)

        stock_info = pd.merge(stock, pbr, 'right', on='종목코드')

        drop_columns = ['종목명_y', '종가_y', '대비_y', '등락률_y']
        stock_info.drop(columns=drop_columns, inplace=True)

        stock_info.rename(columns={
            '종목명_x': '종목명',
            '종가_x': '종가',
            '대비_x': '대비',
            '등락률_x': '등락률',
            }
            , inplace=True)
        
        return stock_info

    def extract_with_api():
        import os
        import requests
        import json

        KRX_API_KEY = os.getenv('KRX_API_KEY')

        # 유가증권 일별매매정보
        SERVER_ENDPOINT_URL = "http://data-dbg.krx.co.kr/svc/apis/sto/stk_bydd_trd"

        targetDate = '20230710'
        params = {
            'basDd': targetDate
        }    
        headers = {
            'AUTH_KEY': KRX_API_KEY
        }

        res = requests.get(url=SERVER_ENDPOINT_URL, params=params, headers=headers)
        result = json.loads(res.text)

        return result

