#!/usr/bin/env python3
# 拉美光 MU 近期日线 + 关键指标,输出供分析
import json, urllib.request

def fetch(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "ignore")

# 东财美股日线(105.MU)
url = ("https://push2his.eastmoney.com/api/qt/stock/kline/get?"
       "secid=105.MU&fields1=f1,f2,f3,f4,f5,f6&"
       "fields2=f51,f52,f53,f54,f55,f56,f57&klt=101&fqt=1&beg=20260401&end=20260704")
try:
    d = json.loads(fetch(url))
    data = d.get("data") or {}
    klines = data.get("klines") or []
    print("股票:", data.get("name"), data.get("code"))
    print("总条数:", len(klines))
    print("=== 近 40 日 (日期,开,收,高,低,成交量,成交额,振幅%) ===")
    for line in klines[-40:]:
        print(line)
except Exception as e:
    print("东财失败:", str(e)[:150])

# 实时快照
try:
    rt = json.loads(fetch("https://push2.eastmoney.com/api/qt/stock/get?secid=105.MU&fields=f43,f44,f45,f46,f60,f170,f171"))
    print("=== 实时 ===", json.dumps(rt.get("data"), ensure_ascii=False))
except Exception as e:
    print("实时失败:", str(e)[:100])
print("FETCH_DONE")
