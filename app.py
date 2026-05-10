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

MONG_IMAGES = {
    "생각": IMG_BASE_URL + "mongi_think.png",
}

NYANG_IMAGES = {
    "기본": IMG_BASE_URL + "nyangi_basic.png",
}

TOGETHER_IMAGES = {
    "미소": IMG_BASE_URL + "together_smile.png",
}

# -----------------------------
# 스타일 (모바일 안정)
# -----------------------------
st.markdown("""
<style>
html, body {
    font-family: 'Nanum Gothic', sans-serif;
}
.title {
    text-align:center;
    font-size:1.7rem;
    font-weight:bold;
    color:#FF7F50;
    margin-bottom:10px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>🐾 몽이 & 냥이 가계부</div>", unsafe_allow_html=True)

# -----------------------------
# 메인 이미지 (작게 고정)
# -----------------------------
cols = st.columns(3)

with cols[1]:
    st.image(TOGETHER_IMAGES["미소"], width=90)

# -----------------------------
# 데이터 로딩
# -----------------------------
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    df = pd.read_csv(CSV_URL)

    # ⭐ 핵심: 시간 제거 (00:00:00 문제 해결)
    df["날짜"] = pd.to_datetime(df["날짜"], errors="coerce").dt.normalize()

    df["금액"] = pd.to_numeric(df["금액"], errors="coerce").fillna(0).astype(int)

except:
    df = pd.DataFrame(columns=["날짜","항목","금액","작성자","메모"])

# -----------------------------
# 기간 필터
# -----------------------------
today = pd.to_datetime("today").normalize()
three_months_ago = today - relativedelta(months=2)

df = df.dropna(subset=["날짜"])
filtered_df = df[df["날짜"] >= three_months_ago].sort_values("날짜", ascending=False)

# -----------------------------
# 입력 섹션 (캐릭터 작게 고정)
# -----------------------------
st.subheader("➕ 지출 입력")

col1, col2, col3 = st.columns(3)

with col1:
    st.image(MONG_IMAGES["생각"], width=70)   # ⭐ 핵심 수정

with col3:
    st.image(NYANG_IMAGES["기본"], width=70)  # ⭐ 핵심 수정

with col2:
    date = st.date_input("날짜", datetime.now())

    category = st.selectbox(
        "항목",
        ["🍱식비-외식","🛒식비-장보기","🏠생필품","🎸여가","✨기타"]
    )

    amount = st.number_input("금액", min_value=0, step=100)

    user = st.radio("사용자", ["승은🐱","상준🐶"], horizontal=True)

    memo = st.text_input("메모")

# -----------------------------
# 저장
# -----------------------------
if st.button("💖 저장하기"):
    if amount <= 0:
        st.warning("금액을 입력해주세요")
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
        st.rerun()

# -----------------------------
# 이번 달 요약
# -----------------------------
st.divider()

st.subheader("📊 이번 달 요약")

this_month = today.strftime("%Y-%m")
m_df = df[df["날짜"].dt.strftime("%Y-%m") == this_month]

if not m_df.empty:
    st.metric("총 지출", f"{m_df['금액'].sum():,}원")

    fig = px.pie(
        m_df.groupby("항목")["금액"].sum().reset_index(),
        values="금액",
        names="항목",
        hole=0.4
    )

    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# 전체 내역
# -----------------------------
st.subheader("📋 전체 내역")

st.data_editor(
    filtered_df,
    use_container_width=True,
    num_rows="dynamic"
)