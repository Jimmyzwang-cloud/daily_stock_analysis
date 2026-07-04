#!/usr/bin/env python3
# 用 yfinance 拉美光 MU 近期日线(云端境外可用)
import subprocess, sys
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "yfinance"], check=False)
import yfinance as yf

t = yf.Ticker("MU")
h = t.history(period="3mo")
print("=== 美光 MU 近3个月日线 ===")
print("总交易日:", len(h))
print("=== 近30日 (日期 收盘 涨跌% 成交量) ===")
closes = h["Close"].tolist()
dates = [str(d.date()) for d in h.index]
vols = h["Volume"].tolist()
for i in range(max(0, len(h)-30), len(h)):
    chg = (closes[i]/closes[i-1]-1)*100 if i > 0 else 0
    print(f"{dates[i]}  ${closes[i]:.2f}  {chg:+.2f}%  vol={int(vols[i]/1e6)}M")

# 关键统计
print("=== 关键统计 ===")
print(f"最新收盘: ${closes[-1]:.2f}  日期: {dates[-1]}")
print(f"3个月最高: ${max(closes):.2f}")
print(f"3个月最低: ${min(closes):.2f}")
print(f"3个月涨幅: {(closes[-1]/closes[0]-1)*100:+.1f}%")
print(f"近1个月涨幅: {(closes[-1]/closes[max(0,len(closes)-22)]-1)*100:+.1f}%")

# 基本面
try:
    info = t.info
    print("=== 基本面 ===")
    for k in ["marketCap","trailingPE","forwardPE","fiftyTwoWeekHigh","fiftyTwoWeekLow","targetMeanPrice"]:
        print(f"{k}: {info.get(k)}")
except Exception as e:
    print("基本面失败:", str(e)[:80])
print("FETCH_DONE")
