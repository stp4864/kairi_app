import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from st_aggrid import AgGrid, GridOptionsBuilder
from streamlit_autorefresh import st_autorefresh

# 🔄 自動リフレッシュ（60秒ごと）
st_autorefresh(interval=60 * 1000, key="nav_refresh")

st.title("📈 ETF NAV vs 現在値（リアルタイム乖離率 & 出来高付き）")

# 🎯 対象銘柄コード（必要に応じて追加可能）
etf_codes = {
    "2845": "ナスダック100（為替ヘッジなし）",
    "2563": "S&P500（為替ヘッジあり）"
}

# 📊 結果格納リスト
rows = []

for code, name in etf_codes.items():
    try:
        url = f"http://tse.factsetdigitalsolutions.com/iopv/etf?language=jp&code={code}"
        res = requests.get(url)
        soup = BeautifulSoup(res.content, "html.parser")

        table = soup.find("table")
        if table is None:
            raise ValueError("テーブルが見つかりませんでした")

        df = pd.read_html(str(table))[0]

        # 必要項目の抽出
        current_price = pd.to_numeric(df.loc[0, "現在値"], errors="coerce")
        nav = pd.to_numeric(df.loc[0, "インディカティブNAV;"], errors="coerce")
        volume = df.loc[0, "出来高"]

        # 乖離率計算
        kairi = ((current_price - nav) / nav) * 100

        rows.append({
            "銘柄コード": code,
            "銘柄名": name,
            "現在値": current_price,
            "NAV": nav,
            "出来高": volume,
            "乖離率(%)": round(kairi, 2)
        })

    except Exception as e:
        st.error(f"[{code}] {name} の取得に失敗：{e}")

# 🧾 DataFrameに変換＆表示
if rows:
    df = pd.DataFrame(rows)
    df["abs_kairi"] = df["乖離率(%)"].abs()
    df_sorted = df.sort_values(by="abs_kairi", ascending=False).drop(columns=["abs_kairi"])

    # AgGrid設定
    gb = GridOptionsBuilder.from_dataframe(df_sorted)
    gb.configure_default_column(resizable=True, filter=True, sortable=True)
    gb.configure_column("銘柄コード", pinned="left", width=100)
    gb.configure_column("銘柄名", width=180)
    gb.configure_column("現在値", width=100)
    gb.configure_column("NAV", width=100)
    gb.configure_column("出来高", width=100)
    gb.configure_column("乖離率(%)", width=110,
        type=["numericColumn"],
        valueFormatter="x.toFixed(2) + '%'"
    )

    grid_options = gb.build()
    AgGrid(df_sorted, gridOptions=grid_options, height=400, fit_columns_on_grid_load=False)
else:
    st.warning("データが取得できませんでした。")
