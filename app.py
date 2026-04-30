import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- 1. 페이지 설정 및 데이터 로드 로직 (기존과 동일) ---
st.set_page_config(page_title="상북중 크롬북 통합 관리", layout="wide")
DB_FILE = "chromebook_master_db_v11.csv"

# [데이터] 학생 명단 (생략 - 기존 리스트 유지)
# ... STUDENT_LIST 코드 ...

def load_data():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE, dtype={'학번': str})
            df['특이사항'] = df['특이사항'].fillna("")
            return df
        except: pass
    # 초기 데이터 생성 생략 (v10과 동일)
    return pd.DataFrame() # 예시용

if 'df' not in st.session_state:
    st.session_state.df = load_data()

# --- 2. [핵심] 대여 선택 시 메모칸 제어 함수 ---
def handle_status_change():
    # 사용자가 라디오 버튼으로 선택한 상태가 '대여'라면
    if st.session_state.new_status_key == "대여":
        # 현재 특이사항이 비어있을 때만 가이드 문구 삽입 (기존 기록 보호)
        if not st.session_state.temp_note_key:
            st.session_state.temp_note_key = "" # placeholder가 보이게 비워둠

# --- 3. 사이드바 구성 ---
with st.sidebar:
    st.header("⚙️ 접속 모드")
    is_admin = st.checkbox("교사용 관리자 모드")
    
    # ... (중략: 관리자 알림/초기화 버튼들) ...

    st.divider()
    st.subheader("🛠️ 개별 상태 보고")
    active_cls = st.selectbox("학급 선택", sorted(list(set(st.session_state.df['학급']))))
    
    cls_df = st.session_state.df[st.session_state.df['학급'] == active_cls]
    student_options = cls_df.apply(lambda x: f"{x['학번']} - {x['이름']}", axis=1).tolist()
    
    selected_student = st.selectbox("학생 선택", student_options)
    target_sid = selected_student.split(" - ")[0]
    row = st.session_state.df[st.session_state.df['학번'] == target_sid].iloc[0]

    # 상태 선택 (on_change를 넣어 즉각 반응하게 만듦)
    STATUS_LIST = ["이상 없음", "대여", "파손/점검", "분실"]
    
    # 폼 외부에서 상태를 먼저 결정 (즉시 반응을 위해)
    current_status = st.radio(
        "기기 상태", 
        STATUS_LIST, 
        index=STATUS_LIST.index(row['상태']) if row['상태'] in STATUS_LIST else 0,
        key="new_status_key",
        on_change=handle_status_change
    )

    # 대여일 때만 placeholder가 나타나도록 설정
    # placeholder는 클릭 후 타이핑을 시작하면 자동으로 지워집니다.
    ph = "반납예정일자를 쓰시오" if current_status == "대여" else ""

    with st.form("edit_form"):
        # 실제 입력창 (key를 부여하여 관리)
        new_note = st.text_input("특이사항/메모", value=row['특이사항'], placeholder=ph, key="temp_note_key")
        
        if st.form_submit_button("저장 및 보고"):
            idx = st.session_state.df[st.session_state.df['학번'] == target_sid].index[0]
            st.session_state.df.at[idx, '상태'] = current_status
            st.session_state.df.at[idx, '특이사항'] = new_note
            st.session_state.df.at[idx, '최종수정'] = datetime.now().strftime("%Y-%m-%d %H:%M")
            
            # 저장 후 파일 업데이트 및 새로고침
            st.session_state.df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
            st.success(f"{row['이름']} 보고 완료!")
            st.rerun()

# --- 4. 메인 화면 (대시보드/테이블) ---
# ... 기존 v10 코드와 동일 ...
