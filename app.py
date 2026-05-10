import streamlit as st
import pandas as pd
from datetime import datetime

# 앱 설정 및 제목
st.set_page_config(page_title="통장을 지켜라", layout="centered")
st.title("🛡️ 통장을 지켜라")
st.subheader("승은 ❤️ 상준 알뜰 가계부")

# 1. 입력 섹션
with st.container():
    st.markdown("### ✍️ 오늘의 소비 내역")
    
    col1, col2 = st.columns(2)
    
    with col1:
        date = st.date_input("날짜", datetime.now())
        # 요청하신 대로 식비 구분 및 주거비 통합 카테고리 적용
        category = st.selectbox("항목", [
            "식비-외식", 
            "식비-장보기", 
            "생필품", 
            "취미", 
            "기타"
        ])
    
    with col2:
        amount = st.number_input("금액 (원)", min_value=0, step=100)
        # 작성자 이름 변경: 승은, 상준
        user = st.radio("누가 썼나요?", ["승은", "상준"], horizontal=True)

    # 저장 버튼
    if st.button("내역 저장하기", use_container_width=True):
        if amount > 0:
            # 추후 구글 스프레드시트 연동 시 실제 데이터가 전송되는 지점
            st.success(f"✅ {user}님의 {category} {amount:,.0f}원 입력 완료!")
            st.balloons() 
        else:
            st.warning("금액을 정확히 입력해주세요.")

# 2. 요약 및 통계 섹션
st.divider()
st.markdown("### 📊 이번 달 지출 현황")

col_a, col_b = st.columns(2)
with col_a:
    st.metric(label="승은 지출", value="0원")
with col_b:
    st.metric(label="상준 지출", value="0원")

st.info("'통장을 지켜라' 시트와 연결되면 실제 합계가 여기에 표시됩니다.")
