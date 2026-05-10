import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
import plotly.express as px

# 데이터 소스 URL
CSV_URL = "https://docs.google.com/spreadsheets/d/10VceFHamxotfak1QoYfcZiBHl9PDZdPg0pkzYqF7aYE/gviz/tq?tqx=out:csv&sheet=Sheet1"

# --- 앱 디자인 설정 (캐릭터 & 폰트) ---
st.set_page_config(page_title="몽이 & 냥이 가계부", page_icon="🐾", layout="centered")

# [중요] GitHub에 올린 캐릭터 이미지 주소로 꼭 변경해 주세요!
# 만약 URL이 없다면, 로컬 경로("./mongi_basic.png")도 가능하지만 Streamlit Cloud 배포를 위해 URL을 권장합니다.
IMG_BASE_URL = "https://raw.githubusercontent.com/Stacynewworld/save-my-tongjang/refs/heads/main/Characters/" # 예시 URL

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

# CSS를 이용해 귀여운 폰트와 스타일 적용
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nanum+Gothic:wght@400;700&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Nanum Gothic', sans-serif;
        color: #444; /* 글자색을 약간 부드럽게 */
    }
    
    /* 제목 스타일 */
    .title-style {
        font-size: 3rem;
        font-weight: bold;
        color: #FF7F50; /* 따뜻한 주황색 */
        text-align: center;
        margin-bottom: 0px;
    }
    
    /* 서브제목 스타일 */
    .subheader-style {
        font-size: 1.2rem;
        color: #888;
        text-align: center;
        margin-bottom: 2rem;
    }

    /* 버튼 스타일 (귀엽게 반올림) */
    .stButton>button {
        border-radius: 30px;
        background-color: #FF7F50;
        color: white;
        font-weight: bold;
        border: none;
        padding: 0.5rem 2rem;
        font-size: 1rem;
        width: 100%;
    }
    
    /* 입력 창 스타일 */
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>div {
        border-radius: 15px;
    }
    
    /* 탭 스타일 */
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 1rem;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)


# --- 제목 섹션 ---
st.markdown("<p class='title-style'>🐾 몽이 & 냥이 가계부</p>", unsafe_allow_html=True)
st.markdown("<p class='subheader-style'>우리가 함께 쓰는 다정한 기록</p>", unsafe_allow_html=True)

# 메인 아이콘 (함께 미소)
col_l, col_c, col_r = st.columns()
with col_c:
    st.image(TOGETHER_IMAGES["미소"], use_container_width=True)

# 구글 시트 연결
conn = st.connection("gsheets", type=GSheetsConnection)

# 데이터 읽기 (빠른 반영 방식)
try:
    df = pd.read_csv(CSV_URL)
    df['날짜'] = pd.to_datetime(df['날짜'], format='mixed')
    df['금액'] = pd.to_numeric(df['금액'], errors='coerce').fillna(0).astype(int)
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    df = pd.DataFrame(columns=["날짜", "항목", "금액", "작성자", "메모"])

today = datetime.now()
three_months_ago = (today - relativedelta(months=2)).replace(day=1)
filtered_df = df[df['날짜'] >= three_months_ago].sort_values("날짜", ascending=False)


# --- 1. 입력 섹션 ---
with st.expander("➕ 새로운 지출 기록하기 (몽이 & 냥이에게 알려주기)", expanded=False):
    col1, col2, col3 = st.columns()
    with col1:
        st.image(MONG_IMAGES["생각"], caption="몽이: 어디에 썼지?", use_container_width=True)
    with col3:
        st.image(NYANG_IMAGES["기본"], caption="냥이: 꼼꼼히 적자!", use_container_width=True)
        
    with col2:
        date = st.date_input("날짜", datetime.now())
        category = st.selectbox("항목", ["🍱식비-외식", "🛒식비-장보기", "🏠생필품", "🎸여가", "✨기타"])
        amount = st.number_input("금액 (원)", min_value=0, step=100)
        user = st.radio("누가 썼나요?", ["승은(냥이)🐱", "상준(몽이)🐶"], horizontal=True)
        memo = st.text_input("메모 (상세 내용)")

    if st.button("사랑으로 저장하기", use_container_width=True):
        if amount > 0:
            user_name = "승은" if "승은" in user else "상준"
            new_row = pd.DataFrame([{
                "날짜": date.strftime('%Y-%m-%d'),
                "항목": category[1:], # 이모지 제외하고 저장
                "금액": amount,
                "작성자": user_name,
                "메모": memo
            }])
            updated_df = pd.concat([df, new_row], ignore_index=True)
            conn.update(worksheet="Sheet1", data=updated_df)
            
            # 저장 성공 시 축하 이미지 (잠깐 표시)
            st.image(TOGETHER_IMAGES["잘됐다"], caption="성공! 아껴주셔서 고마워요!", width=200)
            st.success("✅ 저장 완료!")
            st.rerun()
        else:
            st.image(MONG_IMAGES["걱정"], width=100)
            st.warning("금액을 입력해주세요.")


