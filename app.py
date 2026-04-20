import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 1. 화면 구성 설정
st.set_page_config(page_title="에듀테크 도우미", layout="wide")

# 데이터 저장용 파일 이름
DB_FILE = "logs.csv"

# 데이터 불러오기 함수
def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["날짜", "학반", "유형", "기기번호", "작성자", "내용"])

# 데이터 저장 함수
def save_data(df):
    df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')

# --- UI 시작 ---
st.title("📱 에듀테크 도우미 통합 관리")
st.info("이곳에서 학급 기기를 점검하고 고장 신고를 할 수 있습니다.")

# 메뉴 선택
menu = st.sidebar.selectbox("메뉴", ["오늘의 점검", "고장 리포트", "전체 기록 보기"])

df = load_data()

if menu == "오늘의 점검":
    st.subheader("✅ 정기 점검 완료 체크")
    col1, col2 = st.columns(2)
    
    with col1:
        target_class = st.selectbox("학반 선택", ["1-1", "1-2", "2-1", "2-2", "3-1", "3-2"])
        helper_name = st.text_input("도우미 성함")
    
    if st.button("점검 완료 등록"):
        if helper_name:
            new_data = {
                "날짜": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "학반": target_class,
                "유형": "정기점검",
                "기기번호": "-",
                "작성자": helper_name,
                "내용": "이상 없음"
            }
            df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
            save_data(df)
            st.success(f"{target_class} 점검 완료!")
        else:
            st.warning("성함을 입력해주세요.")

elif menu == "고장 리포트":
    st.subheader("🚨 기기 고장/불량 신고")
    with st.form("issue_form"):
        f_class = st.selectbox("학반", ["1-1", "1-2", "2-1", "2-2", "3-1", "3-2"])
        f_num = st.number_input("기기 번호", min_value=1, max_value=40)
        f_user = st.text_input("신고자 성함")
        f_desc = st.text_area("상세 증상")
        
        if st.form_submit_button("리포트 제출"):
            new_data = {
                "날짜": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "학반": f_class,
                "유형": "고장신고",
                "기기번호": f_num,
                "작성자": f_user,
                "내용": f_desc
            }
            df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
            save_data(df)
            st.success("고장 리포트가 접수되었습니다.")

elif menu == "전체 기록 보기":
    st.subheader("📊 누적 관리 기록")
    st.dataframe(df.sort_values("날짜", ascending=False), use_container_width=True)
    
    # 엑셀 다운로드 기능
    csv = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
    st.download_button("데이터 다운로드 (CSV)", csv, "edutech_logs.csv", "text/csv")
