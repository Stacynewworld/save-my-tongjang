import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 데이터 소스 URL
CSV_URL = "https://docs.google.com/spreadsheets/d/10VceFHamxotfak1QoYfcZiBHl9PDZdPg0pkzYqF7aYE/gviz/tq?tqx=out:csv&sheet=Sheet1"

# 앱 설정
st.set_page_config(page_title="통장을 지켜라", layout="centered")
st.title("통장을 지켜라")
st.subheader("승은 ❤️ 상준 알뜰 가계부")

# 구글 시트 연결
conn = st.connection("gsheets", type=GSheetsConnection)

# 데이터 읽기
df = pd.read_csv(CSV_URL)
df['날짜'] = pd.to_datetime(df['날짜'])
df['금액'] = pd.to_numeric(df['금액'], errors='coerce').fillna(0).astype(int)

# --- 데이터 필터링 (라이브러리 없이 수동 계산) ---
# 오늘 기준 이번 달 포함 최근 3개월 (간단하게 연/월로 필터링)
today = datetime.now()
current_month = today.month
current_year = today.year

def is_recent(row_date):
    diff_months = (today.year - row_date.year) * 12 + (today.month - row_date.month)
    return 0 <= diff_months <= 2

filtered_df = df[df['날짜'].apply(is_recent)].sort_values("날짜", ascending=False)

# 1. 입력 섹션 (기존 유지)
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

# 2. 리포트 섹션
st.divider()
st.markdown("### 📊 지출 리포트 (최근 3개월)")

tab_yearly, tab_monthly, tab_all, tab_food, tab_life, tab_play = st.tabs([
    "📅 연간 현황", "📈 월간 현황", "📋 전체 내역", "🍱 식비", "🏠 생필품", "🎸 여가"
])

# --- 📅 연간 현황 (내장 그래프) ---
with tab_yearly:
    st.write("#### 월별 총 지출 추이")
    df['월'] = df['날짜'].dt.strftime('%Y-%m')
    monthly_total = df.groupby('월')['금액'].sum()
    st.bar_chart(monthly_total)

# --- 📈 월간 현황 (내장 그래프) ---
with tab_monthly:
    this_month_str = today.strftime('%Y-%m')
    st.write(f"#### {this_month_str} 항목별 지출")
    month_df = df[df['날짜'].dt.strftime('%Y-%m') == this_month_str]
    
    if not month_df.empty:
        cat_total = month_df.groupby('항목')['금액'].sum()
        st.bar_chart(cat_total)
        st.write(f"💰 **이번 달 총합: {month_df['금액'].sum():,.0f}원**")
    else:
        st.info("이번 달 내역이 없습니다.")

# --- 📋 전체 내역 (수정/삭제 가능) ---
with tab_all:
    edited_df = st.data_editor(filtered_df, use_container_width=True, num_rows="dynamic", key="editor")
    if st.button("💾 변경사항 반영하기", type="primary"):
        # 필터링되지 않은 데이터(과거 데이터)와 편집된 데이터 합치기
        other_data = df[~df['날짜'].apply(is_recent)]
        final_df = pd.concat([other_data, edited_df], ignore_index=True)
        conn.update(worksheet="Sheet1", data=final_df)
        st.success("✅ 반영되었습니다!")
        st.rerun()

# 나머지 카테고리 조회 탭
with tab_food:
    st.dataframe(filtered_df[filtered_df['항목'].str.contains("식비", na=False)], use_container_width=True)

with tab_life:
    st.dataframe(filtered_df[filtered_df['항목'] == "생필품"], use_container_width=True)

with tab_play:
    st.dataframe(filtered_df[filtered_df['항목'] == "여가"], use_container_width=True)
