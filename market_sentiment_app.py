import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fredapi import Fred
from datetime import datetime, timedelta
import fear_and_greed
import requests
from PIL import Image
from io import BytesIO




# 🎯 あなたのFRED APIキーを入力（※32桁の英数字）
FRED_API_KEY = "079c18debaecb9ff5976bc2334771349"
fred = Fred(api_key=FRED_API_KEY)

# 🧭 タイトル
st.title("📈 U.S. 10-Year Treasury Yield Dashboard")

# 📅 表示期間の選択
term = st.radio("📅 Select time range", ("Past 1 Week", "Past 1 Month", "Past 3 Months"))

# ⏳ 日付範囲の決定
today = datetime.today()
if term == "Past 1 Week":
    start_date = today - timedelta(days=7)
elif term == "Past 1 Month":
    start_date = today - timedelta(days=30)
elif term == "Past 3 Months":
    start_date = today - timedelta(days=90)

# 📉 データ取得と表示
try:
    df = fred.get_series('DGS10', observation_start=start_date)
    df = df.dropna()
    df = df.rename("Yield")
    df = df.to_frame()
    df.index.name = "Date"

    # Y軸の表示範囲（±0.05マージン）
    y_min = df["Yield"].min() - 0.05
    y_max = df["Yield"].max() + 0.05

    st.subheader(f"📊 U.S. 10-Year Treasury Yield - {term}")
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df.index, df["Yield"], marker='o', color='royalblue', linewidth=2)
    ax.set_title(f"10-Year Treasury Yield Trend - {term}", fontsize=14)
    ax.set_xlabel("Date", fontsize=12)
    ax.set_ylabel("Yield (%)", fontsize=12)
    ax.set_ylim(y_min, y_max)
    ax.grid(True)
    plt.xticks(rotation=45)
    st.pyplot(fig)


except Exception as e:
    st.error(f"Fetch Error: {e}")



# 🎯 あなたのFRED APIキーを入力
FRED_API_KEY = "079c18debaecb9ff5976bc2334771349"
fred = Fred(api_key=FRED_API_KEY)

# 🧭 タイトル
st.title("📈 VIX指数ダッシュボード")

# 📅 表示期間の選択
term = st.radio("📅 表示期間を選択", ("Past 1 Week", "Past 1 Month", "Past 3 Months"))

# ⏳ 日付範囲の決定
today = datetime.today()
if term == "Past 1 Week":
    start_date = today - timedelta(days=7)
elif term == "Past 1 Month":
    start_date = today - timedelta(days=30)
elif term == "Past 3 Months":
    start_date = today - timedelta(days=90)

# 📉 データ取得と表示
try:
    df = fred.get_series('VIXCLS', observation_start=start_date)
    df = df.dropna()
    df = df.rename("VIX")
    df = df.to_frame()
    df.index.name = "日付"

    # Y軸の表示範囲（±5のマージン）
    y_min = df["VIX"].min() - 5
    y_max = df["VIX"].max() + 5

    st.subheader(f"📊 VIX指数の推移 - {term}")
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df.index, df["VIX"], marker='o', color='purple', linewidth=2)
    ax.set_title(f"VIX Index Trend - {term}", fontsize=14)
    ax.set_xlabel("日付", fontsize=12)
    ax.set_ylabel("VIX", fontsize=12)
    ax.set_ylim(y_min, y_max)
    ax.grid(True)
    plt.xticks(rotation=45)
    st.pyplot(fig)
except Exception as e:
    st.error(f"データの取得に失敗しました: {e}")






# Fear & Greed Indexの取得
index = fear_and_greed.get()

# 小数点以下1桁で丸めた値（表示用）
rounded_value = round(index.value, 1)

# インデックス情報を常に表示
st.subheader("📊 Fear & Greed Index")
st.metric(label="Current Index", value=f"{rounded_value} ({index.description})")
st.caption(f"Last updated: {index.last_update.strftime('%Y-%m-%d %H:%M:%S')}")

# 📊 Fear & Greed Index（ゲージ表示）
st.subheader("📊 Fear & Greed Index（ゲージ表示）")

# CNN公式ページへのリンク
cnn_url = "https://edition.cnn.com/markets/fear-and-greed"
st.markdown(f"[🔗 CNN公式のFear & Greed Indexページはこちら]({cnn_url})", unsafe_allow_html=True)


st.subheader("📊 Total Put/Call Ratio（情報リンク）")
st.markdown("[🔗 YChartsのPut/Call Ratioページはこちら](https://ycharts.com/indicators/cboe_equity_put_call_ratio)")



# AAII センチメントのセクション
st.subheader("📊 AAII Sentiment Survey")

# リンクだけ表示（クリック可能）
aaii_url = "https://www.aaii.com/sentimentsurvey"
st.markdown(f"[🔗 AAII公式ページはこちら]({aaii_url})")










