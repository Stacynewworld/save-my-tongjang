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

CSV_URL = "https://docs.google.com/spreadsheets/d/10VceFHamxotfak1QoYfcZiBHl9PDZdPg0pkzYqF7aYE/gviz/tq?tqx=out:csv&sheet=Sheet1"

IMG_BASE_URL = "https://raw.githubusercontent.com/Stacynewworld/save-my-tongjang/main/Characters/"

MONG = IMG_BASE_URL + "mongi_think.png"
NYANG = IMG_BASE_URL + "nyangi_basic.png"
TOGETHER = IMG_BASE_URL + "together_smile.png"

# -----------------------------
# UI 스타일 설정
# -----------------------------
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Jua&display=swap" rel="stylesheet">
<style>
html, body, [class*="css"] {
    font-family: 'Jua', sans-serif !important;
    background-color: #fffaf7;
}
.title {
    font-size: 2.2rem;
    text-align: center;
    font-family: 'Jua', sans-serif;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>🐾 몽이 & 냥이 가계부</div>", unsafe_allow_html=True)
st.image(TOGETHER, width=90)

# -----------------------------
# 데이터 로딩 및 전처리
# -----------------------------
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # 1. 데이터 불러오기
    df = pd.read_csv(CSV_URL)

    # 2. 날짜 컬럼을 강제로 문자열(YYYY-MM-DD)로 고정
    # 시간 데이터(00:00:00)가 섞여 들어오는 것을 원천 차단합니다.
    df["날짜"] = df["날짜"].astype(str).str.split(" ").str.str.strip()

    # 3. 금액 숫자로 변환
    df["금액"] = pd.to_numeric(df["금액"], errors="coerce").fillna(0).astype(int)

except Exception as e:
    df = pd.DataFrame(columns=["날짜","항목","금액","작성자","메모"])

# -----------------------------
# 입력 영역
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
# 이번 달 지출 요약
# -----------------------------
st.divider()
this_month = datetime.now().strftime("%Y-%m")
m_df = df[df["날짜"].str[:7] == this_month]

st.subheader("📊 이번 달 요약")
if not m_df.empty:
    st.metric("총 지출", f"{m_df['금액'].sum():,}원")

# -----------------------------
# 분석 탭
# -----------------------------
st.subheader("📊 지출 분석")
tab1, tab2, tab3, tab4 = st.tabs(["📈 월별(3개월)", "🥧 항목별", "📅 연간", "🗑️ 전체+삭제"])

# --- 📈 월별 (최근 3개월) ---
with tab1:
    three_months_ago = (datetime.now() - relativedelta(months=2)).strftime("%Y-%m")
    tmp_m = df[df["날짜"].str[:7] >= three_months_ago].copy()
    
    if not tmp_m.empty:
        month_df = tmp_m.groupby(tmp_m["날짜"].str[:7])["금액"].sum().reset_index()
        month_df.columns = ["월", "금액"]

        fig1 = px.bar(month_df, x="월", y="금액", text_auto=True)
        # X축을 카테고리로 고정하여 00:00:00 방지
        fig1.update_xaxes(type='category')
        st.plotly_chart(fig1, use_container_width=True, key="m_chart")
    else:
        st.info("데이터가 없습니다.")

# --- 🥧 항목별 (이번 달) ---
with tab2:
    if not m_df.empty:
        tmp_p = m_df.copy()
        pie_df = tmp_p.groupby("항목")["금액"].sum().reset_index()

        fig2 = px.pie(pie_df, values="금액", names="항목", hole=0.4)
        st.plotly_chart(fig2, use_container_width=True, key="p_chart")
    else:
        st.info("이번 달 데이터가 없습니다.")

# --- 📅 연간 (최근 1년) ---
with tab3:
    one_year_ago = (datetime.now() - relativedelta(years=1)).strftime("%Y-%m")
    tmp_y = df[df["날짜"].str[:7] >= one_year_ago].copy()

    if not tmp_y.empty:
        # 월별로 그룹화
        year_df = tmp_y.groupby(tmp_y["날짜"].str[:7])["금액"].sum().reset_index()
        year_df.columns = ["월", "금액"]

        fig3 = px.bar(year_df, x="월", y="금액", text_auto=True)
        # 🔥 핵심 수정: X축 타입을 'category'로 설정하여 소수점/시간 표시 방지
        fig3.update_xaxes(type='category')
        st.plotly_chart(fig3, use_container_width=True, key="y_chart")
    else:
        st.info("최근 1년 데이터가 없습니다.")

# --- 🗑️ 전체 내역 및 삭제 기능 ---
with tab4:
    st.subheader("📋 전체 내역 (삭제 가능)")
    if not df.empty:
        df_display = df.copy().reset_index().rename(columns={"index": "id"})
        
        selected = st.selectbox(
            "삭제할 항목 선택",
            df_display["id"].tolist(),
            format_func=lambda x: f"{df_display.loc[df_display['id']==x, '날짜'].values} | {df_display.loc[df_display['id']==x, '항목'].values} | {df_display.loc[df_display['id']==x, '금액'].values}원"
        )

        st.dataframe(df, use_container_width=True)

        if st.button("🗑️ 선택 항목 삭제하기"):
            new_df = df_display[df_display["id"] != selected].drop(columns=["id"])
            conn.update(worksheet="Sheet1", data=new_df)
            st.success("삭제되었습니다!")
            st.rerun()
    else:
        st.info("내역이 없습니다.")
