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
    # usecols를 수정하여 오류 해결
    data = conn.read(spreadsheet=CSV_URL)
    # 데이터가 비어있을 경우를 대비해 컬럼 강제 지정
    if data.empty:
        data = pd.DataFrame(columns=["날짜", "항목", "금액", "작성자", "메모"])
    
    # 금액 컬럼 숫자 변환 및 날짜 형식 정리
    data['금액'] = pd.to_numeric(data['금액'], errors='coerce').fillna(0).astype(int)
    return data

# 최신 데이터 로드
df = get_data()

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
            st.success("✅ 저장되었습니다!")
            st.rerun()
        else:
            st.warning("금액을 입력해주세요.")

# 2. 조회 및 편집/삭제 섹션
st.divider()
st.markdown("### 📊 지출 리포트 및 관리")

tab_all, tab_food, tab_life, tab_play, tab_etc = st.tabs(["전체 관리", "식비", "생필품", "여가", "기타"])

with tab_all:
    st.write(f"💰 **현재 총 지출: {df['금액'].sum():,.0f}원**")
    
    # 데이터 에디터: 여기서 수정하거나 행을 선택해 Del 키로 삭제 가능
    edited_df = st.data_editor(
        df, 
        use_container_width=True,
        num_rows="dynamic", # 행 추가/삭제 가능하게 설정
        column_config={
            "금액": st.column_config.NumberColumn(format="%d원"),
            "날짜": st.column_config.TextColumn() # 날짜 편집 편의를 위해 텍스트로 유지
        },
        key="main_editor"
    )

    # 데이터가 변경되었는지 확인 후 저장 버튼 표시
    if st.button("💾 변경사항 최종 반영하기", type="primary", use_container_width=True):
        try:
            conn.update(worksheet="Sheet1", data=edited_df)
            st.success("✅ 구글 시트에 성공적으로 반영되었습니다!")
            st.rerun()
        except Exception as e:
            st.error(f"저장 중 오류가 발생했습니다: {e}")

# 나머지 탭 (필터링된 결과 확인용)
with tab_food:
    st.dataframe(df[df['항목'].str.contains("식비", na=False)], use_container_width=True)

with tab_life:
    st.dataframe(df[df['항목'] == "생필품"], use_container_width=True)

with tab_play:
    st.dataframe(df[df['항목'] == "여가"], use_container_width=True)

with tab_etc:
    st.dataframe(df[df['항목'] == "기타"], use_container_width=True)
