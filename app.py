import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
import plotly.express as px

# 데이터 소스 URL
CSV_URL = "https://docs.google.com/spreadsheets/d/10VceFHamxotfak1QoYfcZiBHl9PDZdPg0pkzYqF7aYE/gviz/tq?tqx=out:csv&sheet=Sheet1"

# --- 앱 디자인 설정 ---
st.set_page_config(page_title="몽이 & 냥이 가계부", page_icon="🐾", layout="centered")

# [필독] 본인의 GitHub ID와 저장소 이름으로 꼭 수정해 주세요!
IMG_BASE_URL = "https://github.com/Stacynewworld/save-my-tongjang/blob/main/Characters/"

# 승은 님이 직접 수정하신 파일명들로 업데이트했습니다!
MONG_IMAGES = {
    "기본": IMG_BASE_URL + "mongi_basic.png",
    "웃음": IMG_BASE_URL + "mongi_laugh.png",
    "생각": IMG_BASE_URL + "mongi_think.png",
    "걱정": IMG_BASE_URL + "mongi_worry.png",
    "화남": IMG_BASE_URL + "mongi_angry.png",
}

NYANG_IMAGES = {
    "기본": IMG_BASE_URL + "nyangi_basic.png",
    "신남": IMG_BASE_URL + "nyangi_excited.png",
    "감동": IMG_BASE_URL + "nyangi_moved.png",
    "걱정": IMG_BASE_URL + "nyangi_worry.png",
}

TOGETHER_IMAGES = {
    "미소": IMG_BASE_URL + "together_smile.png",
    "고마워": IMG_BASE_URL + "together_thanks.png",
    "잘됐다": IMG_BASE_URL + "together_cheer.png",
}

# CSS (귀여운 폰트 및 주황색 포인트 디자인)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nanum+Gothic:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Nanum Gothic', sans-serif; color: #444; }
    .title-style { font-size: 2.5rem; font-weight: bold; color: #FF7F50; text-align: center; }
    .stButton>button { border-radius: 30px; background-color: #FF7F50; color: white; font-weight: bold; width: 100%; height: 3rem; border: none; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<p class='title-style'>🐾 몽이 & 냥이 가계부</p>", unsafe_allow_html=True)

# --- 메인 이미지 ---
main_cols = st.columns(3)
main_cols.image(TOGETHER_IMAGES["미소"], use_container_width=True)

# 데이터 연결
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    df = pd.read_csv(CSV_URL)
    df['날짜'] = pd.to_datetime(df['날짜'], format='mixed')
    df['금액'] = pd.to_numeric(df['금액'], errors='coerce').fillna(0).astype(int)
except Exception as e:
    st.error(f"데이터 로딩 실패: {e}")
    df = pd.DataFrame(columns=["날짜", "항목", "금액", "작성자", "메모"])

today = datetime.now()
three_months_ago = (today - relativedelta(months=2)).replace(day=1)
filtered_df = df[df['날짜'] >= three_months_ago].sort_values("날짜", ascending=False)

# --- 1. 입력 섹션 ---
with st.expander("➕ 새로운 지출 기록하기", expanded=False):
    input_cols = st.columns(3)
    
    # 캐릭터 배치
    input_cols.image(MONG_IMAGES["생각"], use_container_width=True)
    input_cols.image(NYANG_IMAGES["기본"], use_container_width=True)
    
    # 입력창 배치 (가운데 칸)
    date = input_cols.date_input("날짜", datetime.now())
    category = input_cols.selectbox("항목", ["🍱식비-외식", "🛒식비-장보기", "🏠생필품", "🎸여가", "✨기타"])
    amount = input_cols.number_input("금액 (원)", min_value=0, step=100)
    user = input_cols.radio("누가 썼나요?", ["승은(냥이)🐱", "상준(몽이)🐶"], horizontal=True)
    memo = input_cols.text_input("메모")

    if st.button("사랑으로 저장하기"):
        if amount > 0:
            user_name = "승은" if "승은" in user else "상준"
            new_row = pd.DataFrame([{"날짜": date.strftime('%Y-%m-%d'), "항목": category[1:], "금액": amount, "작성자": user_name, "메모": memo}])
            updated_df = pd.concat([df, new_row], ignore_index=True)
            conn.update(worksheet="Sheet1", data=updated_df)
            st.success("✅ 저장 완료! 몽이와 냥이가 기뻐해요!")
            st.rerun()

# --- 2. 리포트 섹션 ---
st.divider()
tab_yearly, tab_monthly, tab_all = st.tabs(["📅 연간 현황", "📈 월간 비중", "📋 전체 내역"])

with tab_yearly:
    st.write("#### 월별 총 지출 추이 (최근 1년)")
    one_year_ago = (today - relativedelta(years=1))
    y_df = df[df['날짜'] >= one_year_ago].copy()
    if not y_df.empty:
        y_df['월'] = y_df['날짜'].dt.to_period('M').astype(str)
        m_total = y_df.groupby('월')['금액'].sum().reset_index()
        fig = px.bar(m_total, x='월', y='금액', text_auto=',.0f', color_discrete_sequence=['#FF7F50'])
        fig.update_xaxes(type='category')
        st.plotly_chart(fig, use_container_width=True)

with tab_monthly:
    this_month = today.strftime('%Y-%m')
    st.write(f"#### {this_month} 지출 비중")
    m_df = df[df['날짜'].dt.strftime('%Y-%m') == this_month]
    if not m_df.empty:
        cat_total = m_df.groupby('항목')['금액'].sum().reset_index()
        fig_p = px.pie(cat_total, values='금액', names='항목', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_p, use_container_width=True)
        st.write(f"💰 **이번 달 총 지출: {m_df['금액'].sum():,.0f}원**")

with tab_all:
    # 전체 데이터 편집 (삭제/수정 가능)
    st.data_editor(filtered_df, use_container_width=True, num_rows="dynamic")
