import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timezone, timedelta
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="金屬物料價格即時看板", page_icon="🔩", layout="wide")
st_autorefresh(interval=300000, key="auto_refresh")
TW_TZ = timezone(timedelta(hours=8))
FX_URL = "https://api.exchangerate.fun/latest?base=USD"

METALS = {
    "🔶 銅 Copper": "HG=F",
    "🔧 不鏽鋼 (鎳價 Nickel)": "JJN",
}

@st.cache_data(ttl=900)
def fetch_price(ticker):
    try:
        t = yf.Ticker(ticker)
        info = t.fast_info
        p = info.get("lastPrice") or info.get("regularMarketPreviousClose")
        prev = info.get("regularMarketPreviousClose") or p
        chg = ((p - prev) / prev * 100) if p and prev and prev != 0 else 0
        return {"price": p, "change_pct": chg}
    except:
        try:
            hist = t.history(period="2d")
            if len(hist) >= 2:
                p = hist["Close"].iloc[-1]
                prev = hist["Close"].iloc[-2]
                return {"price": p, "change_pct": (p - prev) / prev * 100}
        except:
            return None

@st.cache_data(ttl=900)
def fetch_twd():
    try:
        r = __import__("requests").get(FX_URL, timeout=10)
        return r.json()["rates"].get("TWD", 31.84)
    except:
        return 31.84

st.title("🔩 金屬物料價格即時看板")
st.caption(f"更新：{datetime.now(TW_TZ).strftime('%Y-%m-%d %H:%M:%S')} (UTC+8) ｜ 每 5 分鐘刷新")
twd = fetch_twd()
prices = {l: fetch_price(s) for l, s in METALS.items()}

c1, c2 = st.columns(2)
for c, (l, s) in zip([c1, c2], METALS.items()):
    item = prices.get(l)
    with c:
        if item and item.get("price"):
            u, t = item["price"], item["price"] * twd
            chg = item.get("change_pct", 0)
            st.metric(label=l, value=f"US$ {u:,.2f}", delta=f"NT$ {t:,.0f} ｜ {'🔺' if chg>=0 else '🔻'} {chg:+.2f}%")
            st.caption(f"USD/TWD = {twd:.2f}")
        else:
            st.metric(label=l, value="N/A", delta="無法取得報價")

st.divider()
st.subheader("📊 價格比較")
cd = [{"金屬": l.split(" ")[0], "USD": prices[l]["price"], "TWD": prices[l]["price"]*twd} for l in METALS if prices.get(l) and prices[l].get("price")]
if cd:
    df = pd.DataFrame(cd).set_index("金屬")
    t1, t2 = st.tabs(["USD", "TWD"])
    t1.bar_chart(df["USD"], use_container_width=True)
    t2.bar_chart(df["TWD"], use_container_width=True)

with st.sidebar:
    st.header("📊 資訊")
    st.metric("USD / TWD", f"{twd:.2f}")
    st.caption("銅：COMEX 期貨 (HG=F)")
    st.caption("鎳：iPath Nickel ETN (JJN)")
    st.caption("匯率：exchangerate.fun")
    st.info("💡 不鏽鋼以鎳價為成本參考，佔 304 不鏽鋼原料約 60%。")