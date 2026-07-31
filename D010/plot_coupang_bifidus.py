import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

SRC = "D009/outputs/coupang_bifidus_final.csv"
OUT_DIR = "D009/outputs"

df = pd.read_csv(SRC)
df["log_review"] = np.log(df["review_count"] + 1)

sns.set_style("whitegrid")
plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

# 1. 산점도: x=unit_price, y=rating, 크기=log(review_count+1)
fig, ax = plt.subplots(figsize=(8, 6))
sizes = df["log_review"] * 40 + 20
ax.scatter(
    df["unit_price"], df["rating"],
    s=sizes, color="#2b6cb0", alpha=0.55, edgecolors="white", linewidths=0.6,
)
ax.set_xlabel("단가 (unit_price, 원)")
ax.set_ylabel("평점 (rating)")
ax.set_title("단가 vs 평점 (점 크기 = log(리뷰수+1))")

# 점 크기 범례 (리뷰수 기준 3개 예시)
for review_ref, label in [(10, "리뷰 10개"), (1000, "리뷰 1,000개"), (50000, "리뷰 50,000개")]:
    s = np.log(review_ref + 1) * 40 + 20
    ax.scatter([], [], s=s, color="#2b6cb0", alpha=0.55, edgecolors="white", linewidths=0.6, label=label)
ax.legend(title="리뷰수", loc="lower right", frameon=True)

fig.tight_layout()
fig.savefig(f"{OUT_DIR}/scatter_unitprice_rating.png", dpi=150)
plt.close(fig)

# 2. 박스플롯: unit_price 4구간별 rating 분포
labels = ["저가", "중저가", "중고가", "고가"]
df["price_tier"] = pd.qcut(df["unit_price"], q=4, labels=labels)

palette = {"저가": "#c6dbef", "중저가": "#6baed6", "중고가": "#3182bd", "고가": "#08519c"}

fig, ax = plt.subplots(figsize=(7, 6))
sns.boxplot(
    data=df, x="price_tier", y="rating", order=labels,
    hue="price_tier", palette=palette, legend=False, ax=ax,
)
ax.set_xlabel("단가 구간 (price_tier)")
ax.set_ylabel("평점 (rating)")
ax.set_title("단가 구간별 평점 분포")

fig.tight_layout()
fig.savefig(f"{OUT_DIR}/boxplot_unitprice_tier_rating.png", dpi=150)
plt.close(fig)

# 3. 히스토그램 2개: unit_price 분포, rating 분포
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

sns.histplot(df["unit_price"], bins=15, color="#2b6cb0", ax=axes[0])
axes[0].set_xlabel("단가 (unit_price, 원)")
axes[0].set_ylabel("상품 수")
axes[0].set_title("단가(unit_price) 분포")

sns.histplot(df["rating"], bins=10, color="#c05621", ax=axes[1])
axes[1].set_xlabel("평점 (rating)")
axes[1].set_ylabel("상품 수")
axes[1].set_title("평점(rating) 분포")

fig.tight_layout()
fig.savefig(f"{OUT_DIR}/hist_unitprice_rating.png", dpi=150)
plt.close(fig)

price_tier_counts = df["price_tier"].value_counts().reindex(labels)
with open(f"{OUT_DIR}/plot_log.txt", "w", encoding="utf-8") as f:
    f.write("=== price_tier 구간 경계 및 건수 ===\n")
    f.write(str(pd.qcut(df["unit_price"], q=4).cat.categories) + "\n")
    f.write(price_tier_counts.to_string() + "\n")

print("DONE")
