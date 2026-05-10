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

# 데이터 불러오기 함수 (캐싱 방지를 위해 ttl=0 설정 가능)
def get_data():
    data = pd.read_csv(CSV_URL)
    data['금액'] = pd.to_numeric(data['금액'], errors='coerce').fillna(0)
    return data

df = get_data()

# 1. 입력 섹션
with st.expander("➕ 새로운 지출 기록하기", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("날짜", datetime.now())
        category = st.selectbox("항목", ["식비-외식", "식비-장보기", "생필품", "여가", "기타"])
    with col2:
        amount = st.number_input("금액 (원)", min_value=0, step=100)
        user = st.radio("누가 썼나요?", ["승은", "상준"], horizontal=True)
    
    # 모든 항목에서 메모를 입력할 수 있도록 수정
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
            st.success(f"✅ 저장 완료! ({category})")
            st.balloons()
            st.rerun() # 저장 후 화면 갱신
        else:
            st.warning("금액을 입력해주세요.")

# 2. 삭제 섹션
with st.expander("🗑️ 내역 삭제하기"):
    if not df.empty:
        # 최근 데이터 10개만 보여주며 선택 삭제 (가장 최근이 위로)
        df_for_delete = df.copy()
        df_for_delete['display'] = df_for_delete['날짜'] + " | " + df_for_delete['항목'] + " | " + df_for_delete['금액'].astype(str) + "원"
        
        target_row = st.selectbox("삭제할 내역을 선택하세요", df_for_delete.index, 
                                  format_func=lambda x: df_for_delete.loc[x, 'display'],
                                  index=len(df_for_delete)-1)
        
        if st.button("선택한 내역 삭제", type="primary", use_container_width=True):
            updated_df = df.drop(target_row)
            conn.update(worksheet="Sheet1", data=updated_df)
            st.error("🗑️ 삭제되었습니다.")
            st.rerun()
    else:
        st.write("삭제할 데이터가 없습니다.")

# 3. 조회 섹션
st.divider()
st.markdown("### 📊 지출 리포트")

tab_all, tab_food, tab_life, tab_play, tab_etc = st.tabs(["전체", "식비", "생필품", "여가", "기타"])

with tab_all:
    st.write(f"💰 **총 지출: {df['금액'].sum():,.0f}원**")
    st.dataframe(df.sort_values("날짜", ascending=False), use_container_width=True)

with tab_food:
    food_df = df[df['항목'].str.contains("식비", na=False)]
    eat_out = food_df[food_df['항목'] == "식비-외식"]['금액'].sum()
    grocery = food_df[food_df['항목'] == "식비-장보기"]['금액'].sum()
    
    col_a, col_b = st.columns(2)
    col_a.metric("외식비", f"{eat_out:,.0f}원")
    col_b.metric("장보기", f"{grocery:,.0f}원")
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
