import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- 1. 기본 설정 ---
st.set_page_config(page_title="크롬북 통합 관리", layout="wide")

# CSS를 이용해 상단 카드 디자인 및 버튼 스타일 조정
st.markdown("""
    <style>
    .stButton > button {
        width: 100%;
        border-radius: 10px;
        height: 80px;
        border: 1px solid #f0f2f6;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    .status-text {
        font-size: 14px;
        color: #666;
    }
    .count-text {
        font-size: 24px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

DB_FILE = "chromebook_data_v2.csv"
CLASSES = ["1-1", "1-2", "2-1", "2-2", "3-1", "3-2"]
TOTAL_DEVICES = 122

def load_data():
    """데이터를 로드하거나 초기화합니다."""
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            # 필수 컬럼 확인 (KeyError 방지)
            required_cols = ["기기번호", "학급", "번호", "상태", "특이사항", "최종수정"]
            if not all(col in df.columns for col in required_cols):
                raise ValueError("Column mismatch")
            return df
        except:
            pass
    
    # 데이터가 없거나 에러 발생 시 초기 생성
    data = []
    current_id = 1
    per_class = TOTAL_DEVICES // len(CLASSES)
    remainder = TOTAL_DEVICES % len(CLASSES)
    
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
    new_df = pd.DataFrame(data)
    new_df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
    return new_df

# 세션 상태 초기화
if 'df' not in st.session_state:
    st.session_state.df = load_data()
if 'filter_status' not in st.session_state:
    st.session_state.filter_status = "전체"

def update_status(device_id, status, note):
    """기기 상태를 업데이트하고 파일에 저장합니다."""
    idx = st.session_state.df[st.session_state.df['기기번호'] == device_id].index[0]
    st.session_state.df.at[idx, '상태'] = status
    st.session_state.df.at[idx, '특이사항'] = note if note else "-"
    st.session_state.df.at[idx, '최종수정'] = datetime.now().strftime("%Y-%m-%d %H:%M")
    st.session_state.df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')

# --- 2. 메인 화면 구성 ---
st.title("📱 크롬북 스마트 통합 관리 시스템")

# 현황 요약 카드 (클릭 가능하도록 버튼으로 구성)
df = st.session_state.df
col1, col2, col3, col4 = st.columns(4)

counts = {
    "전체": len(df),
    "이상 없음": len(df[df['상태'] == "이상 없음"]),
    "대여 중": len(df[df['상태'] == "대여 중"]),
    "주의 필요": len(df[df['상태'].isin(["파손/점검", "분실"])])
}

with col1:
    if st.button(f"전체 기기\n{counts['전체']}대"):
        st.session_state.filter_status = "전체"
with col2:
    if st.button(f"정상\n{counts['이상 없음']}대"):
        st.session_state.filter_status = "이상 없음"
with col3:
    if st.button(f"대여 중\n{counts['대여 중']}대"):
        st.session_state.filter_status = "대여 중"
with col4:
    # 파손/분실은 빨간색 느낌을 주기 위해 주의 필요로 표시
    if st.button(f"🚨 점검/분실\n{counts['주의 필요']}대"):
        st.session_state.filter_status = "주의 필요"

st.divider()

# --- 3. 필터링된 결과 표시 ---
st.subheader(f"📍 {st.session_state.filter_status} 목록")

display_df = df.copy()
if st.session_state.filter_status == "이상 없음":
    display_df = display_df[display_df['상태'] == "이상 없음"]
elif st.session_state.filter_status == "대여 중":
    display_df = display_df[display_df['상태'] == "대여 중"]
elif st.session_state.filter_status == "주의 필요":
    display_df = display_df[display_df['상태'].isin(["파손/점검", "분실"])]

# 검색 바
search = st.text_input("🔍 기기번호 또는 학급 검색 (예: C005, 2-1)", placeholder="검색어를 입력하세요...")
if search:
    display_df = display_df[
        display_df['기기번호'].str.contains(search, case=False) |
        display_df['학급'].str.contains(search)
    ]

# 상태별 색상 입히기
def color_status(val):
    color = '#2E7D32' if val == "이상 없음" else '#1565C0' if val == "대여 중" else '#C62828'
    return f'color: {color}; font-weight: bold'

st.dataframe(
    display_df.style.applymap(color_status, subset=['상태']),
    use_container_width=True,
    hide_index=True
)

st.divider()

# --- 4. 관리 도구 (사이드바) ---
with st.sidebar:
    st.header("⚙️ 관리 설정")
    
    # 기기 상태 수정 폼
    st.subheader("개별 기기 상태 변경")
    with st.form("edit_form"):
        device_to_edit = st.selectbox("기기 번호", df['기기번호'].tolist())
        new_status = st.radio("변경할 상태", ["이상 없음", "대여 중", "파손/점검", "분실"])
        new_note = st.text_input("특이사항 입력")
        if st.form_submit_button("상태 저장"):
            update_status(device_to_edit, new_status, new_note)
            st.success(f"{device_to_edit} 상태가 변경되었습니다.")
            st.rerun()

    st.divider()
    
    # 학급별 일괄 처리
    st.subheader("학급 일괄 정상화")
    batch_cls = st.selectbox("학급 선택", CLASSES)
    if st.button(f"{batch_cls} 전원 '이상 없음'"):
        st.session_state.df.loc[st.session_state.df['학급'] == batch_cls, '상태'] = "이상 없음"
        st.session_state.df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
        st.success(f"{batch_cls} 초기화 완료")
        st.rerun()

    st.divider()
    if st.button("🔄 전체 데이터 초기화"):
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
        st.session_state.clear()
        st.rerun()

# --- 5. 자동 저장 안내 ---
st.caption(f"마지막 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 모든 변경사항은 즉시 저장됩니다.")
