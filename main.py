import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="영화 박스오피스 데이터",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 영화 박스오피스 데이터 분석")

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    df["날짜"] = pd.to_datetime(
        df["날짜"].astype(str),
        format="%Y%m%d",
        errors="coerce"
    )

    df["일관객"] = pd.to_numeric(
        df["일관객"],
        errors="coerce"
    )

    return df


df = load_data()


# 그래프 1
st.divider()
st.header("그래프 1. 영화별 일일 관객 수")

movie_list = sorted(df["영화명"].dropna().unique())

selected_movie = st.selectbox(
    "영화를 선택하세요",
    movie_list
)

movie_df = df[df["영화명"] == selected_movie].copy()
movie_df = movie_df.sort_values("날짜")

fig1 = px.line(
    movie_df,
    x="날짜",
    y="일관객",
    markers=True,
    title=f"{selected_movie} - 일일 관객 수",
    labels={
        "날짜": "날짜",
        "일관객": "일일 관객 수"
    }
)

fig1.update_traces(
    hovertemplate=
    "날짜: %{x|%Y-%m-%d}<br>"
    "관객 수: %{y:,}명"
)

fig1.update_layout(
    hovermode="x unified",
    xaxis=dict(
        tickformat="%Y-%m-%d"
    ),
    yaxis=dict(
        tickformat=","
    ),
    height=500
)

st.plotly_chart(
    fig1,
    use_container_width=True
)


# 그래프 2
st.divider()
st.header("그래프 2. 전체 기간 관객 수 TOP 5 영화")

top5_movies = (
    df.groupby("영화명", as_index=False)["일관객"]
    .sum()
    .sort_values("일관객", ascending=False)
    .head(5)
)

top5_movie_names = top5_movies["영화명"].tolist()

top5_df = df[
    df["영화명"].isin(top5_movie_names)
].copy()

top5_df = top5_df.sort_values(
    ["날짜", "영화명"]
)

fig2 = px.line(
    top5_df,
    x="날짜",
    y="일관객",
    color="영화명",
    markers=True,
    title="전체 기간 관객 수 TOP 5 영화의 일일 관객 수",
    labels={
        "날짜": "날짜",
        "일관객": "일일 관객 수",
        "영화명": "영화"
    }
)

fig2.update_traces(
    hovertemplate=
    "영화: %{fullData.name}<br>"
    "날짜: %{x|%Y-%m-%d}<br>"
    "관객 수: %{y:,}명"
)

fig2.update_layout(
    hovermode="x unified",
    xaxis=dict(
        tickformat="%Y-%m-%d"
    ),
    yaxis=dict(
        tickformat=","
    ),
    legend=dict(
        title="영화",
        itemclick="toggle",
        itemdoubleclick="toggleothers"
    ),
    height=600
)

st.plotly_chart(
    fig2,
    use_container_width=True
)


# 그래프 3
st.divider()
st.header("그래프 3. 날짜별 TOP 10 영화 총 관객 수")

daily_total = (
    df.groupby("날짜", as_index=False)["일관객"]
    .sum()
    .sort_values("날짜")
)

top3_days = (
    daily_total
    .sort_values("일관객", ascending=False)
    .head(3)
)

fig3 = px.area(
    daily_total,
    x="날짜",
    y="일관객",
    title="날짜별 TOP 10 영화 총 관객 수",
    labels={
        "날짜": "날짜",
        "일관객": "총 관객 수"
    }
)

fig3.update_traces(
    hovertemplate=
    "날짜: %{x|%Y-%m-%d}<br>"
    "총 관객 수: %{y:,}명"
)

for _, row in top3_days.iterrows():
    fig3.add_annotation(
        x=row["날짜"],
        y=row["일관객"],
        text=(
            f"{row['날짜'].strftime('%Y-%m-%d')}<br>"
            f"{row['일관객']:,}명"
        ),
        showarrow=True,
        arrowhead=2,
        ax=0,
        ay=-50
    )

fig3.update_layout(
    hovermode="x unified",
    xaxis=dict(
        tickformat="%Y-%m-%d"
    ),
    yaxis=dict(
        tickformat=","
    ),
    height=600
)

st.plotly_chart(
    fig3,
    use_container_width=True
)

st.write("📌 관객 수가 가장 많았던 3일은 그래프에 표시되어 있습니다.")


# 그래프 4
st.divider()
st.header("그래프 4. 전체 기간 관객 수 TOP 10 영화")

movie_summary = (
    df.groupby("영화명")
    .agg(
        total_audience=("일관객", "sum"),
        days_in_top10=("날짜", "nunique")
    )
    .reset_index()
)

top10_movies = (
    movie_summary
    .sort_values("total_audience", ascending=False)
    .head(10)
    .copy()
)

top10_movies = top10_movies.sort_values(
    "total_audience",
    ascending=True
)

fig4 = px.bar(
    top10_movies,
    x="total_audience",
    y="영화명",
    orientation="h",
    title="전체 기간 관객 수 TOP 10 영화",
    labels={
        "영화명": "영화",
        "total_audience": "총 관객 수"
    },
    custom_data=["days_in_top10"]
)

fig4.update_traces(
    hovertemplate=
    "영화: %{y}<br>"
    "총 관객 수: %{x:,}명<br>"
    "TOP 10에 포함된 날짜: %{customdata[0]}일"
)

fig4.update_layout(
    xaxis=dict(
        tickformat=","
    ),
    yaxis=dict(
        categoryorder="array",
        categoryarray=top10_movies["영화명"].tolist()
    ),
    height=600
)

st.plotly_chart(
    fig4,
    use_container_width=True
)


# 그래프 5
st.divider()
st.header("그래프 5. 월별 × 요일별 관객 수 히트맵")

df["month"] = df["날짜"].dt.month

weekday_order = [
    "월요일",
    "화요일",
    "수요일",
    "목요일",
    "금요일",
    "토요일",
    "일요일"
]

weekday_map = {
    0: "월요일",
    1: "화요일",
    2: "수요일",
    3: "목요일",
    4: "금요일",
    5: "토요일",
    6: "일요일"
}

df["weekday"] = df["날짜"].dt.weekday.map(weekday_map)

monthly_weekday = (
    df.groupby(["month", "weekday"], as_index=False)["일관객"]
    .sum()
)

monthly_weekday["weekday"] = pd.Categorical(
    monthly_weekday["weekday"],
    categories=weekday_order,
    ordered=True
)

monthly_weekday = monthly_weekday.sort_values(
    ["month", "weekday"]
)

fig5 = px.density_heatmap(
    monthly_weekday,
    x="weekday",
    y="month",
    z="일관객",
    title="월별 × 요일별 총 관객 수",
    labels={
        "month": "월",
        "weekday": "요일",
        "일관객": "총 관객 수"
    },
    category_orders={
        "weekday": weekday_order,
        "month": list(range(1, 13))
    },
    color_continuous_scale="Blues"
)

fig5.update_traces(
    hovertemplate=
    "%{y}월 / %{x}<br>"
    "총 관객 수: %{z:,}명"
)

fig5.update_layout(
    height=600
)

st.plotly_chart(
    fig5,
    use_container_width=True
)


# 그래프 6
st.divider()
st.header("그래프 6")

st.info("추가 예정입니다.")
