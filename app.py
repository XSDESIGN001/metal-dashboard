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

st.markdown("""
<style>
.company-header { display:flex; justify-content:space-between; align-items:center;
    padding:12px 0; border-bottom:3px solid #1a5276; margin-bottom:16px; }
.company-name { font-size:26px; font-weight:bold; color:#1a5276; }
.update-time { font-size:13px; color:#888; }
.notice-box { background:#f0f8ff; border-left:4px solid #2980b9;
    padding:10px 16px; margin-bottom:18px; font-size:13px; border-radius:4px; }
.price-table { width:100%; border-collapse:collapse; }
.price-table th { background:#d4e6f1; color:#1a5276; padding:10px 8px;
    text-align:center; font-size:13px; border:1px solid #bbb; }
.price-table td { padding:8px; text-align:center; border:1px solid #e0e0e0; font-size:13px; }
.price-table tr:nth-child(even) { background:#fafafa; }
.price-up { color:#c0392b; font-weight:bold; }
.price-down { color:#27ae60; font-weight:bold; }
.price-val { font-size:18px; font-weight:bold; color:#2c3e50; }
.info-card { background:#f8f9fa; border:1px solid #dee2e6;
    border-radius:6px; padding:14px; margin-bottom:12px; }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=600)
def fetch_copper():
    try:
        t = yf.Ticker("HG=F")
        h = t.history(period="3d")
        if len(h) >= 2:
            cur = h["Close"].iloc[-1]
            prev = h["Close"].iloc[-2]
            return {"price": cur, "change_pct": ((cur - prev) / prev) * 100}
        elif len(h) == 1:
            return {"price": h["Close"].iloc[-1], "change_pct": 0}
    except:
        pass
    return None

@st.cache_data(ttl=600)
def fetch_nickel():
    try:
        t = yf.Ticker("JJN")
        h = t.history(period="3d")
        if len(h) >= 2 and h["Close"].iloc[-1] > 0:
            cur = h["Close"].iloc[-1]
            prev = h["Close"].iloc[-2]
            return {"price": cur, "change_pct": ((cur - prev) / prev) * 100}
    except:
        pass
    return None

@st.cache_data(ttl=900)
def fetch_twd():
    try:
        r = requests.get("https://api.exchangerate.fun/latest?base=USD", timeout=10)
        return r.json()["rates"].get("TWD", 31.84)
    except:
        return 31.84

twd = fetch_twd()
now = datetime.now(TW_TZ)
copper = fetch_copper()
nickel = fetch_nickel()

st.markdown(f'''<div class="company-header">
<div class="company-name">🔩 洪邦金屬股份有限公司 — 即時物料價格看板</div>
<div class="update-time">更新時間：{now.strftime("%Y-%m-%d %H:%M:%S")} (UTC+8) ｜ 每 2 分鐘自動刷新</div>
</div>''', unsafe_allow_html=True)

st.markdown('''<div class="notice-box">
📌 <b>注意事項：</b>銅價為 COMEX 期貨即時報價；不鏽鋼以鎳價（JJN ETN）作為 304 不鏽鋼原料成本參考（鎳佔成本約 60%）。實際成交價依當日盤價與供應商報價為準。本看板僅供內部參考。
</div>''', unsafe_allow_html=True)

c1, c2, c3 = st.columns([3, 3, 2])

def render_table(title, label, spec, unit, data):
    st.markdown(f"### {title}")
    if data and data.get("price"):
        usd = data["price"]
        ntd = usd * twd
        chg = data["change_pct"]
        arrow = "▲" if chg >= 0 else "▼"
        cls = "price-up" if chg >= 0 else "price-down"
        html = f'''<table class="price-table">
<tr><th>品名</th><th>規格</th><th>單價 (USD)</th><th>單價 (TWD)</th><th>漲跌</th></tr>
<tr><td>{label}</td><td>{spec}</td>
<td class="price-val">${usd:,.2f}{unit}</td>
<td class="price-val">NT$ {ntd:,.0f}{unit}</td>
<td class="{cls}">{arrow} {chg:+.2f}%</td></tr>
</table>'''
        st.markdown(html, unsafe_allow_html=True)
    else:
        st.warning(f"⚠️ 無法取得{label}即時報價，請確認資料來源")

with c1:
    render_table("🟠 銅 Copper", "紅銅", "COMEX 期貨", "/lb", copper)

with c2:
    render_table("⚙️ 不鏽鋼參考價", "鎳 (304 參考)", "JJN ETN", "", nickel)

with c3:
    st.markdown("### 📋 匯率資訊")
    st.markdown(f'''<div class="info-card">
<table style="width:100%">
<tr><td style="color:#888;font-size:13px;">USD / TWD</td>
<td style="font-size:20px;font-weight:bold;color:#1a5276;text-align:right;">{twd:.2f}</td></tr>
</table></div>''', unsafe_allow_html=True)
    st.markdown("### 📞 聯絡資訊")
    st.markdown('''<div class="info-card">
<p style="font-size:12px;color:#999;">📧 待填寫<br>📱 待填寫</p>
</div>''', unsafe_allow_html=True)
    with st.expander("📌 免責聲明"):
        st.caption("本看板價格僅供內部參考，實際交易依當日報價單為準。")

st.markdown("---")
st.subheader("📊 近 7 日價格走勢（銅）")
try:
    hist = yf.Ticker("HG=F").history(period="7d")
    if not hist.empty:
        st.line_chart(pd.DataFrame({"銅 COMEX (USD/lb)": hist["Close"]}), use_container_width=True)
except:
    st.caption("⚠️ 歷史資料暫無法載入")
