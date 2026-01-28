from datetime import datetime, timedelta

from airflow import DAG
from airflow.sensors.python import PythonSensor
from airflow.operators.python import PythonOperator

from utils.file_watcher import (
    check_files,
    move_to_processed,
    MARKET_PRICE_DIR,
    PER_DATA_DIR,
    MARKET_PRICE_PATTERN,
    PER_DATA_PATTERN,
)
from utils.extract import extract
from utils.transform import transform
from utils.load import load_to_silver_task


def cleanup_files(**context):
    """처리 완료된 파일을 processed 폴더로 이동"""
    ti = context['ti']
    market_files = ti.xcom_pull(key='marketPrice_files') or []
    per_files = ti.xcom_pull(key='perData_files') or []

    if market_files:
        move_to_processed(market_files, MARKET_PRICE_DIR)
    if per_files:
        move_to_processed(per_files, PER_DATA_DIR)


with DAG(
    dag_id='stock_etl',
    description='주식 데이터 ETL 파이프라인',
    start_date=datetime(2026, 1, 1),
    schedule_interval='@hourly',  # 매시간 실행 (백업용)
    catchup=False,
    max_active_runs=1,  # 동시 실행 방지
    default_args={
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    },
) as dag:

    # 1. 파일 감시 (병렬, reschedule 모드)
    wait_market_price = PythonSensor(
        task_id='wait_market_price_file',
        python_callable=check_files,
        op_kwargs={
            'directory': MARKET_PRICE_DIR,
            'pattern': MARKET_PRICE_PATTERN,
        },
        poke_interval=30,  # 30초마다 체크
        timeout=60 * 55,   # 55분 (hourly 스케줄 내)
        mode='reschedule',  # worker 점유 안 함
        soft_fail=True,     # 타임아웃 시 skip (fail 아님)
    )

    wait_per_data = PythonSensor(
        task_id='wait_per_data_file',
        python_callable=check_files,
        op_kwargs={
            'directory': PER_DATA_DIR,
            'pattern': PER_DATA_PATTERN,
        },
        poke_interval=30,
        timeout=60 * 55,
        mode='reschedule',
        soft_fail=True,
    )

    # 2. Extract: 데이터 읽기
    extract_task = PythonOperator(
        task_id='extract',
        python_callable=extract,
    )

    # 3. Transform: 병합 및 정리
    transform_task = PythonOperator(
        task_id='transform',
        python_callable=transform,
    )

    # 4. Load: Silver/Gold 테이블에 저장
    load_task = PythonOperator(
        task_id='load',
        python_callable=load_to_silver_task,
    )

    # 5. Cleanup: 처리 완료 파일 이동
    cleanup_task = PythonOperator(
        task_id='cleanup_files',
        python_callable=cleanup_files,
    )

    # 그래프 연결
    [wait_market_price, wait_per_data] >> extract_task >> transform_task >> load_task >> cleanup_task