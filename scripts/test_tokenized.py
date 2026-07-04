#!/usr/bin/env python3
# 确认你那几家美股的 xStock 代币化版本是否存在及价格
import json, urllib.request

def fetch(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "ignore")

# 你的美股 -> 候选 CoinGecko id(xStock 命名规律: <公司>-xstock)
candidates = {
    "NVDA (英伟达)": "nvidia-xstock",
    "GOOGL (谷歌)": "google-xstock",
    "INTC (英特尔)": "intel-xstock",
    "MU (美光)": "micron-xstock",
    "NOK (诺基亚)": "nokia-xstock",
}
ids = ",".join(candidates.values())
print("查询 xStock 价格...")
try:
    d = json.loads(fetch(f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd&include_24hr_change=true"))
    for name, cid in candidates.items():
        info = d.get(cid)
        if info:
            print(f"✅ {name}: ${info.get('usd')}  (24h {info.get('usd_24h_change', 0):+.2f}%)  id={cid}")
        else:
            print(f"❌ {name}: 无 xStock 版本 (id={cid} 不存在)")
except Exception as e:
    print(f"失败: {type(e).__name__}: {str(e)[:100]}")

# 对没找到的,再用 search 兜底看有没有别的发行方
print()
print("对未命中的做 search 兜底:")
for name, cid in candidates.items():
    key = name.split()[0].lower()
    try:
        d = json.loads(fetch(f"https://api.coingecko.com/api/v3/search?query={key}"))
        toks = [(c.get("symbol"), c.get("name"), c.get("id")) for c in d.get("coins", []) if "stock" in (c.get("name","").lower())][:5]
        print(f"[{name}] 代币化候选: {toks}")
    except Exception as e:
        print(f"[{name}] search 失败: {str(e)[:60]}")

print()
print("TEST_SCRIPT_DONE")
