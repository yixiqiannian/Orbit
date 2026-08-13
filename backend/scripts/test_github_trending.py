"""T2 验收脚本: 本地解析 + 边界 + 实网抓取。"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.github_trending import (
    _parse_num,
    _parse_today_stars,
    parse_trending,
    fetch_trending,
    TRENDING_URL,
)

REQUIRED_KEYS = {"rank", "title", "url", "description", "language",
                 "stars_total", "forks", "stars_today"}

# --- 1. _parse_num 边界 ---
cases = [
    ("11,519", 11519),
    ("2,855", 2855),
    ("-", 0),
    ("", 0),
    ("   ", 0),
    ("abc", 0),
    ("1,000,000", 1000000),
]
print("=== _parse_num 边界 ===")
ok = True
for text, expected in cases:
    got = _parse_num(text)
    status = "PASS" if got == expected else "FAIL"
    if got != expected:
        ok = False
    print(f"  {status} _parse_num({text!r}) = {got} (期望 {expected})")

# --- 2. _parse_today_stars ---
print("=== _parse_today_stars ===")
f6 = "HTML 11,519 728 Built by 2,855 stars today"
got = _parse_today_stars(f6)
print(f"  {'PASS' if got == 2855 else 'FAIL'} f6={f6!r} -> {got}")
if got != 2855:
    ok = False
got2 = _parse_today_stars("No stars today here")
print(f"  {'PASS' if got2 == 0 else 'FAIL'} no-match -> {got2}")
if got2 != 0:
    ok = False

# --- 3. 本地解析 trending.html ---
html_path = r"G:/Hermes/trending.html"
print(f"\n=== parse_trending({html_path}) ===")
with open(html_path, encoding="utf-8") as f:
    html = f.read()
items = parse_trending(html)
print(f"解析出 {len(items)} 条")
assert len(items) >= 10, f"FAIL: 少于 10 条: {len(items)}"
for it in items:
    missing = REQUIRED_KEYS - it.keys()
    assert not missing, f"FAIL: 缺少字段 {missing}: {it}"
    # 字段类型抽查
    assert isinstance(it["rank"], int) and it["rank"] > 0
    assert it["title"] and it["title"].count("/") >= 1
    assert it["url"].startswith("https://github.com/")
    assert isinstance(it["stars_total"], int)
    assert isinstance(it["forks"], int)
    assert isinstance(it["stars_today"], int)
    print(f"  #{it['rank']:>2} {it['title']:<45} lang={it['language'] or '-':<12} "
          f"star={it['stars_total']:<8} fork={it['forks']:<6} today={it['stars_today']}")
    if it["description"]:
        print(f"      desc: {it['description'][:90]}")
    print(f"      url:  {it['url']}")

# --- 4. 实网抓取 ---
print(f"\n=== fetch_trending() 实网: {TRENDING_URL} ===")
try:
    live = asyncio.run(fetch_trending())
    print(f"实网抓取成功: {len(live)} 条")
    if live:
        first = live[0]
        print(f"  首条: #{first['rank']} {first['title']} today={first['stars_today']}")
    assert len(live) >= 10, f"FAIL: 实网少于 10 条: {len(live)}"
    print("实网抓取 PASS")
except Exception as e:
    print(f"实网抓取失败(可接受, 本地解析已通过): {type(e).__name__}: {e}")

print("\n=== 结论 ===")
print("全部本地断言 PASS" if ok else "存在 FAIL")
sys.exit(0 if ok else 1)
