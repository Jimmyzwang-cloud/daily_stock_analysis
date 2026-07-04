#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""每日代币化股票(Tokenized Stocks)链上价格 -> 邮件推送(HTML 卡片风)
数据源: CoinGecko  发送: QQ 邮箱 SMTP
凭证复用环境变量: EMAIL_SENDER / EMAIL_PASSWORD / EMAIL_RECEIVERS
涨跌配色: 涨红 #d1333f / 跌绿 #0a8f3c (A股/中国习惯)
"""
import os, json, smtplib, urllib.request, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from datetime import datetime, timezone, timedelta

# 你的美股 -> CoinGecko 代币化 id(已在云端逐一验证存在)
TOKENS = [
    ("英伟达", "NVDA",  "nvidia-xstock",                          "xStock"),
    ("谷歌",   "GOOGL", "alphabet-xstock",                        "xStock"),
    ("英特尔", "INTC",  "intel-xstock",                           "xStock"),
    ("美光",   "MU",    "micron-technology-ondo-tokenized-stock", "Ondo"),
]

UP_COLOR = "#d1333f"    # 涨=红(A股习惯)
DOWN_COLOR = "#0a8f3c"  # 跌=绿
FLAT_COLOR = "#888888"


def fetch_prices():
    ids = ",".join(t[2] for t in TOKENS)
    url = (f"https://api.coingecko.com/api/v3/simple/price?ids={ids}"
           "&vs_currencies=usd&include_24hr_change=true&include_last_updated_at=true")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8", "ignore"))


def _fmt_price(p):
    if p is None:
        return "—"
    return f"${p:,.2f}" if p >= 1 else f"${p}"


def build_html(data, now_str):
    cards = []
    for cn, code, cid, issuer in TOKENS:
        info = data.get(cid) or {}
        price = info.get("usd")
        chg = info.get("usd_24h_change")
        if chg is None:
            color, arrow, chg_s = FLAT_COLOR, "", "—"
        elif chg > 0:
            color, arrow, chg_s = UP_COLOR, "▲", f"+{chg:.2f}%"
        elif chg < 0:
            color, arrow, chg_s = DOWN_COLOR, "▼", f"{chg:.2f}%"
        else:
            color, arrow, chg_s = FLAT_COLOR, "▪", "0.00%"

        cards.append(f"""
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 14px 0;border-collapse:separate;">
          <tr><td style="background:#ffffff;border:1px solid #eceef1;border-radius:14px;padding:18px 20px;box-shadow:0 1px 3px rgba(0,0,0,0.04);">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td style="font-size:16px;font-weight:600;color:#1a1a1a;">{cn} <span style="color:#9aa0a6;font-weight:500;">{code}</span></td>
                <td align="right"><span style="font-size:11px;color:#6b7280;background:#f2f4f7;border-radius:6px;padding:3px 9px;">{issuer}</span></td>
              </tr>
              <tr><td colspan="2" style="padding-top:8px;">
                <span style="font-size:30px;font-weight:700;color:#111111;letter-spacing:-0.5px;">{_fmt_price(price)}</span>
                <span style="font-size:15px;font-weight:600;color:{color};padding-left:10px;">{arrow} {chg_s}</span>
                <span style="font-size:12px;color:#9aa0a6;padding-left:4px;">24h</span>
              </td></tr>
            </table>
          </td></tr>
        </table>""")

    return f"""<!DOCTYPE html>
<html><body style="margin:0;padding:0;background:#f5f6f8;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f5f6f8;padding:24px 0;">
    <tr><td align="center">
      <table role="presentation" width="480" cellpadding="0" cellspacing="0" style="max-width:480px;width:100%;">
        <tr><td style="padding:0 16px;">
          <div style="font-size:22px;font-weight:700;color:#111;margin-bottom:2px;">🔗 链上代币化股价</div>
          <div style="font-size:13px;color:#9aa0a6;margin-bottom:20px;">{now_str} · 数据来源 CoinGecko</div>
          {''.join(cards)}
          <div style="font-size:11px;color:#b0b4ba;line-height:1.6;margin-top:8px;padding:0 4px;">
            代币化股价为区块链上交易价,与真实股价通常贴近但可能有溢价/折价。<br>仅供参考,不构成投资建议。
          </div>
        </td></tr>
      </table>
    </td></tr>
  </table>
</body></html>"""


def build_text(data, now_str):
    lines = [f"链上代币化股价 · {now_str}", ""]
    for cn, code, cid, issuer in TOKENS:
        info = data.get(cid) or {}
        price, chg = info.get("usd"), info.get("usd_24h_change")
        chg_s = f"{chg:+.2f}%" if chg is not None else "—"
        lines.append(f"{cn} {code}: {_fmt_price(price)}  ({chg_s})  [{issuer}]")
    lines += ["", "代币化股价为链上交易价,仅供参考,非投资建议。"]
    return "\n".join(lines)


def send_email(subject, html_body, text_body):
    sender = os.environ["EMAIL_SENDER"]
    password = os.environ["EMAIL_PASSWORD"]
    receivers = [x.strip() for x in os.environ.get("EMAIL_RECEIVERS", sender).split(",") if x.strip()]
    msg = MIMEMultipart("alternative")
    msg["From"] = Header(sender)
    msg["To"] = Header(",".join(receivers))
    msg["Subject"] = Header(subject, "utf-8")
    msg.attach(MIMEText(text_body, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))
    host = "smtp.qq.com" if sender.endswith("@qq.com") else "smtp." + sender.split("@")[1]
    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL(host, 465, timeout=30, context=ctx) as s:
        s.login(sender, password)
        s.sendmail(sender, receivers, msg.as_string())
    print(f"邮件发送成功 -> {receivers}")


def main():
    data = fetch_prices()
    now_str = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M")
    html_body = build_html(data, now_str)
    text_body = build_text(data, now_str)
    print(text_body)
    subject = "链上代币化股价 · " + datetime.now(timezone(timedelta(hours=8))).strftime("%m-%d")
    send_email(subject, html_body, text_body)


if __name__ == "__main__":
    main()
