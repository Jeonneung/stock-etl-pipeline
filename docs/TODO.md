# TODO

## 데이터 리소스 교체: yfinance -> FMP (Financial Modeling Prep)

### 배경
- 현재 rally_analyze에서 yfinance를 사용 중이나, 상장폐지 종목 데이터를 가져올 수 없어 survivorship bias 존재
- YHOO, SUNW, CMGI 등 닷컴 버블 핵심 종목이 분석에서 누락됨

### FMP 전환 시 이점
- `/delisted-company-list` 엔드포인트로 상장폐지 종목 커버 가능
- Full historical stock list로 특정 시점 상장 종목 조회 가능
- Bulk 엔드포인트로 대량 다운로드 안정적
- 공식 REST API (스크래핑 기반이 아님)

### 필요 사항
- [ ] FMP Free 플랜으로 delisted endpoint 및 1988년대 historical data 범위 테스트
- [ ] 플랜 결정 (최소 Starter $29/mo, 일 10,000건 이상 필요)
- [ ] rally_analyze.ipynb의 데이터 수집 코드를 FMP API로 교체
- [ ] 상장폐지 종목 포함한 전체 티커 목록 구성
- [ ] 데이터 로컬 저장 (과금 최소화)
