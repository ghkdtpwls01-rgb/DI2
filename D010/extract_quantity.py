import re

import pandas as pd

SRC = "D009/outputs/coupang_bifidus_cleaned.csv"
DST = "D009/outputs/coupang_bifidus_cleaned.csv"
LOG = "D009/outputs/quantity_log.txt"

# 콤마/공백/문자열 시작-끝으로 둘러싸인 "N개" 또는 "N박스"만 매칭 -> "125ml(8입)x6개"의 6개,
# "1개월"의 1개 같은 오탐은 배제, "..., 3개, ..." / "...30정 2개..." / "..., 7박스, ..." 같은
# 진짜 수량 표기만 추출. "세트"는 패턴에 포함하지 않음 -> "1세트"는 기본값(1)으로 처리.
QTY_PATTERN = re.compile(r'(?:(?<=^)|(?<=[,\s]))(\d+)(?:개|박스)(?=[,\s]|$)')

lines = []
def log(*a):
    lines.append(" ".join(str(x) for x in a))

df = pd.read_csv(SRC)

def extract_qty(name):
    matches = QTY_PATTERN.findall(name)
    if not matches:
        return 1, 0
    return int(matches[-1]), len(matches)

qty_matches = df["name"].apply(extract_qty)
df["quantity"] = qty_matches.apply(lambda t: t[0])
match_count = qty_matches.apply(lambda t: t[1])

df["unit_price"] = df["price_krw"] / df["quantity"]

log("=== 3. quantity 값 분포 ===")
log(df["quantity"].value_counts().sort_index().to_string())

log()
log("=== 4. quantity 추출 실패(패턴 없어 기본값 1 적용) 상품명 ===")
failed = df[match_count == 0][["product_id", "name", "price_krw", "quantity"]]
log(f"실패 건수: {len(failed)}")
log(failed.to_string(index=False))

log()
log("=== 다중 매치 확인 (검증용, 2개 이상 'N개' 패턴 발견) ===")
multi = df[match_count >= 2][["product_id", "name", "quantity"]]
log(f"다중 매치 건수: {len(multi)}")
if len(multi):
    log(multi.to_string(index=False))

df.to_csv(DST, index=False, encoding="utf-8-sig")
log()
log(f"=== 5. 저장 완료: {DST} ({len(df)}행, quantity/unit_price 컬럼 추가) ===")

with open(LOG, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("DONE")
