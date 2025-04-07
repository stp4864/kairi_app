import streamlit as st
import pandas as pd
from datetime import datetime
from fredapi import Fred
import fear_and_greed

# FRED APIキー
FRED_API_KEY = "079c18debaecb9ff5976bc2334771349"
fred = Fred(api_key=FRED_API_KEY)

# Streamlit設定
st.set_page_config(page_title="Fear & Greed Meter", layout="centered")
st.title("\U0001F9E0 Fear & Greed メーター（自動判定）")

# === データ取得 ===
try:
    vix_value = fred.get_series('VIXCLS')[-1]
except:
    vix_value = None
    st.error("VIXの取得に失敗しました")

try:
    fg_index = fear_and_greed.get()
    fg_value = round(fg_index.value, 1)
except:
    fg_value = None
    st.error("Fear & Greed Indexの取得に失敗しました")

# 入力欄
st.subheader("\U0001F6E0 補助データ（必要に応じて手動入力）")
put_call = st.number_input("Put/Call Ratio（例: 0.90）", value=0.9)
aaii_bullish = st.slider("AAII Bullish（%）", 0, 100, 33)

# === スコア化関数 ===
def vix_score(vix):
    if vix is None:
        return 50
    elif vix >= 40:
        return 0
    elif vix <= 12:
        return 100
    else:
        return int((40 - vix) / (40 - 12) * 100)

def fg_score(fg):
    if fg is None:
        return 50
    return int(fg)

def put_call_score(ratio):
    if ratio >= 1.5:
        return 100
    elif ratio <= 0.7:
        return 0
    else:
        return int((ratio - 0.7) / (1.5 - 0.7) * 100)

def aaii_score(pct):
    if pct <= 20:
        return 0
    elif pct <= 30:
        return 25
    elif pct <= 40:
        return 50
    elif pct <= 50:
        return 70
    else:
        return 90

# スコア算出
vix_s = vix_score(vix_value)
fg_s = fg_score(fg_value)
put_s = put_call_score(put_call)
aaii_s = aaii_score(aaii_bullish)
total_score = vix_s + fg_s + put_s + aaii_s

# 判定
if total_score <= 80:
    status = "\U0001F631 極端な恐怖（売られすぎ）"
elif total_score <= 160:
    status = "\U0001F61F 弱気（Fear）"
elif total_score <= 240:
    status = "\U0001F610 中立（Neutral）"
elif total_score <= 320:
    status = "\U0001F603 強気（Greed）"
else:
    status = "\U0001F973 極端な強気（バブル警戒）"

# === 表示 ===
st.markdown("## \U0001F3AF 判定結果")
st.markdown(f"### 総合スコア： **{total_score}/400 → {status}**")

st.markdown("### \U0001F522 各スコア詳細")
st.write(f"- **VIX スコア**：{vix_s}/100（現在値: {vix_value if vix_value else 'N/A'}）")
st.write(f"- **Fear & Greed スコア**：{fg_s}/100（現在値: {fg_value if fg_value else 'N/A'}）")
st.write(f"- **Put/Call スコア**：{put_s}/100（現在値: {put_call}）")
st.write(f"- **AAII スコア**：{aaii_s}/100（現在値: {aaii_bullish}%）")

st.caption("※スコアは目安としてご利用ください。")

# 追加リンク表示
st.subheader("\U0001F4CA Fear & Greed Index")
st.metric(label="Current Index", value=f"{fg_value} ({fg_index.description})")
st.caption(f"Last updated: {fg_index.last_update.strftime('%Y-%m-%d %H:%M:%S')}")
st.markdown("[🔗 CNN公式のFear & Greed Indexページはこちら](https://edition.cnn.com/markets/fear-and-greed)")

st.subheader("\U0001F4CA Total Put/Call Ratio（情報リンク）")
st.markdown("[🔗 YChartsのPut/Call Ratioページはこちら](https://ycharts.com/indicators/cboe_equity_put_call_ratio)")

st.subheader("\U0001F4CA AAII Sentiment Survey")
st.markdown("[🔗 AAII公式ページはこちら](https://www.aaii.com/sentimentsurvey)")
