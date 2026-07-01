# app.py

import streamlit as st
import yfinance as yf
import requests
import pandas as pd
from datetime import datetime, timezone, timedelta
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="聖展金屬價格看板", page_icon="🔩", layout="wide")
st_autorefresh(interval=120000, key="auto_refresh")
TW_TZ = timezone(timedelta(hours=8))

ITEMS = {
    "銅類": [
        ("磷碎", 125), ("紅碎", 109), ("光亮線", 109),
        ("光亮米", 108), ("粉碎角銅(99.8%↑)", 108),
        ("紅白米(98.2%↑)", 107), ("乾淨紅銅管/粗鍍錫線等", 107),
        ("油管/螺旋管/帶雜銅管", 104), ("乾淨無油紅銅屑", 100),
        ("馬達銅/帶油紅銅屑", 98),
    ],
    "青銅類": [("青碎", 80), ("青電", 77), ("青銅絲", 74)],
    "砲金類": [("砲金", 86), ("大青", 68)],
}

st.markdown("""
<style>
.company-header { display:flex; justify-content:space-between; align-items:center;
    padding:12px 0; border-bottom:3px solid #1a5276; margin-bottom:16px; }
.company-name { font-size:24px; font-weight:bold; color:#1a5276; }
.update-time { font-size:13px; color:#666; }
.notice-box { background:#f5f9fc; border-left:4px solid #2980b9;
    padding:10px 16px; margin-bottom:18px; font-size:13px; border-radius:4px; color:#333; }
.price-table { width:100%; border-collapse:collapse; margin-bottom:16px; }
.price-table th { background:#e8e8e8; color:#222; padding:8px 10px;
    text-align:center; font-size:13px; border:1px solid #ccc; }
.price-table td { padding:7px 10px; text-align:center; border:1px solid #ddd;
    font-size:13px; color:#222; background:#fff; }
.price-val { font-size:16px; font-weight:bold; color:#111; }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=600)
def get_copper():
    try:
        h = yf.Ticker("HG=F").history(period="2d")
        if len(h) >= 1:
            return h["Close"].iloc[-1]
    except:
        pass
    return None

@st.cache_data(ttl=900)
def get_twd():
    try:
        r = requests.get("https://api.exchangerate.fun/latest?base=USD", timeout=10)
        return r.json()["rates"].get("TWD", 31.87)
    except:
        return 31.87

cu = get_copper()
twd = get_twd()
now = datetime.now(TW_TZ)
cu_twd_kg = cu * twd / 0.453592 if cu else None

st.markdown(f'''<div class="company-header">
<div class="company-name">🔩 聖展金屬有限公司 — 即時物料價格看板</div>
<div class="update-time">更新時間：{now.strftime("%Y-%m-%d %H:%M:%S")} (UTC+8) ｜ 每 2 分鐘自動刷新</div>
</div>''', unsafe_allow_html=True)

if cu:
    st.markdown(f'''<div class="notice-box">
📌 COMEX 銅：<b>${cu:,.2f}/lb</b> ｜ 匯率：<b>{twd:.2f}</b> ｜
純銅基準：<b>NT$ {cu_twd_kg:,.0f}/kg</b> ｜ 牌價 = 基準價 × 品項%
</div>''', unsafe_allow_html=True)
else:
    st.warning("⚠️ 無法取得國際銅價")

for cat, items in ITEMS.items():
    st.markdown(f"### {cat}")
    rows = ""
    for name, pct in items:
        price = f"NT$ {cu_twd_kg * pct / 100:,.0f}" if cu_twd_kg else "N/A"
        rows += f"<tr><td>{name}</td><td class='price-val'>{price}</td></tr>"
    st.markdown(f"""<table class="price-table">
<tr><th>品名</th><th>即時牌價 (TWD/kg)</th></tr>{rows}</table>""", unsafe_allow_html=True)

st.markdown("### 不銹鋼（手動價格）")
st.markdown("""<table class="price-table">
<tr><th>品名</th><th>單價 (TWD/kg)</th></tr>
<tr><td>301 沖壓料</td><td class='price-val'>NT$ 32</td></tr>
<tr><td>304 沖壓料</td><td class='price-val'>NT$ 40</td></tr>
</table>""", unsafe_allow_html=True)

st.markdown("---")
st.subheader("📊 COMEX 銅 近 7 日走勢")
try:
    hist = yf.Ticker("HG=F").history(period="7d")
    if not hist.empty:
        st.line_chart(pd.DataFrame({"銅 (USD/lb)": hist["Close"]}), use_container_width=True)
except:
    st.caption("⚠️ 無法載入")
