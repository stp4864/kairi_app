import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from st_aggrid import AgGrid, GridOptionsBuilder

st.set_page_config(layout="wide")
st.title("NEXT FUNDS 基準価格 vs 現在値（乖離率順）")

codes = ["1306", "1309", "1311", "1319", "1321", "1325", "1328", "1343", "1357", "1472", "1480", "1489", "1545", "1546", "1559", "1560", "1570", "1571", "1577", "1591", "159A", "1615", "1617", "1618", "1619", "1620", "1621", "1622", "1623", "1624", "1625", "1626", "1627", "1628", "1629", "1630", "1631", "1632", "1633", "1678", "1699", "200A", "2083", "2084", "2251", "2510", "2511", "2512", "2513", "2514", "2515", "2518", "2519", "2529", "2529", "2554", "2633", "2634", "2635", "2643", "2647", "2648", "2845", "2846", "2850", "2859", "2860", "2863", "294A", "346A"]
data = []

for code in codes:
    url = f"https://nextfunds.jp/lineup/{code}/?from=code"

    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")

        name_tag = soup.find("h1")
        name = name_tag.get_text(strip=True) if name_tag else "不明"

        current_price_tag = soup.select_one("dt:contains('取引所価格') + dd .fundprice__price")
        if current_price_tag:
            current_str = current_price_tag.get_text(strip=True).replace(",", "").replace("円", "")
            current_price = float(current_str)
        else:
            raise ValueError("現在値が見つかりません")

        base_price_tag = soup.select_one("dt:contains('基準価額') + dd .fundprice__price")
        if base_price_tag:
           base_str = base_price_tag.get_text(strip=True).replace(",", "").replace("円", "").replace("*", "")
           base_raw = float(base_str)
         else:
    raise ValueError("基準価格が見つかりません")


        digits_current = len(str(int(current_price)))
        digits_base = len(str(int(base_raw)))
        base_price = base_raw / (10 ** (digits_base - digits_current)) if digits_base > digits_current else base_raw

        kairi = ((current_price - base_price) / base_price) * 100

        unit_value = "不明"
        dl_tags = soup.find_all("dl", class_="dl__summary-2col")
        for dl in dl_tags:
            dt = dl.find("dt")
            if dt and "受益権口数" in dt.get_text():
                dd = dl.find("dd")
                if dd:
                    unit_value = dd.get_text(strip=True).replace(",", "").replace("口", "")
                    break

        data.append({
            "銘柄コード": code,
            "銘柄名": name,
            "現在値": round(current_price),
            "基準価格": round(base_price),
            "乖離率(%)": round(kairi, 2),
            "受益権口数": unit_value
        })

    except Exception as e:
        st.error(f"取得失敗: [{code}] {url} / 理由: {e}")

if data:
    df = pd.DataFrame(data)
    df["abs_乖離率"] = df["乖離率(%)"].abs()
    df_sorted = df.sort_values(by="abs_乖離率", ascending=False).drop(columns=["abs_乖離率"])

    gb = GridOptionsBuilder.from_dataframe(df_sorted)
    gb.configure_default_column(resizable=True, sortable=True, filter=True)

    # 列の幅調整（必要に応じて微調整OK）
    gb.configure_column("銘柄コード", pinned="left", width=70)
    gb.configure_column("銘柄名", width=100)
    gb.configure_column("現在値", width=70)
    gb.configure_column("基準価格", width=70)
    gb.configure_column("乖離率(%)", width=70, type=["numericColumn"], valueFormatter="x.toFixed(2) + '%'")
    gb.configure_column("受益権口数", width=100)

    grid_options = gb.build()
    AgGrid(df_sorted, gridOptions=grid_options, height=600, fit_columns_on_grid_load=False)
else:
    st.warning("データが取得できませんでした。")
