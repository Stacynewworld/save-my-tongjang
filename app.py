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
# 🎀 귀여운 UI 테마
# -----------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Jua&display=swap');

html, body {
    font-family: 'Jua', sans-serif;
    background-color: #fffaf7;
}

/* 제목 */
.title {
    text-align:center;
    font-size:2rem;
    color:#FF7F50;
    margin-bottom:10px;
}

/* 카드 스타일 */
.card {
    background: white;
    padding: 15px;
    border-radius: 20px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    margin-bottom: 12px;
}

/* 버튼 */
.stButton>button {
    width: 100%;
    height: 3rem;
    border-radius: 25px;
    background: #FF7F50;
    color: white;
    font-weight: bold;
    font-size: 1rem;
    border: none;
}

/* 입력창 */
input, selectbox, textarea {
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# 타이틀 + 캐릭터
# -----------------------------
st.markdown("<div class='title'>🐾 몽이 & 냥이 가계부</div>", unsafe_allow_html=True)
st.image(TOGETHER, width=100)

# -----------------------------
# 데이터 로딩
# -----------------------------
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    df = pd.read_csv(CSV_URL)

    # 시간 제거 (핵심)
    df["날짜"] = pd.to_datetime(df["날짜"], errors="coerce").dt.normalize()

    df["금액"] = pd.to_numeric(df["금액"], errors="coerce").fillna(0).astype(int)

except:
    df = pd.DataFrame(columns=["날짜","항목","금액","작성자","메모"])

today = pd.to_datetime("today").normalize()
df = df.dropna(subset=["날짜"])

# -----------------------------
# 🐱 입력 카드
# -----------------------------
st.markdown("<div class='card'>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.image(MONG, width=70)

with col3:
    st.image(NYANG, width=70)

with col2:
    st.subheader("➕ 지출 입력")

    date = st.date_input("날짜", datetime.now())

    category = st.selectbox(
        "항목",
        ["🍱식비-외식","🛒식비-장보기","🏠생필품","🎸여가","✨기타"]
    )

    amount = st.number_input("금액", min_value=0, step=100)

    user = st.radio("누가 썼나요?", ["승은🐱","상준🐶"], horizontal=True)

    memo = st.text_input("메모")

st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# 저장 버튼
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

        st.success("몽이랑 냥이가 좋아해요 💕")
        st.rerun()

# -----------------------------
# 📊 이번 달 요약 카드
# -----------------------------
st.markdown("<div class='card'>", unsafe_allow_html=True)

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

st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# 📋 전체 내역 카드
# -----------------------------
st.markdown("<div class='card'>", unsafe_allow_html=True)

st.subheader("📋 전체 내역")

st.data_editor(
    df.sort_values("날짜", ascending=False),
    use_container_width=True,
    num_rows="dynamic"
)

st.markdown("</div>", unsafe_allow_html=True)