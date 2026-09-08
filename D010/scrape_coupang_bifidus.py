"""
쿠팡 검색결과("비피더스균") 스크래핑 -> CSV 저장
- patchright(Playwright 호환, 스텔스 패치) + 실제 Chrome 채널 사용
- 페이지 요청 사이 2~3초 랜덤 딜레이
- 상품 고유 id 기준 중복 제거, 최소 목표 수량 확보까지 다음 페이지 진행
"""
import csv
import random
import re
import time

from bs4 import BeautifulSoup
from patchright.sync_api import sync_playwright

QUERY = "비피더스균"
TARGET_COUNT = 100         # 최소 30~50개 이상 요구 -> 여유 있게 100개 목표(페이지 간 딜레이 실제 사용 위해 다중 페이지 확보)
MAX_PAGES = 6               # 안전장치: 무한 루프 방지
OUTPUT_CSV = "D010/outputs/coupang_bifidus_products.csv"


def search_url(query: str, page: int) -> str:
    from urllib.parse import quote
    return f"https://www.coupang.com/np/search?q={quote(query)}&page={page}"


def parse_products(html: str, page_num: int):
    soup = BeautifulSoup(html, "html.parser")
    items = soup.select("li[class*='productUnit__']")

    rows = []
    for it in items:
        product_id = it.get("data-id", "")

        name_el = it.select_one("div[class*='productNameV2']")
        name = name_el.get_text(strip=True) if name_el else ""

        price = ""
        price_area = it.select_one("div[class*='priceArea']")
        if price_area:
            spans = price_area.find_all("span")
            cand = [s.get_text(strip=True) for s in spans if "원" in s.get_text() and "(" not in s.get_text()]
            price = cand[-1] if cand else ""
        price_krw = int(re.sub(r"[^0-9]", "", price)) if price else None

        rating_wrap = it.select_one("div[aria-label][class*='fw-gap-[2px]']")
        rating = rating_wrap.get("aria-label") if rating_wrap else ""
        rating = float(rating) if rating else None

        review_count = None
        rating_block = it.select_one("div[class*='ProductRating_productRating']")
        if rating_block:
            m = re.search(r"\(([\d,]+)\)", rating_block.get_text())
            if m:
                review_count = int(m.group(1).replace(",", ""))

        rows.append({
            "product_id": product_id,
            "name": name,
            "price_krw": price_krw,
            "rating": rating,
            "review_count": review_count,
            "page": page_num,
        })
    return rows


def main():
    collected = {}  # product_id -> row, 중복 제거용

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=False)
        context = browser.new_context(locale="ko-KR", viewport={"width": 1366, "height": 900})
        page = context.new_page()

        # 워밍업: 루트 페이지 먼저 방문 (콜드 세션으로 검색 페이지 직행 시 Access Denied 발생 확인됨)
        page.goto("https://www.coupang.com/", wait_until="load", timeout=30000)
        time.sleep(3)

        for page_num in range(1, MAX_PAGES + 1):
            url = search_url(QUERY, page_num)

            found = False
            for attempt in range(3):
                page.goto(url, wait_until="load", timeout=30000)
                try:
                    page.wait_for_selector("li[class*='productUnit__']", timeout=20000)
                    found = True
                    break
                except Exception:
                    backoff = 6 + attempt * 5
                    print(f"[page {page_num}] 시도 {attempt + 1}/3 실패 (title='{page.title()}') - {backoff}초 대기 후 재시도")
                    time.sleep(backoff)

            if not found:
                print(f"[page {page_num}] 재시도 소진 - 이 페이지 건너뛰고 지금까지 수집분으로 종료")
                break

            html = page.content()
            rows = parse_products(html, page_num)
            new_count = 0
            for r in rows:
                if r["product_id"] and r["product_id"] not in collected:
                    collected[r["product_id"]] = r
                    new_count += 1

            print(f"[page {page_num}] 파싱 {len(rows)}건, 신규 {new_count}건, 누적 {len(collected)}건")

            if len(collected) >= TARGET_COUNT:
                break

            time.sleep(random.uniform(2, 3))

        browser.close()

    final_rows = list(collected.values())[:max(TARGET_COUNT, len(collected))]

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["product_id", "name", "price_krw", "rating", "review_count", "page"])
        writer.writeheader()
        writer.writerows(final_rows)

    print(f"저장 완료: {OUTPUT_CSV} ({len(final_rows)}행)")


if __name__ == "__main__":
    main()
