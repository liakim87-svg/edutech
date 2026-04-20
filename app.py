import streamlit as st
import pandas as pd
import datetime
import os

# 파일 경로 설정
DATA_FILE = "usage_logs.csv"

def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        df['날짜'] = pd.to_datetime(df['날짜']).dt.date
        return df
    else:
        return pd.DataFrame(columns=["날짜", "기자재명", "사용자", "상태", "비고"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# 페이지 설정
st.set_page_config(page_title="에듀테크 일자별 관리", layout="wide")

# 세션 상태 초기화
if "data" not in st.session_state:
    st.session_state.data = load_data()

st.title("📅 에듀테크 일자별 관리 시스템")

# --- 사이드바: 필터 및 설정 ---
with st.sidebar:
    st.header("🔍 조회 필터")
    
    # 날짜 범위 선택
    today = datetime.date.today()
    start_date = st.date_input("시작일", today - datetime.timedelta(days=7))
    end_date = st.date_input("종료일", today)
    
    st.divider()
    
    st.header("⚙️ 관리자 설정")
    reset_password = st.text_input("초기화 비밀번호", type="password")
    if st.button("데이터 전체 리셋"):
        if reset_password == "admin1234":
            st.session_state.data = pd.DataFrame(columns=["날짜", "기자재명", "사용자", "상태", "비고"])
            save_data(st.session_state.data)
            st.success("초기화되었습니다.")
            st.rerun()
        else:
            st.error("비밀번호 불일치")

# --- 데이터 필터링 ---
filtered_df = st.session_state.data[
    (st.session_state.data['날짜'] >= start_date) & 
    (st.session_state.data['날짜'] <= end_date)
]

# --- 상단 대시보드 ---
col_m1, col_m2, col_m3 = st.columns(3)
with col_m1:
    st.metric("선택 기간 기록", f"{len(filtered_df)} 건")
with col_m2:
    today_count = len(st.session_state.data[st.session_state.data['날짜'] == today])
    st.metric("오늘 신규 기록", f"{today_count} 건")
with col_m3:
    critical_count = len(filtered_df[filtered_df['상태'] == "수리 필요"])
    st.metric("⚠️ 수리 필요(필터내)", f"{critical_count} 건", delta_color="inverse")

# --- 입력 폼 (접이식) ---
with st.expander("➕ 새 기록 추가하기", expanded=False):
    with st.form("usage_form"):
        c1, c2 = st.columns(2)
        with c1:
            item_name = st.selectbox("기자재명", ["태블릿", "크롬북", "노트북", "VR기기", "충전함", "기타"])
            user_name = st.text_input("사용자")
        with c2:
            status = st.radio("상태", ["정상", "이상 발생", "수리 필요"], horizontal=True)
            log_date = st.date_input("기록 날짜", today)
        
        note = st.text_area("비고 (고장 증상 등)")
        if st.form_submit_button("저장하기"):
            if user_name:
                new_entry = pd.DataFrame([{
                    "날짜": log_date,
                    "기자재명": item_name,
                    "사용자": user_name,
                    "상태": status,
                    "비고": note
                }])
                st.session_state.data = pd.concat([st.session_state.data, new_entry], ignore_index=True)
                save_data(st.session_state.data)
                st.success("기록 완료!")
                st.rerun()

# --- 데이터 시각화 및 리스트 ---
st.divider()

tab1, tab2 = st.tabs(["📋 상세 기록 리스트", "📈 일자별 통계"])

with tab1:
    col_h1, col_h2 = st.columns([4, 1])
    with col_h1:
        st.subheader(f"📅 {start_date} ~ {end_date} 기록")
    with col_h2:
        # CSV 다운로드 버튼
        csv = filtered_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 필터 데이터 결과 다운로드", csv, "filtered_logs.csv", "text/csv")

    if not filtered_df.empty:
        # 최신순 정렬하여 표시
        st.dataframe(
            filtered_df.sort_values(by="날짜", ascending=False),
            use_container_width=True,
            column_config={
                "상태": st.column_config.SelectboxColumn(
                    "상태", options=["정상", "이상 발생", "수리 필요"]
                )
            }
        )
    else:
        st.info("해당 기간에 등록된 기록이 없습니다.")

with tab2:
    if not filtered_df.empty:
        st.subheader("일자별 사용 빈도")
        chart_data = filtered_df.groupby('날짜').size()
        st.bar_chart(chart_data)
        
        st.subheader("기자재별 상태 분포")
        item_status = pd.crosstab(filtered_df['기자재명'], filtered_df['상태'])
        st.bar_chart(item_status)
    else:
        st.write("통계를 표시할 데이터가 없습니다.")
