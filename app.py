import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- 1. 페이지 설정 및 알림 JS ---
st.set_page_config(page_title="상북중 크롬북 통합 관리", layout="wide")

# (알림 JS 생략 - 기존과 동일)
st.markdown("""<script>...</script>""", unsafe_allow_html=True)

# 버전 업데이트 및 파일명
DB_FILE = "chromebook_master_db_v14.csv"

# [데이터 로드 함수]
def load_data():
    if os.path.exists(DB_FILE):
        try:
            return pd.read_csv(DB_FILE, dtype={'학번': str}).fillna("")
        except: pass
    # 초기 데이터 생성 로직 (생략 - 기존 리스트 활용)
    return pd.DataFrame() 

if 'df' not in st.session_state:
    st.session_state.df = load_data()

# [필터 상태 관리]
if 'filter_status' not in st.session_state:
    st.session_state.filter_status = "전체"

# --- 2. 사이드바 구성 ---
with st.sidebar:
    st.header("⚙️ 접속 모드")
    is_admin = st.checkbox("교사용 관리자 모드")
    
    # ... (중략: 관리자 기능) ...

    st.divider()
    st.subheader("🛠️ 개별 상태 보고")
    active_cls = st.selectbox("학급 선택", sorted(list(set(st.session_state.df['학급']))))
    cls_df = st.session_state.df[st.session_state.df['학급'] == active_cls]
    student_options = cls_df.apply(lambda x: f"{x['학번']} - {x['이름']}", axis=1).tolist()
    
    selected_student = st.selectbox("학생 선택", student_options)
    target_sid = selected_student.split(" - ")[0]
    row = st.session_state.df[st.session_state.df['학번'] == target_sid].iloc[0]

    # 상태 라디오 (폼 외부로 배치하여 즉시 placeholder 반영)
    STATUS_LIST = ["이상 없음", "대여", "파손/점검", "분실"]
    new_status = st.radio("기기 상태", STATUS_LIST, 
                         index=STATUS_LIST.index(row['상태']) if row['상태'] in STATUS_LIST else 0)

    with st.form("edit_form"):
        # 대여 클릭 시 가이드 문구 즉시 활성화
        ph_msg = "반납 예정일자를 쓰시오" if new_status == "대여" else ""
        new_note = st.text_input("특이사항/메모", value=row['특이사항'], placeholder=ph_msg)
        
        if st.form_submit_button("저장하기"):
            idx = st.session_state.df[st.session_state.df['학번'] == target_sid].index[0]
            st.session_state.df.at[idx, '상태'] = new_status
            st.session_state.df.at[idx, '특이사항'] = new_note
            st.session_state.df.at[idx, '최종수정'] = datetime.now().strftime("%Y-%m-%d %H:%M")
            st.session_state.df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
            st.rerun()

# --- 3. 메인 화면 ---
st.title("🛡️ 상북중 크롬북 통합 현황판")

# [필터 버튼 인터페이스]
df = st.session_state.df
st.subheader(f"📊 실시간 기기 현황 (필터: {st.session_state.filter_status})")

# 버튼형 대시보드 구현
cols = st.columns(5)
if cols[0].button(f"전체\n{len(df)}대"): st.session_state.filter_status = "전체"
if cols[1].button(f"🟢 정상\n{len(df[df['상태']=='이상 없음'])}대"): st.session_state.filter_status = "이상 없음"
if cols[2].button(f"🏠 대여\n{len(df[df['상태']=='대여'])}대"): st.session_state.filter_status = "대여"
if cols[3].button(f"🛠️ 파손\n{len(df[df['상태']=='파손/점검'])}대"): st.session_state.filter_status = "파손/점검"
if cols[4].button(f"🔍 분실\n{len(df[df['상태']=='분실'])}대"): st.session_state.filter_status = "분실"

# 필터링 적용
display_df = df if st.session_state.filter_status == "전체" else df[df['상태'] == st.session_state.filter_status]

st.divider()

# 표 스타일 및 출력
def style_status(row):
    color = ''
    if row['상태'] == "이상 없음": color = 'background-color: #f0fff4;'
    elif row['상태'] == "대여": color = 'background-color: #ebf8ff;'
    elif row['상태'] == "파손/점검": color = 'background-color: #fff5f5; color: #742a2a; font-weight: bold;'
    elif row['상태'] == "분실": color = 'background-color: #2d3748; color: white; font-weight: bold;'
    return [color] * len(row)

st.dataframe(display_df.style.apply(style_status, axis=1), use_container_width=True, hide_index=True)
