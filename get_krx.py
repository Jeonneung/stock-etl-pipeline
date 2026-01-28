import os
import requests
import json

KRX_API_KEY = os.getenv("KRX_API_KEY")

if not KRX_API_KEY:
    raise ValueError("KRX_API_KEY 환경변수를 설정해주세요.")

SERVER_ENDPOINT_URL = "http://data-dbg.krx.co.kr/svc/apis/sto/stk_bydd_trd"

urlInput = '?basDd='
targetDate = '20230710'

url = SERVER_ENDPOINT_URL + urlInput + targetDate
headers = {
    'AUTH_KEY': KRX_API_KEY
}

res = requests.get(url=url, headers=headers)
result = json.loads(res.text)

print(result)
