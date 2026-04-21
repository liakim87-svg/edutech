import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- 1. 기본 설정 및 데이터 초기화 ---
st.set_page_config(page_title="크롬북 관리 시스템", layout="wide")

DB_FILE = "chromebook_data.csv"
CLASSES = ["1-1", "1-2", "2-1", "2-2", "3-1", "3-2"]
TOTAL_DEVICES = 122

def initialize_data():
    """데이터 파일이 없으면 새로 생성합니다."""
    if os.path.exists(DB_FILE):
        try:
            return pd.read_csv(DB_FILE)
        except:
            pass # 파일이 깨졌을 경우 아래에서 새로 생성
    
    data = []
    per_class = TOTAL_DEVICES // len(CLASSES)
    remainder = TOTAL_DEVICES % len(CLASSES)
    
    current_id = 1
    for i, cls in enumerate(CLASSES):
        count_for_this_class = per_class + (1 if i < remainder else 0)
        for student_num in range(1, count_for_this_class + 1):
            if current_id <= TOTAL_DEVICES:
                data.append({
                    "기기번호": f"C{current_id:03d}",
                    "학급": cls,
                    "번호": student_num,
                    "상태": "이상 없음",
                    "특이사항": "-",
                    "최종수정": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                current_id += 1
    df = pd.DataFrame(data)
    df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
    return df

# 세션 상태에 데이터 로드
if 'df' not in st.session_state:
    st.session_state.df = initialize_data()

# --- 2. 사이드바: 관리 도구 ---
st.sidebar.title("🛠️ 관리 도구")

# 학급별 일괄 처리
st.sidebar.subheader("학급 전체 처리")
batch_cls = st.sidebar.selectbox("대상 학급 선택", CLASSES)
if st.sidebar.button(f"{batch_cls} 전체 '이상 없음' 처리"):
    st.session_state.df.loc[st.session_state.df['학급'] == batch_cls, '상태'] = "이상 없음"
    st.session_state.df.loc[st.session_state.df['학급'] == batch_cls, '최종수정'] = datetime.now().strftime("%Y-%m-%d %H:%M")
    st.session_state.df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
    st.sidebar.success(f"{batch_cls} 학급 설정 완료!")
    st.rerun()

st.sidebar.divider()

# 개별 기기 수정 (Form 사용으로 에러 방지)
st.sidebar.subheader("개별 상태 수정")
with st.sidebar.form("update_form", clear_on_submit=True):
    target_id = st.selectbox("기기 번호", st.session_state.df['기기번호'].tolist())
    new_status = st.radio("상태 선택", ["이상 없음", "대여 중", "파손/점검", "분실"])
    new_note = st.text_input("특이사항 (선택사항)")
    
    submit_button = st.form_submit_button("저장하기")
    
    if submit_button:
        idx = st.session_state.df[st.session_state.df['기기번호'] == target_id].index[0]
        st.session_state.df.at[idx, '상태'] = new_status
        st.session_state.df.at[idx, '특이사항'] = new_note if new_note else "-"
        st.session_state.df.at[idx, '최종수정'] = datetime.now().strftime("%Y-%m-%d %H:%M")
        st.session_state.df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
        st.sidebar.info(f"{target_id} 업데이트 완료")
        st.rerun()

# --- 3. 메인 대시보드 ---
st.title("📱 크롬북 스마트 통합 관리")

# 요약 통계
df = st.session_state.df
col1, col2, col3, col4 = st.columns(4)

total = len(df)
normal = len(df[df['상태'] == "이상 없음"])
rented = len(df[df['상태'] == "대여 중"])
broken = len(df[df['상태'].isin(["파손/점검", "분실"])])

col1.metric("전체 수량", f"{total}대")
col2.metric("정상 사용", f"{normal}대")
col3.metric("대여 중", f"{rented}대")
col4.metric("🚨 점검/분실", f"{broken}대")

# 긴급 확인 리스트
if broken > 0:
    st.error("### 🚨 점검 및 분실 기기 명단")
    issue_df = df[df['상태'].isin(["파손/점검", "분실"])]
    st.table(issue_df[['기기번호', '학급', '상태', '특이사항']])

st.divider()

# --- 4. 검색 및 명부 출력 ---
st.subheader("📋 전체 기기 현황")
search = st.text_input("🔍 기기번호 또는 학급으로 검색 (예: C001, 1-1)")

view_df = df.copy()
if search:
    view_df = view_df[
        view_df['기기번호'].str.contains(search, case=False) | 
        view_df['학급'].str.contains(search)
    ]

# 상태별 색상 적용 (최신 Pandas 문법 호환)
def color_status(val):
    if val == "이상 없음": return 'color: #2E7D32'
    if val == "대여 중": return 'color: #1565C0'
    if val == "파손/점검": return 'color: #E65100'
    if val == "분실": return 'color: #C62828'
    return ''

st.dataframe(
    view_df.style.applymap(color_status, subset=['상태']),
    use_container_width=True,
    hide_index=True
)

# 데이터 리셋 버튼
if st.sidebar.button("⚠️ 데이터 전체 초기화"):
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    st.session_state.clear()
    st.rerun()
