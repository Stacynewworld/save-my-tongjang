import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. 데이터 읽기 (가장 빨랐던 첫 번째 방식 그대로)
CSV_URL = "https://docs.google.com/spreadsheets/d/10VceFHamxotfak1QoYfcZiBHl9PDZdPg0pkzYqF7aYE/gviz/tq?tqx=out:csv&sheet=Sheet1"

# 앱 설정
st.set_page_config(page_title="통장을 지켜라", layout="centered")
st.title("통장을 지켜라")
st.subheader("승은 ❤️ 상준 알뜰 가계부")

# 구글 시트 연결 (수정/삭제 기능을 위해 필요)
conn = st.connection("gsheets", type=GSheetsConnection)

# 최신 데이터 읽기
df = pd.read_csv(CSV_URL)
df['금액'] = pd.to_numeric(df['금액'], errors='coerce').fillna(0).astype(int)

# 2. 입력 섹션
with st.expander("➕ 새로운 지출 기록하기", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("날짜", datetime.now())
        category = st.selectbox("항목", ["식비-외식", "식비-장보기", "생필품", "여가", "기타"])
    with col2:
        amount = st.number_input("금액 (원)", min_value=0, step=100)
        user = st.radio("누가 썼나요?", ["승은", "상준"], horizontal=True)
    
    # [수정 1] 메모 입력칸을 밖으로 빼서 모든 항목에서 쓸 수 있게 함
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
            
            # 저장 기능
            conn.update(worksheet="Sheet1", data=updated_df)
            st.success("✅ 저장 완료!")
            st.rerun() # 즉시 반영을 위해 새로고침
        else:
            st.warning("금액을 입력해주세요.")

# 3. 조회 및 삭제 섹션
st.divider()
st.markdown("### 📊 지출 리포트")

# [수정 2] '전체' 탭에서 삭제 기능 추가
tab_all, tab_food, tab_life, tab_play, tab_etc = st.tabs(["전체/관리", "식비", "생필품", "여가", "기타"])

with tab_all:
    st.write(f"💰 **총 지출: {df['금액'].sum():,.0f}원**")
    
    # st.data_editor를 사용하면 리스트에서 바로 지울 수 있습니다.
    # 행을 클릭하고 Delete키를 누른 후 아래 버튼을 누르면 삭제됩니다.
    edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic", key="editor")
    
    if st.button("💾 변경사항(수정/삭제) 반영하기", type="primary"):
        conn.update(worksheet="Sheet1", data=edited_df)
        st.success("✅ 반영되었습니다!")
        st.rerun()

# 나머지 탭들은 원래 코드 방식 유지
with tab_food:
    food_df = df[df['항목'].str.contains("식비", na=False)]
    st.write(f"🍱 **식비 총액: {food_df['금액'].sum():,.0f}원**")
    st.dataframe(food_df, use_container_width=True)

with tab_life:
    life_df = df[df['항목'] == "생필품"]
    st.metric("생필품 합계", f"{life_df['금액'].sum():,.0f}원")
    st.dataframe(life_df, use_container_width=True)

with tab_play:
    play_df = df[df['항목'] == "여가"]
    st.metric("여가 합계", f"{play_df['금액'].sum():,.0f}원")
    st.dataframe(play_df, use_container_width=True)

with tab_etc:
    etc_df = df[df['항목'] == "기타"]
    st.metric("기타 합계", f"{etc_df['금액'].sum():,.0f}원")
    st.dataframe(etc_df, use_container_width=True)
