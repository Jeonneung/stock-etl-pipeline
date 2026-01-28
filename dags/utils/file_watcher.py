import os
import glob
import shutil
from typing import List

# 감시할 디렉토리
MARKET_PRICE_DIR = '/opt/airflow/data/marketPrice'
PER_DATA_DIR = '/opt/airflow/data/perData'

# 처리 완료 디렉토리
PROCESSED_BASE_DIR = '/opt/airflow/data/processed'
PROCESSED_MARKET_PRICE_DIR = f'{PROCESSED_BASE_DIR}/marketPrice'
PROCESSED_PER_DATA_DIR = f'{PROCESSED_BASE_DIR}/perData'

# 특정 파일명 패턴 (예: 전종목시세_20260128.xlsx)
MARKET_PRICE_PATTERN = '전종목시세_*.xlsx'
PER_DATA_PATTERN = 'PER:PBR:배당수익률_*.xlsx'


def check_files(directory: str, pattern: str, **context) -> bool:
    """
    디렉토리 내 파일 존재 여부 확인
    1. 패턴 매칭 시도
    2. fallback - 아무 xlsx 파일

    Args:
        directory: 감시할 디렉토리 경로
        pattern: 파일명 패턴 (glob)
        context: Airflow context (ti 포함)

    Returns:
        파일 존재 여부
    """
    # 패턴 매칭 시도
    pattern_path = os.path.join(directory, pattern)
    matched_files = glob.glob(pattern_path)

    if matched_files:
        context['ti'].xcom_push(key=f'{os.path.basename(directory)}_files', value=matched_files)
        return True

    # fallback - 아무 xlsx 파일
    fallback_path = os.path.join(directory, '*.xlsx')
    fallback_files = glob.glob(fallback_path)

    if fallback_files:
        context['ti'].xcom_push(key=f'{os.path.basename(directory)}_files', value=fallback_files)
        return True

    return False


def move_to_processed(files: List[str], source_dir: str) -> List[str]:
    """
    처리 완료된 파일을 processed 디렉토리로 이동

    Args:
        files: 이동할 파일 경로 리스트
        source_dir: 원본 디렉토리 (MARKET_PRICE_DIR 또는 PER_DATA_DIR)

    Returns:
        이동된 파일 경로 리스트
    """
    # source_dir에 따라 목적지 결정
    if source_dir == MARKET_PRICE_DIR:
        dest_dir = PROCESSED_MARKET_PRICE_DIR
    elif source_dir == PER_DATA_DIR:
        dest_dir = PROCESSED_PER_DATA_DIR
    else:
        dest_dir = f'{PROCESSED_BASE_DIR}/{os.path.basename(source_dir)}'

    # 목적지 디렉토리 생성
    os.makedirs(dest_dir, exist_ok=True)

    moved_files = []
    for file_path in files:
        filename = os.path.basename(file_path)
        dest_path = os.path.join(dest_dir, filename)
        shutil.move(file_path, dest_path)
        moved_files.append(dest_path)

    return moved_files
