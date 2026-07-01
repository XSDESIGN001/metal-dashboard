import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timezone, timedelta
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="金屬物料價格即時看板", page_icon="🔩", layout="wide")
st_autorefresh(interval=120000, key="auto_refresh")
TW_TZ = timezone(timedelta(hours=8))
METALS_API_KEY = st.secrets.get("METALS_DEV_KEY", "")
FX_URL = "https://api.exchangerate.fun/latest?base=USD"
METALS = {"🔶 銅 Copper": "copper", "🔧 不鏽鋼 Stainless (鎳價)": "nickel"}

@st.cache_data(ttl=900)
def fetch_metal_price(api_key, metal_symbol):
    try:
        url = "https://metals.dev/api/v1/latest"
        params = {"api_key": api_key, "base": "USD", "symbols": metal_symbol}
        resp = requests.get(url, params=params, timeout=15)
        data = resp.json()
        if data.get("status") == "success":
            inner = data.get("data", {})
            if metal_symbol in inner:
                item = inner[metal_symbol]
                if isinstance(item, dict):
                    return {"price": item.get("price") or item.get("spot") or item.get("current") or 0, "change_pct": item.get("change_percentage") or item.get("change") or 0}
                elif isinstance(item, (int, float)):
                    return {"price": item, "change_pct": 0}
        if "rates" in data and metal_symbol in data["rates"]:
            rate = data["rates"][metal_symbol]
            if isinstance(rate, dict):
                return {"price": rate.get("price") or rate.get("current") or 0, "change_pct": rate.get("change_percentage") or 0}
            return {"price": rate, "change_pct": 0}
        return None
    except Exception:
        return None

@st.cache_data(ttl=900)
def fetch_twd_rate():
    try:
        resp = requests.get(FX_URL, timeout=10)
        return resp.json()["rates"].get("TWD", 31.84)
    except Exception:
        return 31.84

st.title("🔩 金屬物料價格即時看板")
now = datetime.now(TW_TZ)
st.caption(f"更新時間：{now.strftime('%Y-%m-%d %H:%M:%S')} (UTC+8) ｜ 每 2 分鐘自動刷新")
if not METALS_API_KEY:
    st.warning("⚠️ 尚未設定 API Key")
    st.stop()

with st.spinner("取得即時報價中⋯"):
    twd_rate = fetch_twd_rate()
    prices = {label: fetch_metal_price(METALS_API_KEY, sym) for label, sym in METALS.items()}

col1, col2 = st.columns(2)
for col, (label, sym) in zip([col1, col2], METALS.items()):
    item = prices.get(label)
    with col:
        if item and item.get("price"):
            usd, twd, chg = item["price"], item["price"] * twd_rate, item.get("change_pct", 0)
            st.metric(label=label, value=f"US$ {usd:,.2f}", delta=f"NT$ {twd:,.0f} ｜ {'🔺' if chg >= 0 else '🔻'} {chg:+.2f}%")
            st.caption(f"USD/TWD = {twd_rate:.2f}")
        else:
            st.metric(label=label, value="N/A", delta="無法取得報價")

st.markdown("---")
st.subheader("📊 價格比較")
chart_data = [{"金屬": label.split(" ")[0], "USD": prices[label]["price"], "TWD": prices[label]["price"] * twd_rate} for label in METALS if prices.get(label) and prices[label].get("price")]
if chart_data:
    df = pd.DataFrame(chart_data)
    t1, t2 = st.tabs(["USD", "TWD"])
    with t1: st.bar_chart(df.set_index("金屬")["USD"], use_container_width=True)
    with t2: st.bar_chart(df.set_index("金屬")["TWD"], use_container_width=True)

with st.sidebar:
    st.header("📊 資訊")
    st.metric("USD / TWD 匯率", f"{twd_rate:.2f}")
    st.divider()
    st.caption("金屬報價：metals.dev")
    st.caption("外匯匯率：exchangerate.fun")
    st.divider()
    st.info("💡 不鏽鋼以 LME 鎳價作為參考（鎳佔 304 不鏽鋼成本約 60%）。")