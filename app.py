# app.py

import streamlit as stimport requestsfrom datetime import datetime, timezone, timedeltafrom streamlit_autorefresh import st_autorefresh

# ============================================================

# 頁面設定

# ============================================================

st.set_page_config(page_title=“金屬物料價格即時看板”, page_icon=“🔩”, layout=“wide”)

# UI 每 2 分鐘自動刷新（實際 API 請求受 cache TTL 控制）

st_autorefresh(interval=120000, key="auto_refresh")

TW_TZ = timezone(timedelta(hours=8))

# ============================================================

# 設定區 — 請填入你的 API Key

# ============================================================

# 方式一：Streamlit Cloud → 在 secrets.toml 設定

METALS_API_KEY = st.secrets.get("METALS_DEV_KEY", "")

# 方式二：本機測試 → 直接改下面這行

# METALS_API_KEY = "your_metals_dev_api_key_here"

# 免 API Key 的匯率來源（已確認可用）

FX_URL = "<https://api.exchangerate.fun/latest?base=USD>"

# 金屬定義

METALS = {“🔶 銅 Copper”: “copper”,“🔧 不鏽鋼 Stainless （鎳價 Nickel）”: “nickel”,}

# ============================================================

# 快取層 — 15 分鐘內不重複呼叫 API

# ============================================================

@st.cache_data(ttl=900)def fetch_metal_prices(api_key: str) -> dict:“”“從 metals.dev 拉取銅、鎳即時價格（USD/噸）”“”if not api_key: return {}results = {}for name, symbol in METALS.items(): try: url = f“<https://metals.dev/api/v1/latest>“params = {”api_key“: api_key, ”base“: ”USD“, ”symbols“: symbol}resp = requests.get(url, params=params, timeout=15)data = resp.json()# metals.dev 回應格式： {”status“:”success“,”data“:{”copper“:{……}}}if data.get(”status“) == ”success“ and symbol in data.get(”data“, {}): results[name] = data[”data“][symbol]except Exception: results[name] = Nonereturn results

@st.cache_data(ttl=900)def fetch_twd_rate() -> float:“”“從 exchangerate.fun 取得 USD/TWD 匯率”“”try: resp = requests.get(FX_URL, timeout=10)data = resp.json()return data[“rates”].get(“TWD”, 31.84)except Exception: return 31.84 # 預設 fallback

# ============================================================

# 主畫面

# ============================================================

st.title(“🔩 金屬物料價格即時看板”)now = datetime.now(TW_TZ)st.caption(f“更新時間：{now.strftime(‘%Y-%m-%d %H:%M:%S’)} (UTC+8) ｜ ”f“自動刷新：每 2 分鐘 ｜ API 快取：15 分鐘”)

# 檢查 API Key

if not METALS_API_KEY: st.warning(“⚠️ 尚未設定 API Key，請依照下方說明取得免費金鑰後重新部署。”)with st.expander(“📖 如何取得免費 API Key?”): st.markdown(“”“1. 前往 [metals.dev](https://metals.dev) → 點擊 **Get Free API Key**2. 註冊帳號（免費方案：每月 500 次請求）3. 複製 API Key → 貼入 Streamlit Cloud 的 **Secrets**：`METALS_DEV_KEY = “你的金鑰”`4. 重新部署即可“”“)st.stop()

# 撈資料

with st.spinner(“取得即時報價中……”): metal_data = fetch_metal_prices(METALS_API_KEY)twd_rate = fetch_twd_rate()

if not metal_data:st.error(“無法取得金屬報價，請確認 API Key 是否正確或稍後再試。”)st.stop()

# 顯示卡片

cols = st.columns(len(METALS))

for i, (name, symbol) in enumerate(METALS.items()): item = metal_data.get(name)with cols[i]: if item and isinstance(item, dict): price_usd = item.get("price", item.get("spot", 0))change_pct = item.get("change_percentage", 0)

price_twd = price_usd * twd_ratedelta_str = f"NT$ {price_twd:,.0f} ｜ {'🔺' if change_pct >= 0 else '🔻'} {change_pct:+.2f}%"

st.metric(label=name, value=f“US$ {price_usd:,.2f}”, delta=delta_str,)st.caption(f“USD/TWD = {twd_rate:.2f}”)else: st.metric(label=name, value=“—”, delta=“無資料”)

# ============================================================

# 側邊欄

# ============================================================

with st.sidebar: st.header(“📊 看板資訊”)st.metric(label=“USD / TWD 匯率”, value=f“{twd_rate:.2f}”)

st.markdown(“---”)st.markdown(“### 📡 資料來源”)st.markdown(“- 金屬報價：[metals.dev](https://metals.dev)“)st.markdown(”- 外匯匯率：[exchangerate.fun](https://exchangerate.fun)")

st.markdown(“---”)st.markdown(“### ℹ️ 關於不鏽鋼”)st.info(“不鏽鋼無標準化即時報價，此處以 **LME 鎳價**“” 作為 304 不鏽鋼原料成本參考指標。“”鎳佔 304 不鏽鋼原料成本約 60%。“)