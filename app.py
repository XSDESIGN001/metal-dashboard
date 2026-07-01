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

# ====== 品項 % 數（修改這裡即可） ======
ITEMS = {
    "銅類": [
        ("磷碎", 125),
        ("紅碎", 109),
        ("光亮線", 109),
        ("光亮米", 108),
        ("粉碎角銅(99.8%↑)", 108),
        ("紅白米(98.2%↑)", 107),
        ("乾淨紅銅管/粗鍍錫線等", 107),
        ("油管/螺旋管/帶雜銅管", 104),
        ("乾淨無油紅銅屑", 100),
        ("馬達銅/帶油紅銅屑", 98),
    ],
    "青銅類": [
        ("青碎", 80),
        ("青電", 77),
        ("青銅絲", 74),
    ],
    "砲金類": [
        ("砲金", 86),
        ("大青", 68),
    ],
}

# ====== CSS ======
st.markdown("""
<style>
.company-header { display:flex; justify-content:space-between; align-items:center;
    padding:12px 0; border-bottom:3px solid #1a5276; margin-bottom:16px; }
.company-name { font-size:24px; font-weight:bold; color:#1a5276; }
.update-time { font-size:13px; color:#888; }
.notice-box { background:#f0f8ff; border-left:4px solid #2980b9;
    padding:10px 16px; margin-bottom:18px; font-size:13px; border-radius:4px; }
.price-table { width:100%; border-collapse:collapse; margin-bottom:16px; }
.price-table th { background:#d4e6f1; color:#1a5276; padding:8px 6px;
    text-align:center; font-size:12px; border:1px solid #bbb; }
.price-table td { padding:6px; text-align:center; border:1px solid #e0e0e0; font-size:12px; }
.price-table tr:nth-child(even) { background:#fafafa; }
.price-up { color:#c0392b; font-weight:bold; }
.price-down { color:#27ae60; font-weight:bold; }
.price-val { font-size:15px; font-weight:bold; color:#2c3e50; }
</style>
""", unsafe_allow_html=True)

# ====== 資料抓取 ======
@st.cache_data(ttl=600)
def get_copper_usd_lb():
    try:
        h = yf.Ticker("HG=F").history(period="2d")
        if len(h) >= 1:
            return h["Close"].iloc[-1]
    except:
        pass
    return None

@st.cache_data(ttl=900)
def get_twd_rate():
    try:
        r = requests.get("https://api.exchangerate.fun/latest?base=USD", timeout=10)
        return r.json()["rates"].get("TWD", 31.87)
    except:
        return 31.87

copper_usd = get_copper_usd_lb()
twd_rate = get_twd_rate()
now = datetime.now(TW_TZ)

# 轉換: USD/lb -> TWD/kg (1 lb = 0.453592 kg)
if copper_usd:
    copper_twd_kg = copper_usd * twd_rate / 0.453592
else:
    copper_twd_kg = None

# ====== HEADER ======
st.markdown(f'''<div class="company-header">
<div class="company-name">🔩 洪邦金屬股份有限公司 — 即時物料價格看板</div>
<div class="update-time">更新時間：{now.strftime("%Y-%m-%d %H:%M:%S")} (UTC+8) ｜ 每 2 分鐘自動刷新</div>
</div>''', unsafe_allow_html=True)

# ====== 公告區 ======
if copper_usd:
    st.markdown(f'''<div class="notice-box">
📌 COMEX 銅期貨：<b>${copper_usd:,.2f}/lb</b> ｜ 匯率 USD/TWD：<b>{twd_rate:.2f}</b> ｜
換算純銅基準價：<b>NT$ {copper_twd_kg:,.0f}/kg</b> ｜ 各品項價格 = 基準價 × 品項%
</div>''', unsafe_allow_html=True)
else:
    st.warning("⚠️ 無法取得國際銅價，請稍後再試")

# ====== 價格表 ======
for cat, items in ITEMS.items():
    st.markdown(f"### {cat}")
    rows = ""
    for name, pct in items:
        if copper_twd_kg:
            price = copper_twd_kg * pct / 100
            rows += f"<tr><td>{name}</td><td>{pct}%</td><td class='price-val'>NT$ {price:,.0f}</td></tr>"
        else:
            rows += f"<tr><td>{name}</td><td>{pct}%</td><td>N/A</td></tr>"
    st.markdown(f"""<table class="price-table">
<tr><th>品名</th><th>%數</th><th>即時牌價 (TWD/kg)</th></tr>
{rows}
</table>""", unsafe_allow_html=True)

# ====== 不銹鋼 ======
st.markdown("### 不銹鋼（手動價格）")
st.markdown("""<table class="price-table">
<tr><th>品名</th><th>單價 (TWD/kg)</th></tr>
<tr><td>301 沖壓料</td><td class='price-val'>NT$ 32</td></tr>
<tr><td>304 沖壓料</td><td class='price-val'>NT$ 40</td></tr>
</table>""", unsafe_allow_html=True)

# ====== 走勢圖 ======
st.markdown("---")
st.subheader("📊 COMEX 銅 近 7 日走勢 (USD/lb)")
try:
    hist = yf.Ticker("HG=F").history(period="7d")
    if not hist.empty:
        st.line_chart(pd.DataFrame({"銅": hist["Close"]}), use_container_width=True)
except:
    st.caption("⚠️ 無法載入")
