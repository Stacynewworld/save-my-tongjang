import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 앱 설정
st.set_page_config(page_title="통장을 지켜라", layout="centered")
st.title("통장을 지켜라")
st.subheader("승은 ❤️ 상준 알뜰 가계부")

# 구글 시트 연결
conn = st.connection("gsheets", type=GSheetsConnection)

# 1. 입력 섹션
with st.expander("➕ 새로운 지출 기록하기", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("날짜", datetime.now())
        # 카테고리 수정: 취미 -> 여가
        category = st.selectbox("항목", ["식비-외식", "식비-장보기", "생필품", "여가", "기타"])
    with col2:
        amount = st.number_input("금액 (원)", min_value=0, step=100)
        user = st.radio("누가 썼나요?", ["승은", "상준"], horizontal=True)
    
    # 기타 항목일 때만 메모 입력칸 표시
    memo = ""
    if category == "기타":
        memo = st.text_input("메모 (어디에 썼나요?)")

    if st.button("내역 저장하기", use_container_width=True):
        if amount > 0:
            existing_data = conn.read(
                worksheet="Sheet1",
                usecols=[0,1,2,3,4],
                ttl=0
        )

        if existing_data is None:
            existing_data = pd.DataFrame(
                columns=["날짜","항목","금액","작성자","메모"]
            )

        new_row = pd.DataFrame([{
            "날짜": date.strftime('%Y-%m-%d'),
            "항목": category,
            "금액": amount,
            "작성자": user,
            "메모": memo
        }])
        updated_df = pd.concat([existing_data, new_row], ignore_index=True)
        conn.update(worksheet="Sheet1", data=updated_df)
        st.success(f"✅ 저장 완료! ({category})")
        st.balloons()
    else:
        st.warning("금액을 입력해주세요.")

# 2. 조회 섹션 (탭 기능)
st.divider()
st.markdown("### 📊 지출 리포트")

# 시트 데이터 불러오기
df = conn.read(
    worksheet="Sheet1",
    usecols=[0,1,2,3,4],
    ttl=0
)
df['금액'] = pd.to_numeric(df['금액'], errors='coerce').fillna(0)

# 탭 생성
tab_all, tab_food, tab_life, tab_play, tab_etc = st.tabs(["전체", "식비", "생필품", "여가", "기타"])

with tab_all:
    st.write(f"💰 **총 지출: {df['금액'].sum():,.0f}원**")
    st.dataframe(df.sort_values("날짜", ascending=False), use_container_width=True)

with tab_food:
    food_df = df[df['항목'].str.contains("식비")]
    eat_out = food_df[food_df['항목'] == "식비-외식"]['금액'].sum()
    grocery = food_df[food_df['항목'] == "식비-장보기"]['금액'].sum()
    
    col_a, col_b = st.columns(2)
    col_a.metric("외식비 합계", f"{eat_out:,.0f}원")
    col_b.metric("장보기 합계", f"{grocery:,.0f}원")
    st.write(f"🍱 **식비 총액: {(eat_out + grocery):,.0f}원**")
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
    st.dataframe(etc_df[["날짜", "금액", "작성자", "메모"]], use_container_width=True)
