import streamlit as st
import requests
from datetime import datetime, timezone, timedelta
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Metal Price Dashboard", page_icon="🔩", layout="wide")
st_autorefresh(interval=120000, key="auto_refresh")
TW_TZ = timezone(timedelta(hours=8))
METALS_API_KEY = st.secrets.get("METALS_DEV_KEY", "")
FX_URL = "https://api.exchangerate.fun/latest?base=USD"
METALS = {"Copper": "copper", "Stainless (Nickel)": "nickel"}

@st.cache_data(ttl=900)
def fetch_metal_prices(api_key):
    if not api_key: return {}
    results = {}
    for name, symbol in METALS.items():
        try:
            url = "https://metals.dev/api/v1/latest"
            params = {"api_key": api_key, "base": "USD", "symbols": symbol}
            resp = requests.get(url, params=params, timeout=15)
            data = resp.json()
            if data.get("status") == "success" and symbol in data.get("data", {}):
                results[name] = data["data"][symbol]
        except Exception:
            results[name] = None
    return results

@st.cache_data(ttl=900)
def fetch_twd_rate():
    try:
        resp = requests.get(FX_URL, timeout=10)
        data = resp.json()
        return data["rates"].get("TWD", 31.84)
    except Exception:
        return 31.84

st.title("Metal Price Dashboard")
now = datetime.now(TW_TZ)
st.caption(f"Updated: {now.strftime('%Y-%m-%d %H:%M:%S')} (UTC+8)")
if not METALS_API_KEY:
    st.warning("API Key not set.")
    st.stop()
with st.spinner("Fetching prices..."):
    metal_data = fetch_metal_prices(METALS_API_KEY)
    twd_rate = fetch_twd_rate()
if not metal_data:
    st.error("Failed to fetch metal prices.")
    st.stop()
cols = st.columns(len(METALS))
for i, (name, symbol) in enumerate(METALS.items()):
    item = metal_data.get(name)
    with cols[i]:
        if item and isinstance(item, dict):
            price_usd = item.get("price", item.get("spot", 0))
            price_twd = price_usd * twd_rate
            st.metric(label=name, value=f"US$ {price_usd:,.2f}", delta=f"NT$ {price_twd:,.0f}")
            st.caption(f"USD/TWD = {twd_rate:.2f}")
        else:
            st.metric(label=name, value="N/A")
with st.sidebar:
    st.header("Info")
    st.metric(label="USD / TWD", value=f"{twd_rate:.2f}")
    st.markdown("- Metals: metals.dev")
    st.markdown("- Forex: exchangerate.fun")
    st.info("Stainless price via LME Nickel.")