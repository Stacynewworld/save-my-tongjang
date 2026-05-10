import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
import plotly.express as px

# 데이터 소스 URL
CSV_URL = "https://docs.google.com/spreadsheets/d/10VceFHamxotfak1QoYfcZiBHl9PDZdPg0pkzYqF7aYE/gviz/tq?tqx=out:csv&sheet=Sheet1"

# 앱 설정
st.set_page_config(page_title="통장을 지켜라", layout="centered")
st.title("통장을 지켜라")
st.subheader("승은 ❤️ 상준 알뜰 가계부")

# 구글 시트 연결
conn = st.connection("gsheets", type=GSheetsConnection)

# 데이터 읽기 (빠른 반영 방식)
try:
    df = pd.read_csv(CSV_URL)
    # 날짜 형식 오류 해결: format='mixed' 추가
    df['날짜'] = pd.to_datetime(df['날짜'], format='mixed')
    df['금액'] = pd.to_numeric(df['금액'], errors='coerce').fillna(0).astype(int)
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    df = pd.DataFrame(columns=["날짜", "항목", "금액", "작성자", "메모"])

# --- 데이터 필터링 (현재 달 포함 이전 2달) ---
today = datetime.now()
three_months_ago = (today - relativedelta(months=2)).replace(day=1)
filtered_df = df[df['날짜'] >= three_months_ago].sort_values("날짜", ascending=False)

# 1. 입력 섹션
with st.expander("➕ 새로운 지출 기록하기", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("날짜", datetime.now())
        category = st.selectbox("항목", ["식비-외식", "식비-장보기", "생필품", "여가", "기타"])
    with col2:
        amount = st.number_input("금액 (원)", min_value=0, step=100)
        user = st.radio("누가 썼나요?", ["승은", "상준"], horizontal=True)
    
    memo = st.text_input("메모 (어디에 썼나요?)")

    if st.button("내역 저장하기", use_container_width=True):
        if amount > 0:
            new_row = pd.DataFrame([{
                "날짜": date.strftime('%Y-%m-%d'),
                "항목": category,
                "금액": amount,
                "작성자": user,
                "메모": memo
            }])
            updated_df = pd.concat([df, new_row], ignore_index=True)
            conn.update(worksheet="Sheet1", data=updated_df)
            st.success("✅ 저장 완료!")
            st.rerun()
        else:
            st.warning("금액을 입력해주세요.")

# 2. 리포트 섹션
st.divider()
st.markdown(f"### 📊 지출 리포트 (최근 3개월)")

tab_yearly, tab_monthly, tab_all, tab_food, tab_life, tab_play = st.tabs([
    "📈 연간 현황", "📅 월간 비중", "💳 전체 내역", "🍽️ 식비", "🏠 생필품", "💫 여가"
])

# --- 📅 연간 현황 탭 (최근 1년 월별 총액) ---
with tab_yearly:
    st.write("#### 월별 총 지출 추이 (최근 1년)")
    one_year_ago = (today - relativedelta(years=1))
    yearly_df = df[df['날짜'] >= one_year_ago].copy()
    
    if not yearly_df.empty:
        # X축을 깔끔하게 '2026-05' 형식의 문자열로 변환
        yearly_df['월'] = yearly_df['날짜'].dt.to_period('M').astype(str)
        monthly_total = yearly_df.groupby('월')['금액'].sum().reset_index()
        
        fig_bar = px.bar(monthly_total, x='월', y='금액', 
                         text_auto=',.0f', 
                         color_discrete_sequence=['#FF4B4B'])
        
        # X축이 시간 순서대로 텍스트 기반으로 표시되도록 강제 설정
        fig_bar.update_xaxes(type='category')
        fig_bar.update_layout(yaxis_title="금액 (원)", xaxis_title="월", showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("데이터가 부족합니다.")

# --- 📈 월간 비중 탭 (이번 달 카테고리 비중) ---
with tab_monthly:
    this_month_str = today.strftime('%Y-%m')
    st.write(f"#### {this_month_str} 카테고리별 비중")
    month_df = df[df['날짜'].dt.strftime('%Y-%m') == this_month_str]
    
    if not month_df.empty:
        cat_total = month_df.groupby('항목')['금액'].sum().reset_index()
        fig_pie = px.pie(cat_total, values='금액', names='항목', 
                         hole=0.4)
        fig_pie.update_traces(textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
        st.write(f"💰 **이번 달 총 지출: {month_df['금액'].sum():,.0f}원**")
    else:
        st.info("이번 달 기록된 지출이 없습니다.")

# --- 📋 전체 내역 (수정 및 삭제 관리) ---
with tab_all:
    st.info("💡 행 선택 후 Del키로 삭제 -> 아래 버튼 클릭!")
    edited_df = st.data_editor(
        filtered_df, 
        use_container_width=True, 
        num_rows="dynamic", 
        key="data_editor_main"
    )
    
    if st.button("💾 변경사항 반영하기", type="primary", use_container_width=True):
        try:
            # 3개월 이전 데이터 + 편집된 데이터 합치기
            old_data = df[df['날짜'] < three_months_ago]
            final_df = pd.concat([old_data, edited_df], ignore_index=True)
            # 날짜 형식을 시트 저장용 문자열로 변환
            final_df['날짜'] = final_df['날짜'].dt.strftime('%Y-%m-%d')
            
            conn.update(worksheet="Sheet1", data=final_df)
            st.success("✅ 구글 시트에 반영되었습니다!")
            st.rerun()
        except Exception as e:
            st.error(f"반영 중 오류 발생: {e}")

# --- 카테고리별 상세 내역 (최근 3개월) ---
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
