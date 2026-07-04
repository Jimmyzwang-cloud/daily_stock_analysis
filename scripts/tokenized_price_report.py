#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""每日代币化股票(Tokenized Stocks)链上价格 -> 邮件推送
数据源: CoinGecko  发送: QQ 邮箱 SMTP
凭证复用环境变量: EMAIL_SENDER / EMAIL_PASSWORD / EMAIL_RECEIVERS
"""
import os, json, smtplib, urllib.request, ssl
from email.mime.text import MIMEText
from email.header import Header
from datetime import datetime, timezone, timedelta

# 你的美股 -> CoinGecko 代币化 id(已在云端逐一验证存在)
TOKENS = [
    ("英伟达 NVDA",  "nvidia-xstock",                          "xStock"),
    ("谷歌 GOOGL",   "alphabet-xstock",                        "xStock"),
    ("英特尔 INTC",  "intel-xstock",                           "xStock"),
    ("美光 MU",      "micron-technology-ondo-tokenized-stock", "Ondo"),
]

def fetch_prices():
    ids = ",".join(t[1] for t in TOKENS)
    url = (f"https://api.coingecko.com/api/v3/simple/price?ids={ids}"
           "&vs_currencies=usd&include_24hr_change=true&include_last_updated_at=true")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8", "ignore"))

def build_report(data):
    bj = timezone(timedelta(hours=8))
    now = datetime.now(bj).strftime("%Y-%m-%d %H:%M")
    lines = [f"# 链上代币化股价 · {now}", "",
             "> 数据来源: CoinGecko | 代币化股票(区块链上交易的股票代币)", ""]
    lines.append("| 股票 | 链上价格(USD) | 24h涨跌 | 发行方 |")
    lines.append("|------|------|------|------|")
    for name, cid, issuer in TOKENS:
        info = data.get(cid)
        if info and info.get("usd") is not None:
            price = info["usd"]
            chg = info.get("usd_24h_change")
            chg_s = f"{chg:+.2f}%" if chg is not None else "N/A"
            arrow = "🔺" if (chg or 0) > 0 else ("🔻" if (chg or 0) < 0 else "▪️")
            lines.append(f"| {name} | ${price} | {arrow}{chg_s} | {issuer} |")
        else:
            lines.append(f"| {name} | 暂无数据 | - | {issuer} |")
    lines += ["", "---",
              "*代币化股价为区块链上交易价,与真实股价通常贴近但可能有溢价/折价。仅供参考,非投资建议。*"]
    return "\n".join(lines)

def send_email(subject, body):
    sender = os.environ["EMAIL_SENDER"]
    password = os.environ["EMAIL_PASSWORD"]
    receivers = [x.strip() for x in os.environ.get("EMAIL_RECEIVERS", sender).split(",") if x.strip()]
    msg = MIMEText(body, "plain", "utf-8")
    msg["From"] = Header(sender)
    msg["To"] = Header(",".join(receivers))
    msg["Subject"] = Header(subject, "utf-8")
    host = "smtp.qq.com" if sender.endswith("@qq.com") else "smtp." + sender.split("@")[1]
    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL(host, 465, timeout=30, context=ctx) as s:
        s.login(sender, password)
        s.sendmail(sender, receivers, msg.as_string())
    print(f"邮件发送成功 -> {receivers}")

def main():
    data = fetch_prices()
    report = build_report(data)
    print(report)
    subject = "链上代币化股价 · " + datetime.now(timezone(timedelta(hours=8))).strftime("%m-%d")
    send_email(subject, report)

if __name__ == "__main__":
    main()
