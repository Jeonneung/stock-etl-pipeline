import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# matplotlib 한글 폰트 설정
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

# PostgreSQL 접속
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
df = pd.read_sql(query, conn)
conn.close()

if df.empty:
    print("데이터가 없습니다. DB를 확인하세요.")
    exit()

# 종목별 누적 수익률 계산
results = []
for name, group in df.groupby("stock_name"):
    group = group.sort_values("trade_date").reset_index(drop=True)
    # 첫날은 시가→종가, 이후는 전일 종가→당일 종가
    daily_returns = []
    for i, row in group.iterrows():
        if i == 0:
            daily_ret = (row["close_price"] - row["open_price"]) / row["open_price"]
        else:
            prev_close = group.loc[i - 1, "close_price"]
            daily_ret = (row["close_price"] - prev_close) / prev_close
        daily_returns.append(daily_ret)

    cum_ret = 1.0
    for i, row in group.iterrows():
        cum_ret *= (1 + daily_returns[i])
        results.append({
            "stock_name": name,
            "trade_date": row["trade_date"],
            "daily_return": daily_returns[i] * 100,
            "cumulative_return": (cum_ret - 1) * 100,
        })

result = pd.DataFrame(results)

# 테이블 출력
print("=" * 70)
print("  종목별 일간 수익률 및 누적 수익률 (1/26 시가 매수 기준)")
print("=" * 70)
for name, group in result.groupby("stock_name"):
    print(f"\n▶ {name}")
    print(f"  {'날짜':>12}  {'일간 수익률':>10}  {'누적 수익률':>10}")
    print(f"  {'-'*12}  {'-'*10}  {'-'*10}")
    for _, row in group.iterrows():
        d = row['trade_date'].strftime('%Y-%m-%d') if hasattr(row['trade_date'], 'strftime') else str(row['trade_date'])
        print(f"  {d:>12}  {row['daily_return']:>+9.2f}%  {row['cumulative_return']:>+9.2f}%")
print()

# 그래프
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

colors = {"롯데쇼핑": "#E74C3C", "KG에코솔루션": "#2E86C1"}

# 왼쪽: 누적 수익률
for name, group in result.groupby("stock_name"):
    ax1.plot(group["trade_date"], group["cumulative_return"],
             marker="o", linewidth=2, color=colors[name], label=name)
    for _, row in group.iterrows():
        ax1.annotate(f'{row["cumulative_return"]:.2f}%',
                     (row["trade_date"], row["cumulative_return"]),
                     textcoords="offset points", xytext=(0, 10),
                     ha="center", fontsize=9)

ax1.set_title("누적 수익률 추이 (1/26 시가 매수 기준)", fontsize=14)
ax1.set_xlabel("날짜")
ax1.set_ylabel("누적 수익률 (%)")
ax1.axhline(y=0, color="gray", linestyle="--", linewidth=0.8)
ax1.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))
ax1.legend(fontsize=11)
ax1.grid(True, alpha=0.3)

# 오른쪽: 일간 수익률 (막대 그래프)
dates = result["trade_date"].unique()
x = range(len(dates))
width = 0.35

for idx, (name, group) in enumerate(result.groupby("stock_name")):
    offset = -width / 2 + idx * width
    bars = ax2.bar([i + offset for i in x], group["daily_return"].values,
                   width=width, label=name, color=colors[name], alpha=0.8)
    for bar in bars:
        h = bar.get_height()
        ax2.annotate(f'{h:.2f}%',
                     xy=(bar.get_x() + bar.get_width() / 2, h),
                     xytext=(0, 5 if h >= 0 else -12),
                     textcoords="offset points", ha="center", fontsize=9)

ax2.set_title("일간 수익률 비교", fontsize=14)
ax2.set_xlabel("날짜")
ax2.set_ylabel("일간 수익률 (%)")
ax2.set_xticks(list(x))
ax2.set_xticklabels([d.strftime("%m/%d") if hasattr(d, 'strftime') else str(d) for d in dates])
ax2.axhline(y=0, color="gray", linestyle="--", linewidth=0.8)
ax2.legend(fontsize=11)
ax2.grid(True, alpha=0.3, axis="y")

plt.tight_layout()
plt.savefig("cumulative_return.png", dpi=150)
plt.show()

print("차트 저장 완료: cumulative_return.png")
