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
# UI (폰트 강제)
# -----------------------------
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Jua&display=swap" rel="stylesheet">

<style>
html, body, [class*="css"] {
    font-family: 'Jua', sans-serif !important;
    background-color: #fffaf7;
}

.stButton>button {
    background: #f2f2f2 !important;
    color: #333 !important;
    border-radius: 20px;
    border: 1px solid #ddd;
    height: 3rem;
}

.title {
    font-family: 'Jua', sans-serif !important;
    text-align: center;
    font-size: 2.2rem;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# 타이틀
# -----------------------------
st.markdown("<div class='title'>🐾 몽이 & 냥이 가계부</div>", unsafe_allow_html=True)
st.image(TOGETHER, width=90)

# -----------------------------
# 데이터 로딩 (안정 버전)
# -----------------------------
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    df = pd.read_csv(CSV_URL)

    # ✔️ 날짜 완전 고정 (시간 제거)
    df["날짜"] = pd.to_datetime(df["날짜"], errors="coerce").dt.strftime("%Y-%m-%d")

    df["금액"] = pd.to_numeric(df["금액"], errors="coerce").fillna(0).astype(int)

except:
    df = pd.DataFrame(columns=["날짜","항목","금액","작성자","메모"])

today = datetime.now().date()

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

if st.button("저장"):
    if amount > 0:
        new_row = pd.DataFrame([{
            "날짜": date.strftime("%Y-%m-%d"),
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
# 이번 달
# -----------------------------
st.divider()

df_dt = pd.to_datetime(df["날짜"])
this_month = datetime.now().strftime("%Y-%m")
m_df = df[df_dt.dt.strftime("%Y-%m") == this_month]

st.subheader("📊 이번 달")

if not m_df.empty:
    st.metric("총 지출", f"{m_df['금액'].sum():,}원")

# -----------------------------
# 분석
# -----------------------------
st.subheader("📊 분석")

tab1, tab2, tab3 = st.tabs(["📈 월별", "🥧 항목별", "📅 연간"])

# -----------------------------
# 📈 월별 (최근 3개월 정확 버전)
# -----------------------------
with tab1:
    three_months_ago = datetime.now() - relativedelta(months=2)

    tmp = df.copy()
    tmp["날짜_dt"] = pd.to_datetime(tmp["날짜"], errors="coerce")

    tmp = tmp[tmp["날짜_dt"] >= three_months_ago]
    tmp["월"] = tmp["날짜_dt"].dt.strftime("%Y-%m")

    month_df = tmp.groupby("월")["금액"].sum().reset_index()
    month_df = month_df.sort_values("월")

    fig = px.bar(month_df, x="월", y="금액", text_auto=True)
    fig.update_layout(font=dict(family="Jua"))

    st.plotly_chart(fig, use_container_width=True, key="monthly_chart")

# -----------------------------
# 🥧 항목별 (이번 달 + 월 표시)
# -----------------------------
with tab2:
    if not m_df.empty:
        tmp = m_df.copy()
        tmp["월항목"] = this_month + " " + tmp["항목"]

        pie_df = tmp.groupby("월항목")["금액"].sum().reset_index()

        fig = px.pie(
            pie_df,
            values="금액",
            names="월항목",
            hole=0.4
        )

        fig.update_layout(font=dict(family="Jua"))

        st.plotly_chart(fig, use_container_width=True, key="category_chart")

# -----------------------------
# 📅 연간 (최근 1년)
# -----------------------------
with tab3:
    one_year_ago = datetime.now() - relativedelta(years=1)

    y_df = df.copy()
    y_df["날짜_dt"] = pd.to_datetime(y_df["날짜"], errors="coerce")

    y_df = y_df[y_df["날짜_dt"] >= one_year_ago]
    y_df["월"] = y_df["날짜_dt"].dt.strftime("%Y-%m")

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