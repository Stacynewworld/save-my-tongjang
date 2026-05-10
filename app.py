import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
import plotly.express as px

# -----------------------------
# 앱 설정
# -----------------------------
st.set_page_config(
    page_title="통장을 지켜라",
    page_icon="🐾",
    layout="centered",
    initial_sidebar_state="collapsed"
)

CSV_URL = "https://docs.google.com/spreadsheets/d/10VceFHamxotfak1QoYfcZiBHl9PDZdPg0pkzYqF7aYE/gviz/tq?tqx=out:csv&sheet=Sheet1"

IMG_BASE_URL = "https://raw.githubusercontent.com/Stacynewworld/save-my-tongjang/main/Characters/"

MONG = IMG_BASE_URL + "mongi_think.png"
NYANG = IMG_BASE_URL + "nyangi_basic.png"
TOGETHER = IMG_BASE_URL + "together_smile.png"

# -----------------------------
# 폰트 + 전체 스타일 (강제 적용)
# -----------------------------
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Jua&display=swap" rel="stylesheet">

<style>
* {
    font-family: 'Jua', sans-serif !important;
}

html, body {
    background-color: #fffaf7;
}

.btn {
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# 앱 제목 (HTML로 강제 적용)
# -----------------------------
st.markdown("""
<div style="
    text-align:center;
    font-size:36px;
    font-weight:bold;
    margin-top:10px;
">
🐾 통장을 지켜라
</div>

<div style="
    text-align:center;
    font-size:16px;
    color:gray;
    margin-bottom:15px;
">
서울에서 살아남기
</div>
""", unsafe_allow_html=True)

st.image(TOGETHER, width=90)

# -----------------------------
# 데이터 로딩
# -----------------------------
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    df = pd.read_csv(CSV_URL)

    # 날짜 완전 정리 (시간 / 9998 방지)
    df["날짜"] = (
        df["날짜"]
        .astype(str)
        .str.split(" ")
        .str[0]
        .str.extract(r"(\d{4}-\d{2}-\d{2})")[0]
    )

    df["금액"] = pd.to_numeric(df["금액"], errors="coerce").fillna(0).astype(int)

except:
    df = pd.DataFrame(columns=["날짜","항목","금액","작성자","메모"])

# -----------------------------
# 입력
# -----------------------------
st.subheader("➕ 지출 입력")

col1, col2, col3 = st.columns(3)

with col1:
    st.image(MONG, width=70)
with col3:
    st.image(NYANG, width=70)

with col2:
    date = st.date_input("날짜", datetime.now())
    category = st.selectbox(
        "항목",
        ["🍱식비-외식","🛒식비-장보기","🏠생필품","🎸여가","✨기타"]
    )
    amount = st.number_input("금액", min_value=0, step=100)
    user = st.radio("사용자", ["승은🐱","상준🐶"], horizontal=True)
    memo = st.text_input("메모")

if st.button("💾 저장"):
    if amount > 0:
        new_row = pd.DataFrame([{
            "날짜": date.strftime("%Y-%m-%d"),
            "항목": category,
            "금액": amount,
            "작성자": user,
            "메모": memo
        }])

        df2 = pd.concat([df, new_row], ignore_index=True)
        conn.update(data=df2)

        st.success("저장 완료 💕")
        st.rerun()

# -----------------------------
# 이번 달
# -----------------------------
st.divider()

this_month = datetime.now().strftime("%Y-%m")
m_df = df[df["날짜"].str[:7] == this_month]

st.subheader("📊 이번 달")

if not m_df.empty:
    st.metric("총 지출", f"{m_df['금액'].sum():,}원")

# -----------------------------
# 분석
# -----------------------------
st.subheader("📊 분석")

tab1, tab2, tab3, tab4 = st.tabs(["📈 월별(3개월)", "🥧 항목별", "📅 연간", "🗑️ 전체+삭제"])

# -----------------------------
# 📈 월별
# -----------------------------
with tab1:
    three_months = (datetime.now() - relativedelta(months=2)).strftime("%Y-%m")

    tmp = df[df["날짜"].str[:7] >= three_months]

    if not tmp.empty:
        month_df = tmp.groupby(tmp["날짜"].str[:7])["금액"].sum().reset_index()
        month_df.columns = ["월", "금액"]

        fig = px.bar(month_df, x="월", y="금액", text_auto=True)
        fig.update_xaxes(type="category")
        st.plotly_chart(fig, use_container_width=True, key="m")

    else:
        st.info("데이터 없음")

# -----------------------------
# 🥧 항목별
# -----------------------------
with tab2:
    if not m_df.empty:
        pie_df = m_df.groupby("항목")["금액"].sum().reset_index()

        fig = px.pie(pie_df, values="금액", names="항목", hole=0.4)
        st.plotly_chart(fig, use_container_width=True, key="p")

    else:
        st.info("이번 달 데이터 없음")

# -----------------------------
# 📅 연간
# -----------------------------
with tab3:
    one_year = (datetime.now() - relativedelta(years=1)).strftime("%Y-%m")

    tmp_y = df[df["날짜"].str[:7] >= one_year]

    if not tmp_y.empty:
        year_df = tmp_y.groupby(tmp_y["날짜"].str[:7])["금액"].sum().reset_index()
        year_df.columns = ["월", "금액"]

        fig = px.bar(year_df, x="월", y="금액", text_auto=True)
        fig.update_xaxes(type="category")
        st.plotly_chart(fig, use_container_width=True, key="y")

    else:
        st.info("최근 1년 데이터 없음")

# -----------------------------
# 🗑️ 삭제
# -----------------------------
with tab4:
    st.subheader("📋 전체 내역")

    if not df.empty:
        df2 = df.copy().reset_index().rename(columns={"index": "id"})

        selected = st.selectbox(
            "삭제할 항목",
            df2["id"].tolist(),
            format_func=lambda x: f"{df2.loc[df2['id']==x,'날짜'].values[0]} | {df2.loc[df2['id']==x,'항목'].values[0]} | {df2.loc[df2['id']==x,'금액'].values[0]}원"
        )

        st.dataframe(df2.drop(columns=["id"]), use_container_width=True)

        if st.button("🗑️ 삭제"):
            new_df = df2[df2["id"] != selected].drop(columns=["id"])
            conn.update(data=new_df)

            st.success("삭제 완료")
            st.rerun()

    else:
        st.info("데이터 없음")