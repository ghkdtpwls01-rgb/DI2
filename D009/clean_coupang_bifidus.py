import pandas as pd

SRC = "D009/outputs/coupang_bifidus_products.csv"
DST = "D009/outputs/coupang_bifidus_cleaned.csv"
LOG = "D009/outputs/clean_log.txt"

lines = []
def log(*args):
    s = " ".join(str(a) for a in args)
    lines.append(s)

df = pd.read_csv(SRC)
before_count = len(df)

log("=== 1. 정제 전 dtypes ===")
log(df.dtypes.to_string())

for col in ["price_krw", "rating", "review_count"]:
    if not pd.api.types.is_numeric_dtype(df[col]):
        df[col] = pd.to_numeric(df[col], errors="coerce")
        log(f"-> {col} 숫자형으로 변환")

log()
log("=== 1. 변환 후 dtypes ===")
log(df.dtypes.to_string())

log()
log("=== 2. rating 결측치 행 제거 ===")
missing_rating_rows = df[df["rating"].isna()]
log("제거 대상 (rating 결측):")
log(missing_rating_rows[["product_id", "name", "rating", "review_count"]].to_string(index=False))
df = df[df["rating"].notna()].copy()

log()
log("=== 3. name 앞뒤 공백 제거 및 중복 확인 ===")
before_strip = df["name"].copy()
df["name"] = df["name"].str.strip()
changed = (before_strip != df["name"]).sum()
log(f"공백 제거로 변경된 행 수: {changed}")

dup_mask = df["name"].duplicated(keep=False)
dup_names = df.loc[dup_mask, ["product_id", "name", "price_krw"]].sort_values("name")
log(f"중복 상품명 행 수: {dup_mask.sum()}")
if dup_mask.sum() > 0:
    log(dup_names.to_string(index=False))
else:
    log("중복 상품명 없음")

log()
log("=== 4. 가격 상위 5개 상품 ===")
top_price = df.sort_values("price_krw", ascending=False).head(5)[["name", "price_krw", "rating", "review_count"]]
log(top_price.to_string(index=False))

log()
log("=== 4. 리뷰수 상위 5개 상품 ===")
top_review = df.sort_values("review_count", ascending=False).head(5)[["name", "price_krw", "rating", "review_count"]]
log(top_review.to_string(index=False))

after_count = len(df)
log()
log("=== 5. 정제 전후 행 수 비교 ===")
log(f"정제 전: {before_count}행")
log(f"정제 후: {after_count}행")
log(f"제거된 행: {before_count - after_count}행 (rating 결측)")

df.to_csv(DST, index=False, encoding="utf-8-sig")
log()
log(f"=== 6. 저장 완료: {DST} ({after_count}행) ===")

with open(LOG, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("DONE")
