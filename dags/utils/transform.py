import pandas as pd


def merge_stock_data(stock_df: pd.DataFrame, pbr_df: pd.DataFrame) -> pd.DataFrame:
    """
    시세 데이터와 PBR 데이터를 종목코드 기준으로 병합

    Args:
        stock_df: 시세 데이터
        pbr_df: PER/PBR 데이터

    Returns:
        병합된 DataFrame
    """
    merged = pd.merge(stock_df, pbr_df, how='right', on='종목코드')

    # 중복 컬럼 제거
    drop_columns = ['종목명_y', '종가_y', '대비_y', '등락률_y']
    merged.drop(columns=drop_columns, inplace=True)

    # 컬럼명 정리
    merged.rename(columns={
        '종목명_x': '종목명',
        '종가_x': '종가',
        '대비_x': '대비',
        '등락률_x': '등락률',
    }, inplace=True)

    return merged


def transform(**context):
    """
    Transform: 데이터 병합 및 정리 (ETL용)
    """
    ti = context['ti']

    # XCom에서 데이터 가져오기
    stock_json = ti.xcom_pull(key='stock_data')
    pbr_json = ti.xcom_pull(key='pbr_data')
    trade_date = ti.xcom_pull(key='market_trade_date')

    stock_df = pd.read_json(stock_json)
    pbr_df = pd.read_json(pbr_json)

    # 병합
    merged = merge_stock_data(stock_df, pbr_df)

    # 다음 태스크로 전달
    ti.xcom_push(key='merged_data', value=merged.to_json())
    ti.xcom_push(key='trade_date', value=trade_date)

    return {'rows': len(merged), 'trade_date': trade_date}
