#!/usr/bin/env python3
# 测试:云端能否拿到代币化股票(tokenized stocks)链上价格
import json, urllib.request, urllib.error

def fetch(url, timeout=20, headers=None):
    req = urllib.request.Request(url, headers=headers or {"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "ignore")

print("=" * 60)
print("测试 1: CoinGecko 搜索代币化股票")
print("=" * 60)
for q in ["nvidia", "xstock", "tokenized"]:
    try:
        d = json.loads(fetch(f"https://api.coingecko.com/api/v3/search?query={q}"))
        coins = [(c.get("symbol"), c.get("name"), c.get("id")) for c in d.get("coins", [])][:8]
        print(f"[{q}] -> {coins}")
    except Exception as e:
        print(f"[{q}] 失败: {type(e).__name__}: {str(e)[:80]}")

print()
print("=" * 60)
print("测试 2: Jupiter 价格 API (Solana xStocks 代币地址)")
print("=" * 60)
# xStocks 在 Solana 上的代币 mint 地址(Backed Finance 发行)
xstocks = {
    "NVDAx": "Xsc9qvGR1efVDFGLrVsmkzv3qi45LTBjeUKSPmx9qEh",
    "GOOGLx": "XsCPL9dNWBMvFtTmwcCA5v3xWPSMEBCszbQdiLLq6aN",
    "AAPLx": "XsbEhLAtcf6HdfpFZ5xEMdqW8nfAvcsP5bdudRLJzJp",
    "MSFTx": "XsP7xzNPvEHS1m6qfanPUGjNmdnmsLKEoNAnHjdxxyZ",
}
for sym, mint in xstocks.items():
    try:
        d = json.loads(fetch(f"https://api.jup.ag/price/v2?ids={mint}"))
        info = d.get("data", {}).get(mint)
        price = info.get("price") if info else None
        print(f"[{sym}] mint={mint[:8]}... 价格=${price}")
    except Exception as e:
        print(f"[{sym}] 失败: {type(e).__name__}: {str(e)[:80]}")

print()
print("=" * 60)
print("测试 3: CoinGecko 直接按已知 xStocks id 取价")
print("=" * 60)
try:
    ids = "nvidia-xstock,apple-xstock,google-xstock,tesla-xstock"
    d = json.loads(fetch(f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd"))
    print(json.dumps(d, ensure_ascii=False))
except Exception as e:
    print(f"失败: {type(e).__name__}: {str(e)[:80]}")

print()
print("TEST_SCRIPT_DONE")
