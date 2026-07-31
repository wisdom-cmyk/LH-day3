from pathlib import Path

import pandas as pd
import streamlit as st


st.set_page_config(page_title="서울 소방서 출동거리 분석", page_icon="🚒", layout="wide")

DATA_PATH = Path(__file__).parent / "count_merged.csv"


@st.cache_data
def load_data(path: Path) -> pd.DataFrame:
    """CSV를 불러오고 2020년 대비 출동거리 증가율을 계산합니다."""
    data = pd.read_csv(path)
    data["출동거리_증가율"] = (
        (data["출동거리_2021"] - data["출동거리_2020"])
        / data["출동거리_2020"]
        * 100
    )
    return data.sort_values("출동거리_증가율", ascending=False)


st.title("🚒 서울 소방서 출동거리 증가율")
st.caption("2020년 대비 2021년 출동거리 변화")

if not DATA_PATH.exists():
    st.error("count_merged.csv 파일을 app.py와 같은 폴더에 넣어주세요.")
    st.stop()

df = load_data(DATA_PATH)

col1, col2, col3 = st.columns(3)
col1.metric("소방서 수", f"{len(df)}곳")
col2.metric("평균 증가율", f"{df['출동거리_증가율'].mean():.2f}%")
col3.metric("가장 높은 증가율", f"{df.iloc[0]['출동거리_증가율']:.2f}%")

st.subheader("소방서별 출동거리 증가율")
selected_stations = st.multiselect(
    "확인할 소방서를 선택하세요. 선택하지 않으면 전체를 표시합니다.",
    options=df["fire_station_name"].tolist(),
)

chart_df = df.copy()
if selected_stations:
    chart_df = chart_df[chart_df["fire_station_name"].isin(selected_stations)]

st.bar_chart(
    chart_df.set_index("fire_station_name")["출동거리_증가율"],
    color="#2563eb",
)

st.subheader("상세 데이터")
display_df = chart_df[
    [
        "fire_station_name",
        "출동거리_2020",
        "출동거리_2021",
        "출동거리_증가율",
    ]
].rename(columns={"fire_station_name": "소방서"})

st.dataframe(
    display_df.style.format(
        {
            "출동거리_2020": "{:.2f}",
            "출동거리_2021": "{:.2f}",
            "출동거리_증가율": "{:.2f}%",
        }
    ),
    use_container_width=True,
    hide_index=True,
)

st.download_button(
    "분석 결과 CSV 다운로드",
    data=chart_df.to_csv(index=False).encode("utf-8-sig"),
    file_name="출동거리_증가율_분석.csv",
    mime="text/csv",
)
