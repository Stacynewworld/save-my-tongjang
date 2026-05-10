import streamlit as st
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
import plotly.express as px
from streamlit_gsheets import GSheetsConnection

# -----------------------------
# 기본 설정
# -----------------------------
st.set_page_config(page_title="몽이 & 냥이 가계부", page_icon="🐾", layout="wide")

CSV_URL = "https://docs.google.com/spreadsheets/d/10VceFHamxotfak1QoYfcZiBHl9PDZdPg0pkzYqF7aYE/gviz/tq?tqx=out:csv&sheet=Sheet1"

# -----------------------------
# 상태 (하단 메뉴)
# -----------------------------
if "page" not in st.session_state:
    st.session_state.page = "홈"

def nav(page):
    st.session_state.page = page

# -----------------------------
# 데이터
# -----------------------------
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    df = pd.read_csv(CSV_URL)
    df["날짜"] = pd.to_datetime(df["날짜"], errors="coerce")
    df["금액"] = pd.to_numeric(df["금액"], errors="coerce").fillna(0).astype(int)
except:
    df = pd.DataFrame(columns=["날짜","항목","금액","작성자","메모"])

df = df.dropna(subset=["날짜"])
today = datetime.now()

# -----------------------------
# 스타일 (앱 느낌)
# -----------------------------
st.markdown("""
<style>
.title {
    text-align:center;
    font-size:1.6rem;
    font-weight:bold;
    color:#FF7F50;
    margin-bottom:10px;
}

/* 하단 네비 */
.navbar {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: white;
    display: flex;
    justify-content: space-around;
    padding: 10px 0;
    border-top: 1px solid #eee;
    z-index: 999;
}

.navbtn button {
    background: none;
    border: none;
    font-size: 0.9rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>🐾 몽이 & 냥이 가계부</div>", unsafe_allow_html=True)

# -----------------------------
# 하단 네비게이션 (앱 핵심)
# -----------------------------
st.markdown("<div class='navbar'>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🏠 홈"):
        nav("홈")

with col2:
    if st.button("➕ 입력"):
        nav("입력")

with col3:
    if st.button("📊 통계"):
        nav("통계")

with col4:
    if st.button("📋 전체"):
        nav("전체")

st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 🏠 HOME
# =========================================================
if st.session_state.page == "홈":

    st.subheader("💰 이번 달 요약")

    m_df = df[df["날짜"].dt.strftime("%Y-%m") == today.strftime("%Y-%m")]

    if not m_df.empty:
        st.metric("총 지출", f"{m_df['금액'].sum():,}원")

        fig = px.pie(
            m_df.groupby("항목")["금액"].sum().reset_index(),
            values="금액",
            names="항목",
            hole=0.4
        )
        st.plotly_chart(fig, use_container_width=True)

# =========================================================
# ➕ INPUT
# =========================================================
elif st.session_state.page == "입력":

    st.subheader("➕ 지출 입력")

    with st.form("input_form"):

        date = st.date_input("날짜", datetime.now())

        category = st.selectbox(
            "항목",
            ["🍱식비-외식","🛒식비-장보기","🏠생필품","🎸여가","✨기타"]
        )

        amount = st.number_input("금액", min_value=0, step=100)

        user = st.radio("사용자", ["승은🐱","상준🐶"], horizontal=True)

        memo = st.text_input("메모")

        submitted = st.form_submit_button("💖 저장하기")

        if submitted:
            if amount <= 0:
                st.warning("금액 입력 필요")
            else:
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

# =========================================================
# 📊 STATISTICS
# =========================================================
elif st.session_state.page == "통계":

    st.subheader("📊 월별 분석")

    one_year = today - relativedelta(years=1)
    y_df = df[df["날짜"] >= one_year]

    if not y_df.empty:
        y_df["월"] = y_df["날짜"].dt.to_period("M").astype(str)

        fig = px.bar(
            y_df.groupby("월")["금액"].sum().reset_index(),
            x="월",
            y="금액",
            text_auto=True,
            color_discrete_sequence=["#FF7F50"]
        )

        st.plotly_chart(fig, use_container_width=True)

# =========================================================
# 📋 ALL
# =========================================================
elif st.session_state.page == "전체":

    st.subheader("📋 전체 내역")

    st.data_editor(
        df.sort_values("날짜", ascending=False),
        use_container_width=True,
        num_rows="dynamic"
    )