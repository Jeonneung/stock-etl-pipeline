import os
import re
from typing import List, Optional, Tuple

import pandas as pd


def get_latest_file(file_paths: List[str]) -> Optional[str]:
    if not file_paths:
        return None
    return max(file_paths, key=os.path.getmtime)


def read_excel(file_path: str) -> pd.DataFrame:
    return pd.read_excel(file_path)


def read_latest_excel(file_paths: List[str]) -> Optional[pd.DataFrame]:
    latest = get_latest_file(file_paths)
    if latest is None:
        return None
    return read_excel(latest)


def extract_date_from_filename(filepath: str) -> Optional[str]:
    """
    파일명에서 날짜 추출 (YYYYMMDD → YYYY-MM-DD)

    예: 전종목시세_20260125.xlsx → 2026-01-25
    """
    match = re.search(r'(\d{8})', filepath)
    if match:
        date_str = match.group(1)
        return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
    return None


def extract(**context):
    """
    Extract: 원본 데이터 읽기만 수행 (ETL/ELT 공용)

    Returns:
        dict: {'stock': DataFrame, 'pbr': DataFrame}
    """
    ti = context['ti']

    market_files = ti.xcom_pull(key='marketPrice_files')
    per_files = ti.xcom_pull(key='perData_files')

    # 최신 파일 경로
    market_file = get_latest_file(market_files)
    per_file = get_latest_file(per_files)

    stock_df = read_excel(market_file)
    pbr_df = read_excel(per_file)

    # 파일명에서 거래일 추출
    market_trade_date = extract_date_from_filename(market_file)
    per_trade_date = extract_date_from_filename(per_file)

    # XCom으로 전달 (DataFrame은 JSON 직렬화)
    ti.xcom_push(key='stock_data', value=stock_df.to_json())
    ti.xcom_push(key='pbr_data', value=pbr_df.to_json())
    ti.xcom_push(key='market_trade_date', value=market_trade_date)
    ti.xcom_push(key='per_trade_date', value=per_trade_date)
    ti.xcom_push(key='market_file', value=market_file)
    ti.xcom_push(key='per_file', value=per_file)

    return {
        'stock': len(stock_df),
        'pbr': len(pbr_df),
        'market_trade_date': market_trade_date,
        'per_trade_date': per_trade_date,
    }