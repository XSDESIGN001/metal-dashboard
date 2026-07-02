# app.py

import streamlit as st
import yfinance as yf
import requests
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
        ("砲金", 75), ("C3青銅屑 (油水4%↓)", 60), ("大青", 60),
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
.info-section { background:#fafafa; border:1px solid #e0e0e0;
    border-radius:6px; padding:20px 24px; margin-bottom:16px; font-size:14px; color:#333; line-height:1.8; }
.info-section b { color:#1a5276; }
.footer-section { text-align:center; padding:20px; color:#666; font-size:13px; }
.footer-section a { color:#2980b9; text-decoration:none; }
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

st.markdown("---")
st.markdown("""
<div class="info-section">
<b>為了提供您最即時、高效的物料處置服務，請務必詳閱以下出貨規範：</b><br><br>
<b>動態報價機制：</b>因國際銅價波動劇烈，本公司實際成交價格均依據客戶貨量、物料品質、訂單類別，並錨定倫敦金屬交易所（LME）之即時盤價進行動態浮動調整。<br><br>
<b>出貨前請先加 LINE 預約：</b>為確保您的出貨權益，出貨前請直接加入官方 LINE，並提供物料照片與預估數量。雙方於線上確認當日報價後，方能為您安排後續的進貨、送貨時間。<br><br>
<b>實際價格以現場判定為主：</b>來貨物料需經過基本整理，若現場實際卸貨之品質、純度與前期照片存在落差，本公司將以現場專業檢測後之最終報價為主。<br><br>
<b>當日進料限額管控：</b>為維持廠區產能平衡，全品項訂單皆設有每日限額。若當日收貨量達上限即會停止接單，送貨前請務必先來電確認。<br><br>
<b>訊息覆蓋提醒：</b>若官方 LINE 於商務尖峰時間未即時回覆，可能是訊息量過大遭到覆蓋，請您再次發送訊息，我們將安排專人以最快速度為您對接。<br><br>
洪邦金屬為政府立案之甲級廢棄物清除機構，流程 100% 合法合規，值得信賴。我們不僅具備成熟的國內外多元金屬循環與貿易通路，更與國內頂級甲級處理廠深度合作，協助科技產業與製造業無縫對接 ESG 供應鏈審查，杜絕任何環保違規風險。<br><br>
<b>連絡電話/LINE：09XX000123</b>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="info-section">
<b>【免責聲明】</b><br><br>
<b>報價參考性質：</b>本官網及相關廣告看板上所展示之金屬價格、數據僅供海內外客戶參考，並不視為任何形式的成交承諾或要約。<br><br>
<b>有效報價認定：</b>所有實際收購價格與合約內容，必須經由本公司業務窗口透過電話、官方 LINE 或書面確認後方為有效報價。在雙方正式確認前，本站任何資訊均不構成法律上的交易要約。
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="footer-section">
<h3>洪邦金屬股份有限公司</h3>
<p><a href="https://www.hbmetal.com" target="_blank">www.hbmetal.com</a></p>
<br>
<div style="display:inline-block; border:1px solid #ddd; padding:10px; background:#fff;">
    <div style="width:150px; height:150px; background:#f0f0f0; display:flex; align-items:center; justify-content:center; color:#bbb; font-size:12px;">
        LINE<br>QR CODE
    </div>
</div>
<p style="margin-top:8px; font-size:13px;">洪邦金屬官方LINE</p>
</div>
""", unsafe_allow_html=True)
