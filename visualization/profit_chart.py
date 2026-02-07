import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import date

# matplotlib 한글 폰트 설정
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

DATA_DIR = "/Users/buildingbite/analyze/data"
DATES = ["20260126", "20260127", "20260128", "20260129"]

# ── 1. 종목 데이터 (DB) ──
conn = psycopg2.connect(
    host="localhost", port=5432,
    database="airflow", user="airflow", password="airflow",
)

query = """
SELECT stock_name, trade_date, open_price, close_price
FROM stock.silver_daily_price
WHERE stock_name IN ('롯데쇼핑', 'KG에코솔루션')
  AND trade_date BETWEEN '2026-01-26' AND '2026-01-29'
ORDER BY stock_name, trade_date
"""
df_stock = pd.read_sql(query, conn)
conn.close()

if df_stock.empty:
    print("종목 데이터가 없습니다. DB를 확인하세요.")
    exit()

# 종목별 수익률 (1/26 시가 매수 → 각 날짜 종가 기준)
stock_records = []
for name, group in df_stock.groupby("stock_name"):
    group = group.sort_values("trade_date").reset_index(drop=True)
    buy_price = group.loc[0, "open_price"]
    for _, row in group.iterrows():
        stock_records.append({
            "name": name,
            "trade_date": row["trade_date"],
            "return_pct": (row["close_price"] - buy_price) / buy_price * 100,
        })

df_stock_ret = pd.DataFrame(stock_records)

# ── 2. 지수 데이터 (엑셀) ──
index_records = []
for market, index_name in [("kospi", "코스피"), ("kosdaq", "코스닥")]:
    for d in DATES:
        fpath = f"{DATA_DIR}/{market}/{market}_{d}.xlsx"
        df = pd.read_excel(fpath)
        row = df[df["지수명"] == index_name].iloc[0]
        index_records.append({
            "name": index_name,
            "trade_date": date(int(d[:4]), int(d[4:6]), int(d[6:])),
            "open_price": float(row["시가"]),
            "close_price": float(row["종가"]),
        })

df_index = pd.DataFrame(index_records)

# 지수 수익률 (1/26 시가 기준)
index_ret_records = []
for name, group in df_index.groupby("name"):
    group = group.sort_values("trade_date").reset_index(drop=True)
    buy_price = group.loc[0, "open_price"]
    for _, row in group.iterrows():
        index_ret_records.append({
            "name": name,
            "trade_date": row["trade_date"],
            "return_pct": (row["close_price"] - buy_price) / buy_price * 100,
        })

df_index_ret = pd.DataFrame(index_ret_records)

# ── 3. 전체 수익률 합치기 ──
df_all = pd.concat([df_stock_ret, df_index_ret], ignore_index=True)

# ── 4. 그래프 그리기 (2개 서브플롯) ──
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))

# --- 상단: 수익률 추이 ---
styles = {
    "롯데쇼핑":     {"color": "#E74C3C", "linestyle": "-"},
    "KG에코솔루션":  {"color": "#2E86C1", "linestyle": "-"},
    "코스피":       {"color": "#888888", "linestyle": "--"},
    "코스닥":       {"color": "#AAAAAA", "linestyle": "--"},
}

for name, group in df_all.groupby("name"):
    s = styles.get(name, {})
    ax1.plot(group["trade_date"], group["return_pct"],
             marker="o", linewidth=2, label=name, **s)
    for _, row in group.iterrows():
        ax1.annotate(f'{row["return_pct"]:.2f}%',
                     (row["trade_date"], row["return_pct"]),
                     textcoords="offset points", xytext=(0, 10),
                     ha="center", fontsize=8)

ax1.set_title("1월 26일 시가 매수 기준 수익률 추이 (1/26 ~ 1/29)", fontsize=14)
ax1.set_ylabel("수익률 (%)")
ax1.axhline(y=0, color="gray", linestyle="--", linewidth=0.8)
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3)

# --- 하단: 지수 대비 초과수익률 ---
# 롯데쇼핑은 코스피 상장, KG에코솔루션은 코스닥 상장
benchmarks = {"롯데쇼핑": "코스피", "KG에코솔루션": "코스닥"}

for stock_name, bench_name in benchmarks.items():
    sr = df_stock_ret[df_stock_ret["name"] == stock_name].set_index("trade_date")["return_pct"]
    br = df_index_ret[df_index_ret["name"] == bench_name].set_index("trade_date")["return_pct"]
    excess = (sr - br).reset_index()
    excess.columns = ["trade_date", "excess_pct"]

    s = styles.get(stock_name, {})
    ax2.plot(excess["trade_date"], excess["excess_pct"],
             marker="s", linewidth=2,
             label=f"{stock_name} vs {bench_name}", color=s.get("color"))
    for _, row in excess.iterrows():
        ax2.annotate(f'{row["excess_pct"]:.2f}%p',
                     (row["trade_date"], row["excess_pct"]),
                     textcoords="offset points", xytext=(0, 10),
                     ha="center", fontsize=8)

ax2.set_title("지수 대비 초과수익률 (1/26 ~ 1/29)", fontsize=14)
ax2.set_xlabel("날짜")
ax2.set_ylabel("초과수익률 (%p)")
ax2.axhline(y=0, color="gray", linestyle="--", linewidth=0.8)
ax2.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))
ax2.legend(fontsize=10)
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("profit_chart.png", dpi=150)
plt.show()

print("차트 저장 완료: profit_chart.png")
