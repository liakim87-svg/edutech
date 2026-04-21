import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- 1. 페이지 설정 및 디자인 ---
st.set_page_config(page_title="크롬북 통합 관리", layout="wide")

# 사이드바 유지 및 디자인 CSS
st.markdown("""
    <style>
    .stButton > button {
        width: 100%;
        border-radius: 10px;
        height: 70px;
        border: 1px solid #f0f2f6;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
        background-color: white;
    }
    .main-title {
        font-size: 28px;
        font-weight: bold;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

DB_FILE = "chromebook_master_db.csv"
CLASSES = ["1-1", "1-2", "2-1", "2-2", "3-1", "3-2"]
TOTAL_DEVICES = 122

def load_data():
    """데이터 로드 및 무결성 검사"""
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            required_cols = ["기기번호", "학급", "번호", "상태", "특이사항", "최종수정"]
            if all(col in df.columns for col in required_cols):
                return df
        except:
            pass
    
    # 초기 데이터 생성
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
if 'filter_mode' not in st.session_state:
    st.session_state.filter_mode = "전체"

def save_to_file():
    st.session_state.df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')

# --- 2. 사이드바 (기존 기능 유지) ---
with st.sidebar:
    st.title("⚙️ 관리 도구")
    
    st.subheader("개별 상태 변경")
    with st.form("edit_form"):
        target_id = st.selectbox("수정할 기기번호", st.session_state.df['기기번호'].tolist())
        new_status = st.radio("상태 선택", ["이상 없음", "대여 중", "파손/점검", "분실"])
        new_note = st.text_input("특이사항/사유")
        if st.form_submit_button("변경사항 저장"):
            idx = st.session_state.df[st.session_state.df['기기번호'] == target_id].index[0]
            st.session_state.df.at[idx, '상태'] = new_status
            st.session_state.df.at[idx, '특이사항'] = new_note if new_note else "-"
            st.session_state.df.at[idx, '최종수정'] = datetime.now().strftime("%Y-%m-%d %H:%M")
            save_to_file()
            st.success(f"{target_id} 수정 완료!")
            st.rerun()
    
    st.divider()
    st.subheader("학급 일괄 처리")
    batch_cls = st.selectbox("대상 학급", CLASSES)
    if st.button(f"{batch_cls} 전체 정상화"):
        st.session_state.df.loc[st.session_state.df['학급'] == batch_cls, '상태'] = "이상 없음"
        save_to_file()
        st.success(f"{batch_cls} 일괄 정상 처리되었습니다.")
        st.rerun()

    st.divider()
    if st.button("🚨 시스템 전체 초기화"):
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
        st.session_state.clear()
        st.rerun()

# --- 3. 메인 대시보드 ---
st.markdown('<div class="main-title">📱 크롬북 스마트 통합 관리 시스템</div>', unsafe_allow_html=True)

# 현황 요약 카드 (클릭 시 필터링)
df = st.session_state.df
c1, c2, c3, c4 = st.columns(4)

count_total = len(df)
count_normal = len(df[df['상태'] == "이상 없음"])
count_rent = len(df[df['상태'] == "대여 중"])
count_issue = len(df[df['상태'].isin(["파손/점검", "분실"])])

with c1:
    if st.button(f"전체 기기\n{count_total}대"):
        st.session_state.filter_mode = "전체"
with c2:
    if st.button(f"✅ 정상\n{count_normal}대"):
        st.session_state.filter_mode = "이상 없음"
with c3:
    if st.button(f"📤 대여 중\n{count_rent}대"):
        st.session_state.filter_mode = "대여 중"
with c4:
    if st.button(f"⚠️ 점검/분실\n{count_issue}대"):
        st.session_state.filter_mode = "주의 필요"

st.divider()

# --- 4. 필터링된 데이터 출력 ---
st.subheader(f"📍 {st.session_state.filter_mode} 목록")

# 필터링 로직
view_df = df.copy()
if st.session_state.filter_mode == "이상 없음":
    view_df = view_df[view_df['상태'] == "이상 없음"]
elif st.session_state.filter_mode == "대여 중":
    view_df = view_df[view_df['상태'] == "대여 중"]
elif st.session_state.filter_mode == "주의 필요":
    view_df = view_df[view_df['상태'].isin(["파손/점검", "분실"])]

# 검색 기능
search_q = st.text_input("🔍 기기번호 또는 학급 검색 (예: C001, 1-1)", placeholder="검색어를 입력하세요...")
if search_q:
    view_df = view_df[
        view_df['기기번호'].str.contains(search_q, case=False) |
        view_df['학급'].str.contains(search_q)
    ]

# 표 색상 스타일링 함수 (최신 Pandas 버전 호환)
def apply_status_color(val):
    if val == "이상 없음": return 'color: #2E7D32; font-weight: bold;'
    if val == "대여 중": return 'color: #1565C0; font-weight: bold;'
    return 'color: #C62828; font-weight: bold;'

# 출력
st.dataframe(
    view_df.style.map(apply_status_color, subset=['상태']),
    use_container_width=True,
    hide_index=True
)

st.caption(f"데이터 파일 경로: {os.path.abspath(DB_FILE)}")
