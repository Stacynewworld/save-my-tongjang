import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
import plotly.express as px

# -----------------------------
# 기본 설정
# -----------------------------
st.set_page_config(
    page_title="몽이 & 냥이 가계부",
    page_icon="🐾",
    layout="centered"
)

# -----------------------------
# 데이터
# -----------------------------
CSV_URL = "https://docs.google.com/spreadsheets/d/10VceFHamxotfak1QoYfcZiBHl9PDZdPg0pkzYqF7aYE/gviz/tq?tqx=out:csv&sheet=Sheet1"

IMG_BASE_URL = "https://raw.githubusercontent.com/Stacynewworld/save-my-tongjang/main/Characters/"

MONG = IMG_BASE_URL + "mongi_think.png"
NYANG = IMG_BASE_URL + "nyangi_basic.png"
TOGETHER = IMG_BASE_URL + "together_smile.png"

# -----------------------------
# 🎨 스타일 (폰트 최대 고정)
# -----------------------------
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Jua&display=swap" rel="stylesheet">

<style>
html, body, [class*="css"] {
    font-family: 'Jua', sans-serif !important;
    background-color: #fffaf7;
}

/* 버튼 회색 (주황 제거) */
.stButton>button {
    background: #f2f2f2 !important;
    color: #333 !important;
    border-radius: 20px;
    border: 1px solid #ddd;
    height: 3rem;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# 타이틀
# -----------------------------
st.markdown("<h2 style='text-align:center;'>🐾 몽이 & 냥이 가계부</h2>", unsafe_allow_html=True)
st.image(TOGETHER, width=90)

# -----------------------------
# 데이터 로딩 (핵심 안정화)
# -----------------------------
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    df = pd.read_csv(CSV_URL)

    # ✔️ 시간 완전 제거 (핵심)
    df["날짜"] = pd.to_datetime(df["날짜"], errors="coerce").dt.date

    df["금액"] = pd.to_numeric(df["금액"], errors="coerce").fillna(0).astype(int)

except:
    df = pd.DataFrame(columns=["날짜","항목","금액","작성자","메모"])

today = datetime.now().date()

# -----------------------------
# ➕ 입력 영역
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

if st.button("저장"):
    if amount > 0:
        new_row = pd.DataFrame([{
            "날짜": date,
            "항목": category,
            "금액": amount,
            "작성자": user,
            "메모": memo
        }])

        df2 = pd.concat([df, new_row], ignore_index=True)
        conn.update(worksheet="Sheet1", data=df2)

        st.success("저장 완료 💕")
        st.rerun()

# -----------------------------
# 📊 이번 달 요약
# -----------------------------
st.divider()

this_month = datetime.now().strftime("%Y-%m")
m_df = df[pd.to_datetime(df["날짜"]).dt.strftime("%Y-%m") == this_month]

st.subheader("📊 이번 달")

if not m_df.empty:
    st.metric("총 지출", f"{m_df['금액'].sum():,}원")

# -----------------------------
# 📊 분석 탭
# -----------------------------
st.subheader("📊 분석")

tab1, tab2, tab3 = st.tabs(["📈 월별", "🥧 항목별", "📅 연간"])

# -----------------------------
# 📈 월별 (최근 3개월)
# -----------------------------
with tab1:
    three_months = datetime.now() - relativedelta(months=2)

    tmp = df[pd.to_datetime(df["날짜"]) >= three_months].copy()
    tmp["월"] = pd.to_datetime(tmp["날짜"]).dt.strftime("%Y-%m")

    month_df = tmp.groupby("월")["금액"].sum().reset_index()

    fig = px.bar(month_df, x="월", y="금액", text_auto=True)
    fig.update_layout(font=dict(family="Jua"))

    st.plotly_chart(fig, use_container_width=True, key="monthly_chart")

# -----------------------------
# 🥧 항목별 (이번 달)
# -----------------------------
with tab2:
    if not m_df.empty:
        pie_df = m_df.groupby("항목")["금액"].sum().reset_index()

        fig = px.pie(
            pie_df,
            values="금액",
            names="항목",
            hole=0.4
        )

        fig.update_layout(font=dict(family="Jua"))

        st.plotly_chart(fig, use_container_width=True, key="category_chart")

# -----------------------------
# 📅 연간 (최근 1년)
# -----------------------------
with tab3:
    one_year = datetime.now() - relativedelta(years=1)

    y_df = df[pd.to_datetime(df["날짜"]) >= one_year].copy()
    y_df["월"] = pd.to_datetime(y_df["날짜"]).dt.strftime("%Y-%m")

    year_df = y_df.groupby("월")["금액"].sum().reset_index()

    fig = px.bar(year_df, x="월", y="금액", text_auto=True)
    fig.update_layout(font=dict(family="Jua"))

    st.plotly_chart(fig, use_container_width=True, key="yearly_chart")

# -----------------------------
# 전체 내역
# -----------------------------
st.subheader("📋 전체 내역")

st.data_editor(
    df.sort_values("날짜", ascending=False),
    use_container_width=True,
    num_rows="dynamic"
)