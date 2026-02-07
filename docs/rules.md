# 프로젝트 규칙

## 파일명 규칙

### 노트북 파일

```
{기간}_{분석유형}_{데이터소스}_v{버전}_{용도}.ipynb
```

| 요소 | 설명 | 예시 |
|------|------|------|
| 기간 | 분석 대상 랠리/시기 | `dotcom`, `bigtech`, `ai` |
| 분석유형 | 분석 종류 | `rally`, `sector`, `rs` |
| 데이터소스 | 데이터 출처 | `yfinance`, `fmp` |
| 버전 | 연구 버전 | `v1`, `v2` |
| 용도 (선택) | 파일 용도 | `clean` (포트폴리오용), 생략시 작업용 |

### 예시

| 파일명 | 설명 |
|--------|------|
| `dotcom_rally_yfinance_v1.ipynb` | 닷컴 버블 랠리 분석, yfinance, 1차, 작업용 |
| `dotcom_rally_yfinance_v1_clean.ipynb` | 닷컴 버블 랠리 분석, yfinance, 1차, 포트폴리오용 |
| `dotcom_rally_fmp_v1.ipynb` | 닷컴 버블 랠리 분석, FMP, 1차, 작업용 |
| `bigtech_rally_yfinance_v1.ipynb` | 빅테크 랠리 (2009~2021) 분석, yfinance, 1차 |
| `ai_rally_fmp_v1.ipynb` | AI 랠리 분석, FMP, 1차 |

### 디렉토리 구조

```
analyze/
├── docs/
│   ├── rules.md          # 프로젝트 규칙
│   └── TODO.md           # 할 일 목록
├── labs/
│   ├── dotcom_rally_*.ipynb
│   ├── bigtech_rally_*.ipynb
│   └── ai_rally_*.ipynb
└── data/                 # 로컬 데이터 저장 (추후)
```
