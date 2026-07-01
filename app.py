# app.py

import streamlit as stimport yfinance as yfimport requestsimport pandas as pdfrom datetime import datetime, timezone, timedeltafrom streamlit_autorefresh import st_autorefresh

# ── 設定 ──────────────────────────────────────────

st.set_page_config(page_title=“聖展金屬價格看板”, page_icon=“🔩”, layout=“wide”)st_autorefresh(interval=120000, key="auto_refresh")TW_TZ = timezone(timedelta(hours=8))

# ── 自訂 CSS（仿參考圖樣式）─────────────────────

st.markdown("""

""", unsafe_allow_html=True)

# ── 資料抓取 ──────────────────────────────────────

@st.cache_data(ttl=600)def fetch_copper():try:t = yf. Ticker("HG=F")h = t.history(period="3d")if len(h) >= 2:cur = h['Close'].iloc[-1]prev = h['Close'].iloc[-2]return {"price": cur, "change_pct": ((cur-prev)/prev)*100}elif len(h) == 1:return {"price": h['Close'].iloc[-1], "change_pct": 0}except:passreturn None

@st.cache_data(ttl=600)def fetch_nickel():“”“鎳價 — 用 JJN ETN 作為參考，無法取得時用 LME 備用 API”“”try:t = yf. Ticker("JJN")h = t.history(period="3d")if len(h) >= 2 and h['Close'].iloc[-1] > 0:cur = h['Close'].iloc[-1]prev = h['Close'].iloc[-2]return {"price": cur, "change_pct": ((cur-prev)/prev)*100}except:passreturn None

@st.cache_data(ttl=900)def fetch_twd():try:r = requests.get("<https://api.exchangerate.fun/latest?base=USD>", timeout=10)return r.json()["rates"].get("TWD", 31.84)except:return 31.84

# ── 取得資料 ──────────────────────────────────────

twd = fetch_twd()now = datetime.now(TW_TZ)copper = fetch_copper()nickel = fetch_nickel()

# ── HEADER ────────────────────────────────────────

st.markdown(f"""


 

🔩 聖展金屬有限公司 — 即時物料價格看板

 

更新時間：{now.strftime(‘%Y-%m-%d %H:%M:%S’)} (UTC+8) ｜ 每 2 分鐘自動刷新

""", unsafe_allow_html=True)

# ── 公告區 ────────────────────────────────────────

st.markdown("""


📌 **注意事項：**銅價為 COMEX 期貨即時報價；不鏽鋼以鎳價（JJN ETN）作為 304 不鏽鋼原料成本參考（鎳佔成本約 60%）。實際成交價依當日盤價與供應商報價為準。本看板僅供內部參考。

""", unsafe_allow_html=True)

# ── 主內容：三欄 ──────────────────────────────────

c1, c2, c3 = st.columns([3, 3, 2])

def render_table(title, label, spec, unit, data):st.markdown(f"### {title}")if data and data.get("price"):usd = data["price"]ntd = usd * twdchg = data["change_pct"]arrow = "▲" if chg >= 0 else "▼"cls = "price-up" if chg >= 0 else "price-down"st.markdown(f"""

| 品名 | 規格 | 單價 (USD) | 單價 (TWD) | 漲跌 |
| --- | --- | --- | --- | --- |
| {label} | {spec} | ${usd:,.2f}{unit} | NT$ {ntd:,.0f}{unit} | {arrow} {chg:+.2f}% |

""", unsafe_allow_html=True)else:st.warning(f“⚠️ 無法取得{label}即時報價，請確認資料來源”)

with c1:render_table(“🟠 銅 Copper”, “紅銅”, “COMEX 期貨”, “/lb”, copper)

with c2:render_table(“⚙️ 不鏽鋼參考價”, “鎳 (304 參考）”, “JJN ETN”, “”, nickel)

with c3:st.markdown(“### 📋 匯率資訊”)st.markdown(f"""

| USD / TWD | {twd:.2f} |
| --- | --- |

""", unsafe_allow_html=True)st.markdown(“### 📞 聯絡資訊”)st.markdown('

📧 待填寫📱 待填寫

', unsafe_allow_html=True)with st.expander(“📌 免責聲明”):st.caption(“本看板價格僅供內部參考，實際交易依當日報價單為準。”)

# ── 走勢圖 ────────────────────────────────────────

st.markdown("---")st.subheader(“📊 近 7 日價格走勢（銅）”)try:hist = yf. Ticker("HG=F").history(period="7d")if not hist.empty:st.line_chart(pd. DataFrame({“銅 COMEX (USD/lb)”: hist[‘Close’]}), use_container_width=True)except:st.caption(“⚠️ 歷史資料暫無法載入”)