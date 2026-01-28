-- 스키마 생성
CREATE SCHEMA IF NOT EXISTS stock;

-- =====================
-- BRONZE LAYER (원본 보장, 전부 TEXT)
-- =====================

-- Bronze: 일별 시세 원본
CREATE TABLE IF NOT EXISTS stock.bronze_daily_price (
    id SERIAL PRIMARY KEY,
    stock_code TEXT,
    stock_name TEXT,
    close_price TEXT,
    change_amount TEXT,
    change_rate TEXT,
    open_price TEXT,
    high_price TEXT,
    low_price TEXT,
    volume TEXT,
    trade_value TEXT,
    market_cap TEXT,
    shares_outstanding TEXT,
    trade_date DATE,
    source_file TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bronze: PER/PBR 원본
CREATE TABLE IF NOT EXISTS stock.bronze_valuation (
    id SERIAL PRIMARY KEY,
    stock_code TEXT,
    stock_name TEXT,
    close_price TEXT,
    change_amount TEXT,
    change_rate TEXT,
    eps TEXT,
    per TEXT,
    forward_eps TEXT,
    forward_per TEXT,
    bps TEXT,
    pbr TEXT,
    dividend_yield TEXT,
    trade_date DATE,
    source_file TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================
-- SILVER LAYER (클렌징, 타입 변환)
-- =====================

-- Silver: 일별 시세 + 밸류에이션 통합 정제
CREATE TABLE IF NOT EXISTS stock.silver_daily_price (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(20) NOT NULL,
    stock_name VARCHAR(100),
    close_price BIGINT,
    change_amount BIGINT,
    change_rate DECIMAL(10, 2),
    open_price BIGINT,
    high_price BIGINT,
    low_price BIGINT,
    volume BIGINT,
    trade_value BIGINT,
    market_cap BIGINT,
    shares_outstanding BIGINT,
    eps DECIMAL(15, 2),
    per DECIMAL(10, 2),
    forward_eps DECIMAL(15, 2),
    forward_per DECIMAL(10, 2),
    bps DECIMAL(15, 2),
    pbr DECIMAL(10, 2),
    dividend_yield DECIMAL(10, 2),
    trade_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stock_code, trade_date)
);

-- Silver: PER/PBR 정제
CREATE TABLE IF NOT EXISTS stock.silver_valuation (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(20) NOT NULL,
    stock_name VARCHAR(100),
    close_price BIGINT,
    eps DECIMAL(15, 2),
    per DECIMAL(10, 2),
    forward_eps DECIMAL(15, 2),
    forward_per DECIMAL(10, 2),
    bps DECIMAL(15, 2),
    pbr DECIMAL(10, 2),
    dividend_yield DECIMAL(10, 2),
    trade_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stock_code, trade_date)
);

-- =====================
-- GOLD LAYER (분석 결과)
-- =====================

-- Gold: 분석 결과
CREATE TABLE IF NOT EXISTS stock.gold_analysis (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(20) NOT NULL,
    stock_name VARCHAR(100),
    close_price BIGINT,
    bps DECIMAL(15, 2),
    pbr DECIMAL(10, 2),
    target_price DECIMAL(15, 2),
    downside_support DECIMAL(15, 2),
    upside_potential DECIMAL(10, 2),
    risk_reward_ratio DECIMAL(10, 2),
    analysis_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stock_code, analysis_date)
);

-- =====================
-- INDEXES
-- =====================

-- Bronze indexes
CREATE INDEX IF NOT EXISTS idx_bronze_daily_price_source ON stock.bronze_daily_price(source_file);
CREATE INDEX IF NOT EXISTS idx_bronze_daily_price_trade_date ON stock.bronze_daily_price(trade_date);
CREATE INDEX IF NOT EXISTS idx_bronze_valuation_source ON stock.bronze_valuation(source_file);
CREATE INDEX IF NOT EXISTS idx_bronze_valuation_trade_date ON stock.bronze_valuation(trade_date);

-- Silver indexes
CREATE INDEX IF NOT EXISTS idx_silver_daily_price_date ON stock.silver_daily_price(trade_date);
CREATE INDEX IF NOT EXISTS idx_silver_daily_price_code ON stock.silver_daily_price(stock_code);
CREATE INDEX IF NOT EXISTS idx_silver_valuation_date ON stock.silver_valuation(trade_date);
CREATE INDEX IF NOT EXISTS idx_silver_valuation_code ON stock.silver_valuation(stock_code);

-- Gold indexes
CREATE INDEX IF NOT EXISTS idx_gold_analysis_date ON stock.gold_analysis(analysis_date);
CREATE INDEX IF NOT EXISTS idx_gold_analysis_code ON stock.gold_analysis(stock_code);