# --- 2. 리포트 섹션 ---
st.divider()
st.markdown(f"### 📊 우리들의 지출 리포트 (최근 3개월)")

tab_yearly, tab_monthly, tab_all, tab_food, tab_life, tab_play = st.tabs([
    "📅 연간 현황", "📈 월간 비중", "📋 전체 내역", "🍱 식비", "🏠 생필품", "🎸 여가"
])

# --- 📅 연간 현황 탭 ---
with tab_yearly:
    col_t_l, col_t_r = st.columns()
    with col_t_l:
        st.write("#### 월별 총 지출 추이 (최근 1년)")
    with col_t_r:
        st.image(MONG_IMAGES["웃음"], use_container_width=True)

    one_year_ago = (today - relativedelta(years=1))
    yearly_df = df[df['날짜'] >= one_year_ago].copy()
    
    if not yearly_df.empty:
        yearly_df['월'] = yearly_df['날짜'].dt.to_period('M').astype(str)
        monthly_total = yearly_df.groupby('월')['금액'].sum().reset_index()
        
        fig_bar = px.bar(monthly_total, x='월', y='금액', 
                         text_auto=',.0f', 
                         color_discrete_sequence=['#FF7F50']) # 따뜻한 주황색 막대
        
        fig_bar.update_xaxes(type='category')
        fig_bar.update_layout(yaxis_title="금액 (원)", xaxis_title="월", showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("데이터가 부족합니다.")

# --- 📈 월간 비중 탭 ---
with tab_monthly:
    this_month_str = today.strftime('%Y-%m')
    col_p_l, col_p_r = st.columns()
    with col_p_l:
        st.image(NYANG_IMAGES["신남"], use_container_width=True)
    with col_p_r:
        st.write(f"#### {this_month_str} 카테고리별 비중")
    
    month_df = df[df['날짜'].dt.strftime('%Y-%m') == this_month_str]
    
    if not month_df.empty:
        cat_total = month_df.groupby('항목')['금액'].sum().reset_index()
        fig_pie = px.pie(cat_total, values='금액', names='항목', 
                         hole=0.4,
                         color_discrete_sequence=px.colors.qualitative.Pastel) # 파스텔톤 색상
        fig_pie.update_traces(textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
        st.write(f"💰 **이번 달 총 지출: {month_df['금액'].sum():,.0f}원**")
    else:
        st.info("이번 달 기록된 지출이 없습니다.")

# --- 📋 전체 내역 ---
with tab_all:
    col_d_l, col_d_r = st.columns()
    with col_d_l:
        st.info("💡 수정 후 아래 버튼 클릭! 삭제는 Del키!")
    with col_d_r:
        st.image(MONG_IMAGES["기본"], use_container_width=True)
        
    edited_df = st.data_editor(
        filtered_df, 
        use_container_width=True, 
        num_rows="dynamic", 
        key="data_editor_main"
    )
    
    if st.button("💾 변경사항 반영하기 (몽이 & 냥이에게 확인받기)", type="primary", use_container_width=True):
        try:
            old_data = df[df['날짜'] < three_months_ago]
            final_df = pd.concat([old_data, edited_df], ignore_index=True)
            final_df['날짜'] = final_df['날짜'].dt.strftime('%Y-%m-%d')
            conn.update(worksheet="Sheet1", data=final_df)
            st.image(TOGETHER_IMAGES["고마워"], caption="수정 완료! 꼼꼼한 관리 칭찬해요!", width=200)
            st.success("✅ 구글 시트에 반영되었습니다!")
            st.rerun()
        except Exception as e:
            st.image(NYANG_IMAGES["걱정"], width=100)
            st.error(f"반영 중 오류 발생: {e}")

# --- 카테고리별 상세 내역 ---
with tab_food:
    f_df = filtered_df[filtered_df['항목'].str.contains("식비", na=False)]
    st.metric("식비 합계", f"{f_df['금액'].sum():,.0f}원")
    st.dataframe(f_df, use_container_width=True)

with tab_life:
    l_df = filtered_df[filtered_df['항목'] == "생필품"]
    st.metric("생필품 합계", f"{l_df['금액'].sum():,.0f}원")
    st.dataframe(l_df, use_container_width=True)

with tab_play:
    p_df = filtered_df[filtered_df['항목'] == "여가"]
    st.metric("여가 합계", f"{p_df['금액'].sum():,.0f}원")
    st.dataframe(p_df, use_container_width=True)
