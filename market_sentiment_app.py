
import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="マーケット・センチメント分析", layout="wide")
st.title("マーケット・センチメント分析（β版）")

# データを格納するリスト
data = []

# --- AAII強気比率（スクレイピング） ---
try:
    url = "https://www.aaii.com/sentimentsurvey"
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.content, "html.parser")
    bull_ratio_tag = soup.select_one(".sentiment-survey .bullish .percent")
    if bull_ratio_tag:
        bull_ratio = int(bull_ratio_tag.get_text(strip=True).replace("%", ""))
        if bull_ratio > 45:
            judgment = "強気"
        elif bull_ratio < 30:
            judgment = "弱気"
        else:
            judgment = "中立"
        data.append(["AAII 強気比率", f"{bull_ratio}%", judgment])
    else:
        data.append(["AAII 強気比率", "取得失敗", "不明"])
except Exception as e:
    data.append(["AAII 強気比率", "取得エラー", str(e)])

# --- 今後追加予定の指標 ---
data.append(["Fear & Greed Index", "未取得", "未実装"])
data.append(["VIX指数", "未取得", "未実装"])
data.append(["Put/Callレシオ", "未取得", "未実装"])
data.append(["10年債利回り", "未取得", "未実装"])

# DataFrameに変換して表示
df = pd.DataFrame(data, columns=["指標", "現在値", "判定"])

def highlight_judgment(val):
    if "強気" in val:
        return "background-color: lightcoral"
    elif "弱気" in val:
        return "background-color: lightskyblue"
    elif "中立" in val:
        return "background-color: lightgreen"
    return ""

st.dataframe(df.style.applymap(highlight_judgment, subset=["判定"]), use_container_width=True)
