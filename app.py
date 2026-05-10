import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

CSV_URL = "https://docs.google.com/spreadsheets/d/10VceFHamxotfak1QoYfcZiBHl9PDZdPg0pkzYqF7aYE/gviz/tq?tqx=out:csv&sheet=Sheet1"

# 앱 설정
st.set_page_config(page_title="통장을 지켜라", layout="centered")
st.title("통장을 지켜라")
st.subheader("승은 ❤️ 상준 알뜰 가계부")

# 구글 시트 연결
conn = st.connection("gsheets", type=GSheetsConnection)

# 데이터 불러오기 함수
def get_data():
    # 시트에서 최신 데이터 가져오기 (pandas 직접 읽기보다 conn 사용 권장)
    data = conn.read(spreadsheet=CSV_URL, usecols=)
    data['금액'] = pd.to_numeric(data['금액'], errors='coerce').fillna(0)
    return data

df = get_data()

# 1. 입력 섹션 (기존과 동일)
with st.expander("➕ 새로운 지출 기록하기", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("날짜", datetime.now())
        category = st.selectbox("항목", ["식비-외식", "식비-장보기", "생필품", "여가", "기타"])
    with col2:
        amount = st.number_input("금액 (원)", min_value=0, step=100)
        user = st.radio("누가 썼나요?", ["승은", "상준"], horizontal=True)
    
    memo = st.text_input("메모 (상세 내용을 적어주세요)")

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
            st.success("✅ 저장되었습니다!")
            st.rerun()

# 2. 조회 및 편집/삭제 섹션
st.divider()
st.markdown("### 📊 지출 리포트 및 관리")
st.info("💡 표에서 내용을 수정하거나 왼쪽 체크박스를 눌러 행을 삭제(Del키)한 후 아래 '변경사항 반영하기'를 눌러주세요.")

tab_all, tab_food, tab_life, tab_play, tab_etc = st.tabs(["전체 관리", "식비", "생필품", "여가", "기타"])

with tab_all:
    # st.data_editor를 사용하여 직접 수정 및 삭제 기능 제공
    edited_df = st.data_editor(
        df, 
        use_container_width=True,
        num_rows="dynamic", # 행 추가/삭제 활성화
        column_config={
            "금액": st.column_config.NumberColumn(format="%d원"),
            "날짜": st.column_config.DateColumn()
        },
        key="data_editor"
    )

    # 변경 사항이 있을 때만 버튼 표시
    if st.button("💾 변경사항 반영하기 (삭제/수정)", type="primary", use_container_width=True):
        conn.update(worksheet="Sheet1", data=edited_df)
        st.success("✅ 구글 시트에 반영되었습니다!")
        st.rerun()

    st.write(f"💰 **현재 총 지출: {edited_df['금액'].sum():,.0f}원**")

# 나머지 탭은 조회 전용 (기존과 동일)
with tab_food:
    food_df = df[df['항목'].str.contains("식비", na=False)]
    st.dataframe(food_df, use_container_width=True)

with tab_life:
    st.dataframe(df[df['항목'] == "생필품"], use_container_width=True)

with tab_play:
    st.dataframe(df[df['항목'] == "여가"], use_container_width=True)

with tab_etc:
    st.dataframe(df[df['항목'] == "기타"], use_container_width=True)
