import streamlit as st

# ✅ ページ設定は最初に！
st.set_page_config(page_title="ETF NAV vs 現在値（リアルタイム乖離率）", layout="wide")

import pandas as pd
import requests
from st_aggrid import AgGrid, GridOptionsBuilder
from streamlit_autorefresh import st_autorefresh

# ⏱️ 自動リフレッシュ（60秒）
st_autorefresh(interval=60 * 1000, key="autorefresh")

st.title("📉 ETF NAV vs 現在値（リアルタイム乖離率 & 出来高付き）")

# 対象ETFコード
target_codes = ["2845", "2563", "22248", "2630", "2634", "2521", "2558", "1655", "2247", "2633", "2635", "1557", "1547", "2559", "1540", "1328", "1672", "2036", "2037", "2559", "1554", "1550", "2514", "2563", "316A", "2841", "2632", "2569", "1545", "2840", "2631", "2568", "2846", "2242", "2562", "1546", "2241", "2235", "1679", "1473", "1348", "1475", "1369", "1367", "2621", "1486", "2255", "1368", "1489", "1570", "1458", "1579", "1458", "1367", "1357", "1459", "1360", "1459", "1368", "1472", "1678"]

# 取得元URL
url = "http://tse.factsetdigitalsolutions.com/iopv/table?language=jp"

try:
    response = requests.get(url)
    tables = pd.read_html(response.text)
    df = tables[0]

    df["コード"] = df["コード"].astype(str)
    df = df[df["コード"].isin(target_codes)]

    df["現在値"] = pd.to_numeric(df["現在値"], errors="coerce")
    df["インディカティブNAV;"] = pd.to_numeric(df["インディカティブNAV;"], errors="coerce")
    df["出来高"] = pd.to_numeric(df["出来高"], errors="coerce")
    df["乖離率(%)"] = ((df["現在値"] - df["インディカティブNAV;"]) / df["インディカティブNAV;"]) * 100

    # 並び順（乖離率の絶対値で降順）
    df["abs_乖離率"] = df["乖離率(%)"].abs()
    df = df.sort_values(by="abs_乖離率", ascending=False).drop(columns=["abs_乖離率"])

    # カラム順を調整
    df = df.rename(columns={"インディカティブNAV;": "NAV"})
    order = ["コード", "銘柄名", "現在値", "時刻", "NAV", "出来高", "乖離率(%)"]
    order += [col for col in df.columns if col not in order]
    df = df[order]

    # AgGridで表示
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(resizable=True, filter=True, sortable=True)
    gb.configure_column("コード", pinned="left", width=80)
    gb.configure_column("銘柄名", width=200)
    gb.configure_column("現在値", width=100)
    gb.configure_column("時刻", width=80)
    gb.configure_column("NAV", width=100)
    gb.configure_column("出来高", width=100)
    gb.configure_column("乖離率(%)", type=["numericColumn"], valueFormatter="x.toFixed(2) + '%'", width=100)

    grid_options = gb.build()
    AgGrid(df, gridOptions=grid_options, height=400, fit_columns_on_grid_load=False)

except Exception as e:
    st.error(f"❌ データの取得に失敗しました：{e}")
