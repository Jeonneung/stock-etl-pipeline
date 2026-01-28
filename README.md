# Stock Data ETL Pipeline

KRX(한국거래소) 주식 데이터를 수집하고 분석하기 위한 ETL 파이프라인입니다.
Apache Airflow + PostgreSQL + Docker 기반으로 구성되어 있습니다.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        File Upload                               │
│           (전종목시세_YYYYMMDD.xlsx, PER:PBR_YYYYMMDD.xlsx)        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Apache Airflow                               │
│  ┌──────────┐   ┌──────────┐   ┌───────────┐   ┌────────────┐  │
│  │  Sensor  │ → │ Extract  │ → │ Transform │ → │    Load    │  │
│  │(30s poll)│   │(read xlsx)│   │  (merge)  │   │ (to Silver)│  │
│  └──────────┘   └──────────┘   └───────────┘   └────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       PostgreSQL                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    stock schema                          │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────────────┐ │   │
│  │  │   Bronze   │  │   Silver   │  │        Gold        │ │   │
│  │  │  (raw txt) │  │  (cleaned) │  │     (analysis)     │ │   │
│  │  └────────────┘  └────────────┘  └────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Features

- **파일 기반 트리거**: 엑셀 파일 업로드 시 자동으로 파이프라인 실행
- **Medallion Architecture**: Bronze(원본) → Silver(정제) → Gold(분석) 레이어
- **시계열 데이터 지원**: 파일명에서 거래일 추출하여 저장
- **자동 파일 정리**: 처리 완료된 파일은 `processed/` 폴더로 이동

## Tech Stack

- **Orchestration**: Apache Airflow 2.10.4
- **Database**: PostgreSQL 13
- **Container**: Docker, Docker Compose
- **Language**: Python 3.12

## Project Structure

```
.
├── dags/
│   ├── etl.py              # ETL DAG 정의
│   └── utils/
│       ├── extract.py      # 데이터 추출 (Excel → DataFrame)
│       ├── transform.py    # 데이터 변환 (병합, 정리)
│       ├── load.py         # 데이터 적재 (DataFrame → PostgreSQL)
│       └── file_watcher.py # 파일 감시 유틸리티
├── data/
│   ├── marketPrice/        # 시세 데이터 업로드 위치
│   └── perData/            # PER/PBR 데이터 업로드 위치
├── scripts/                # 분석 스크립트
├── docker-compose.yaml     # Docker 설정
├── init.sql                # DB 스키마 초기화
└── .env.example            # 환경변수 템플릿
```

## Quick Start

### 1. 환경 설정

```bash
# 환경변수 파일 생성
cp .env.example .env

# 필요시 .env 파일 수정 (AIRFLOW_UID 등)
```

### 2. 서비스 시작

```bash
docker compose up -d
```

### 3. Airflow 접속

- URL: http://localhost:8080
- ID/PW: airflow / airflow

### 4. 데이터 업로드

엑셀 파일을 아래 경로에 복사:
- 시세 데이터: `data/marketPrice/전종목시세_YYYYMMDD.xlsx`
- PER/PBR: `data/perData/PER:PBR:배당수익률_YYYYMMDD.xlsx`

파일 감지 후 자동으로 ETL 파이프라인이 실행됩니다.

## Database Schema

### Silver Layer (주요 테이블)

```sql
stock.silver_daily_price
├── stock_code       -- 종목코드
├── stock_name       -- 종목명
├── close_price      -- 종가
├── change_rate      -- 등락률
├── volume           -- 거래량
├── market_cap       -- 시가총액
├── eps, per         -- 주당순이익, PER
├── bps, pbr         -- 주당순자산, PBR
├── dividend_yield   -- 배당수익률
└── trade_date       -- 거래일
```

## Configuration

### Airflow 연결 설정

서비스 시작 후 PostgreSQL 연결 추가:

```bash
docker compose exec airflow-webserver airflow connections add 'postgres_default' \
    --conn-type 'postgres' \
    --conn-host 'postgres' \
    --conn-schema 'airflow' \
    --conn-login 'airflow' \
    --conn-password 'airflow' \
    --conn-port '5432'
```

## License

MIT License
