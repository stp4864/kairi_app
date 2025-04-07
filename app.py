import streamlit as st
import pandas as pd
import requests
from st_aggrid import AgGrid, GridOptionsBuilder
from streamlit_autorefresh import st_autorefresh  # ← 自動更新追加

# 🔁 自動リフレッシュ（60秒ごと）
st_autorefresh(interval=60 * 1000, key="refresh")

st.title("ETF IOPVスクレイピング")

url = "http://tse.factsetdigitalsolutions.com/iopv/table?language=jp"

try:
    st.write("URLにアクセス中…")
    response = requests.get(url)
    st.success("ページ取得成功！")

    tables = pd.read_html(response.text)
    st.success("テーブル発見！")

    df = tables[0]

    # 数値変換と乖離率追加
    df["現在値"] = pd.to_numeric(df["現在値"], errors="coerce")
    df["インディカティブNAV;"] = pd.to_numeric(df["インディカティブNAV;"], errors="coerce")
    df["乖離率(%)"] = ((df["現在値"] - df["インディカティブNAV;"]) / df["インディカティブNAV;"]) * 100

    
    # 並び替え（最新の時刻 → 乖離率（絶対値）降順 → 出来高降順）
    df_sorted = df.dropna(subset=["乖離率(%)"]).copy()

    # 「時刻」列をdatetime型に変換（例："04/07 10:57" → 2025/04/07 10:57） ※日付は仮に今年で補完
    df_sorted["日時"] = pd.to_datetime("2025/" + df_sorted["時刻"], format="%Y/%m/%d %H:%M", errors='coerce')

    df_sorted["abs_乖離率"] = df_sorted["乖離率(%)"].abs()
    df_sorted["出来高"] = pd.to_numeric(df_sorted["出来高"], errors="coerce").fillna(0)

    df_sorted = df_sorted.sort_values(
        by=["日時", "abs_乖離率", "出来高"],
        ascending=[False, False, False]
    ).drop(columns=["abs_乖離率", "日時"])




    # カラムの順番を指定（「時刻」を「現在値」の右に配置）
    cols = list(df_sorted.columns)
    new_order = []
    for col in ["コード", "銘柄名", "現在値", "時刻", "インディカティブNAV;", "出来高", "乖離率(%)", "ETFスポンサー", "前日比", "前日比１"]:
        if col in cols:
            new_order.append(col)
    for col in cols:
        if col not in new_order:
            new_order.append(col)
    df_sorted = df_sorted[new_order]

    # 列名を短縮して間隔を詰める
    df_sorted = df_sorted.rename(columns={"インディカティブNAV;": "NAV"})

    # AgGridの設定
    gb = GridOptionsBuilder.from_dataframe(df_sorted)
    gb.configure_default_column(resizable=True, filter=True, sortable=True)

    # 「コード」列を固定（左にピン）
    gb.configure_column("コード", pinned="left")

    # 列幅を調整して感覚を詰める
    gb.configure_column("コード", width=70)
    gb.configure_column("銘柄名", width=110)
    gb.configure_column("現在値", width=80)
    gb.configure_column("時刻", width=80)
    gb.configure_column("NAV", width=80)
    gb.configure_column("出来高", width=100)
    gb.configure_column("乖離率(%)", width=90)
    gb.configure_column("ETFスポンサー", width=120)
    gb.configure_column("前日比", width=90)
    gb.configure_column("前日比１", width=90)

    # 乖離率のフォーマット %.2f + %
    gb.configure_column(
        "乖離率(%)",
        type=["numericColumn"],
        valueFormatter="x.toFixed(2) + '%'"
    )

    # 表示
    grid_options = gb.build()
    AgGrid(df_sorted, gridOptions=grid_options, height=500, fit_columns_on_grid_load=False)

except Exception as e:
    st.error(f"エラー発生: {e}")
