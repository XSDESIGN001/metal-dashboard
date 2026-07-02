# app.py

import streamlit as st
import yfinance as yf
import requests
import pandas as pd
from datetime import datetime, timezone, timedelta
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="洪邦金屬價格看板", page_icon="🔩", layout="wide")
st_autorefresh(interval=120000, key="auto_refresh")
TW_TZ = timezone(timedelta(hours=8))

ITEMS = [
    [
        ("磷碎", 110), ("紅碎", 95), ("青碎", 70),
        ("青電", 67), ("青銅絲", 65),
    ],
    [
        ("光亮線", 109), ("光亮米", 108),
        ("粉碎角銅 (含銅99.8%↑)", 108), ("紅白米 (含銅98.2%↑)", 107),
        ("乾淨紅銅管、粗鍍錫線、鍍錫板、破碎銅", 107),
        ("油管 / 螺旋管 / 帶雜銅管", 104),
        ("乾淨無油紅銅屑", 100), ("馬達銅 / 帶油紅銅屑", 98),
    ],
    [
        ("砲金", 75), ("大青", 60),
    ],
]

SS_ITEMS = [("301不鏽鋼沖壓料", 32), ("304不鏽鋼沖壓料", 40)]

st.markdown("""
<style>
.company-header { display:flex; justify-content:space-between; align-items:center;
    padding:12px 0; border-bottom:3px solid #1a5276; margin-bottom:16px; }
.company-name { font-size:24px; font-weight:bold; color:#1a5276; }
.update-time { font-size:13px; color:#666; }
.notice-box { background:#f5f9fc; border-left:4px solid #2980b9;
    padding:10px 16px; margin-bottom:18px; font-size:13px; border-radius:4px; color:#333; }
.price-table { width:100%; border-collapse:collapse; margin-bottom:20px; }
.price-table th { background:#e8e8e8; color:#222; padding:8px 10px;
    text-align:center; font-size:13px; border:1px solid #ccc; }
.price-table td { padding:7px 10px; text-align:center; border:1px solid #ddd;
    font-size:13px; color:#222; background:#fff; }
.price-val { font-size:16px; font-weight:bold; color:#111; }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60)
def get_copper():
    try:
        h = yf.Ticker("HG=F").history(period="2d")
        return h["Close"].iloc[-1] if len(h) >= 1 else None
    except:
        return None

@st.cache_data(ttl=60)
def get_twd():
    try:
        r = requests.get("https://api.exchangerate.fun/latest?base=USD", timeout=10)
        return r.json()["rates"].get("TWD", 31.88)
    except:
        return 31.88

cu = get_copper()
twd = get_twd()
now = datetime.now(TW_TZ)
cu_kg = (cu * 2.20462) * twd if cu else None

st.markdown(f'''<div class="company-header">
<div class="company-name">🔩 洪邦金屬股份有限公司 — 即時物料價格看板</div>
<div class="update-time">更新時間：{now.strftime("%Y-%m-%d %H:%M:%S")} (UTC+8) ｜ 每 2 分鐘自動刷新</div>
</div>''', unsafe_allow_html=True)

if cu:
    st.markdown(f'''<div class="notice-box">
📌 COMEX 銅：<b>${cu:,.2f}/lb</b> ｜ 匯率：<b>{twd:.2f}</b> ｜
純銅基準：<b>NT$ {cu_kg:,.0f}/kg</b> ｜ 牌價 = 基準價 × 品項%
</div>''', unsafe_allow_html=True)
else:
    st.warning("⚠️ 無法取得國際銅價")

for group in ITEMS:
    rows = ""
    for name, pct in group:
        price = f"NT$ {cu_kg * pct / 100:,.0f}" if cu_kg else "N/A"
        rows += f"<tr><td>{name}</td><td class='price-val'>{price}</td></tr>"
    st.markdown(f"""<table class="price-table">
<tr><th>品名</th><th>即時牌價 (TWD/kg)</th></tr>{rows}</table>""", unsafe_allow_html=True)

rows_ss = ""
for name, price in SS_ITEMS:
    rows_ss += f"<tr><td>{name}</td><td class='price-val'>NT$ {price}</td></tr>"
st.markdown(f"""<table class="price-table">
<tr><th>品名</th><th>單價 (TWD/kg)</th></tr>{rows_ss}</table>""", unsafe_allow_html=True)


