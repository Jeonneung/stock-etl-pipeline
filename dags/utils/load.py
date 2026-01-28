import pandas as pd
from typing import Optional

from airflow.providers.postgres.hooks.postgres import PostgresHook

from utils.extract import extract_date_from_filename

# 한글 → 영문 컬럼 매핑 (시세 데이터)
DAILY_PRICE_COLUMN_MAP = {
    '종목코드': 'stock_code',
    '종목명': 'stock_name',
    '종가': 'close_price',
    '대비': 'change_amount',
    '등락률': 'change_rate',
    '시가': 'open_price',
    '고가': 'high_price',
    '저가': 'low_price',
    '거래량': 'volume',
    '거래대금': 'trade_value',
    '시가총액': 'market_cap',
    '상장주식수': 'shares_outstanding',
}

# 한글 → 영문 컬럼 매핑 (PER/PBR 데이터)
VALUATION_COLUMN_MAP = {
    '종목코드': 'stock_code',
    '종목명': 'stock_name',
    '종가': 'close_price',
    '대비': 'change_amount',
    '등락률': 'change_rate',
    'EPS': 'eps',
    'PER': 'per',
    '선행 EPS': 'forward_eps',
    '선행 PER': 'forward_per',
    'BPS': 'bps',
    'PBR': 'pbr',
    '배당수익률': 'dividend_yield',
}


def rename_columns(df: pd.DataFrame, column_map: dict) -> pd.DataFrame:
    """한글 컬럼명을 영문으로 변환"""
    return df.rename(columns=column_map)


def load_to_bronze(
    df: pd.DataFrame,
    table: str,
    column_map: dict,
    source_file: str,
    trade_date: str,
    conn_id: str = 'postgres_default'
) -> int:
    """
    Bronze 테이블에 원본 데이터 로드 (전부 TEXT)

    Args:
        df: 로드할 DataFrame
        table: 테이블명 (bronze_daily_price 또는 bronze_valuation)
        column_map: 컬럼 매핑
        source_file: 원본 파일명
        trade_date: 거래일 (파일명에서 추출)
        conn_id: Airflow connection ID

    Returns:
        삽입된 행 수
    """
    # 컬럼명 변환
    df_renamed = rename_columns(df.copy(), column_map)

    # 매핑에 있는 컬럼만 선택
    valid_columns = [col for col in column_map.values() if col in df_renamed.columns]
    df_load = df_renamed[valid_columns].copy()

    # 전부 문자열로 변환 (Bronze는 TEXT)
    df_load = df_load.astype(str)

    # source_file, trade_date 추가
    df_load['source_file'] = source_file
    df_load['trade_date'] = trade_date

    # PostgreSQL 로드
    hook = PostgresHook(postgres_conn_id=conn_id)
    engine = hook.get_sqlalchemy_engine()

    df_load.to_sql(
        name=table,
        schema='stock',
        con=engine,
        if_exists='append',
        index=False,
    )

    return len(df_load)


def load_daily_price_bronze(df: pd.DataFrame, source_file: str, trade_date: str, **context) -> int:
    """시세 데이터를 Bronze 테이블에 로드"""
    return load_to_bronze(
        df=df,
        table='bronze_daily_price',
        column_map=DAILY_PRICE_COLUMN_MAP,
        source_file=source_file,
        trade_date=trade_date,
    )


def load_valuation_bronze(df: pd.DataFrame, source_file: str, trade_date: str, **context) -> int:
    """PER/PBR 데이터를 Bronze 테이블에 로드"""
    return load_to_bronze(
        df=df,
        table='bronze_valuation',
        column_map=VALUATION_COLUMN_MAP,
        source_file=source_file,
        trade_date=trade_date,
    )


def load_to_bronze_task(**context):
    """
    Airflow Task: Bronze 테이블에 로드 (ELT용)
    """
    ti = context['ti']

    # XCom에서 데이터 가져오기
    stock_json = ti.xcom_pull(key='stock_data')
    pbr_json = ti.xcom_pull(key='pbr_data')

    stock_df = pd.read_json(stock_json)
    pbr_df = pd.read_json(pbr_json)

    # 파일 경로 및 거래일 가져오기
    market_file = ti.xcom_pull(key='market_file') or 'unknown'
    per_file = ti.xcom_pull(key='per_file') or 'unknown'
    market_trade_date = ti.xcom_pull(key='market_trade_date')
    per_trade_date = ti.xcom_pull(key='per_trade_date')

    # Bronze 로드
    daily_count = load_daily_price_bronze(stock_df, market_file, market_trade_date)
    valuation_count = load_valuation_bronze(pbr_df, per_file, per_trade_date)

    return {
        'daily_price_rows': daily_count,
        'valuation_rows': valuation_count,
        'market_trade_date': market_trade_date,
        'per_trade_date': per_trade_date,
    }


def load_to_silver_task(**context):
    """
    Airflow Task: Silver 테이블에 로드 (ETL용, transform 후)
    """
    ti = context['ti']

    # XCom에서 변환된 데이터 가져오기
    merged_json = ti.xcom_pull(key='merged_data')
    trade_date = ti.xcom_pull(key='trade_date')

    merged_df = pd.read_json(merged_json)

    # 컬럼명 매핑 (한글 → 영문)
    column_map = {
        '종목코드': 'stock_code',
        '종목명': 'stock_name',
        '종가': 'close_price',
        '대비': 'change_amount',
        '등락률': 'change_rate',
        '시가': 'open_price',
        '고가': 'high_price',
        '저가': 'low_price',
        '거래량': 'volume',
        '거래대금': 'trade_value',
        '시가총액': 'market_cap',
        '상장주식수': 'shares_outstanding',
        'EPS': 'eps',
        'PER': 'per',
        '선행 EPS': 'forward_eps',
        '선행 PER': 'forward_per',
        'BPS': 'bps',
        'PBR': 'pbr',
        '배당수익률': 'dividend_yield',
    }

    # 매핑에 있는 컬럼만 선택 (존재하는 컬럼만)
    valid_korean_columns = [col for col in column_map.keys() if col in merged_df.columns]
    merged_df = merged_df[valid_korean_columns].copy()

    # 컬럼명 변환
    merged_df = merged_df.rename(columns=column_map)

    # trade_date 추가
    merged_df['trade_date'] = trade_date

    # 숫자 컬럼 변환 ('-' → NULL)
    numeric_columns = ['eps', 'per', 'forward_eps', 'forward_per', 'bps', 'pbr', 'dividend_yield']
    for col in numeric_columns:
        if col in merged_df.columns:
            merged_df[col] = pd.to_numeric(merged_df[col], errors='coerce')

    hook = PostgresHook(postgres_conn_id='postgres_default')
    engine = hook.get_sqlalchemy_engine()

    # Silver 테이블에 저장
    merged_df.to_sql(
        name='silver_daily_price',
        schema='stock',
        con=engine,
        if_exists='append',
        index=False,
    )

    return {'rows': len(merged_df), 'trade_date': trade_date}
