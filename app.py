import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- 1. 기본 설정 및 데이터 생성 ---
st.set_page_config(page_title="에듀테크 크롬북 관리", layout="wide", initial_sidebar_state="expanded")

DB_FILE = "chromebook_data_v2.csv"
CLASSES = ["1-1", "1-2", "2-1", "2-2", "3-1", "3-2"]
TOTAL_DEVICES = 122

def initialize_data():
    """초기 122명의 학생 데이터를 생성합니다."""
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    
    data = []
    # 122명을 6개 반으로 나누어 할당
    students_per_class = TOTAL_DEVICES // len(CLASSES)
    remainder = TOTAL_DEVICES % len(CLASSES)
    
    current_count = 0
    for i, class_name in enumerate(CLASSES):
        # 남은 인원을 앞반부터 배분 (122 / 6 = 20...2 이므로 앞 두 반은 21명, 나머지는 20명)
        num_in_this_class = students_per_class + (1 if i < remainder else 0)
        for s in range(1, num_in_this_class + 1):
            current_count += 1
            data.append({
                "기기번호": f"CB-{current_count:03d}",
                "학급": class_name,
                "번호": s,
                "상태": "이상 없음",
                "특이사항": "-",
                "최종수정": datetime.now().strftime("%m/%d %H:%M")
            })
    return pd.DataFrame(data)

# 데이터 로드
if 'df' not in st.session_state:
    st.session_state.df = initialize_data()

df = st.session_state.df

# --- 2. 사이드바: 도우미 입력 인터페이스 ---
st.sidebar.title("🛠️ 도우미 전용")
st.sidebar.markdown(f"**대상 학급:** {', '.join(CLASSES)}")

with st.sidebar.form("update_form"):
    sel_class = st.selectbox("학급 선택", CLASSES)
    
    # 선택한 반 학생들만 필터링
    class_mask = df['학급'] == sel_class
    student_list = df[class_mask]['기기번호'].tolist()
    
    sel_device = st.selectbox("기기 번호 선택", student_list)
    
    # '정상 반납' 대신 '이상 없음' 적용
    new_status = st.radio("반납 상태", ["이상 없음", "대여 중", "파손/점검", "분실"])
    new_note = st.text_input("특이사항 (기재 사항 있을 시)")
    
    submitted = st.form_submit_button("상태 기록하기")
    
    if submitted:
        idx = df[df['기기번호'] == sel_device].index[0]
        df.at[idx, '상태'] = new_status
        df.at[idx, '특이사항'] = new_note if new_note else "-"
        df.at[idx, '최종수정'] = datetime.now().strftime("%m/%d %H:%M")
        
        # 파일 저장 및 세션 갱신
        df.to_csv(DB_FILE, index=False)
        st.session_state.df = df
        st.sidebar.success(f"{sel_device} 업데이트 완료!")
        st.rerun()

# --- 3. 메인 화면: 관리자 대시보드 ---
st.title("💻 크롬북 실시간 관리 시스템")
st.caption(f"전체 관리 대상: {TOTAL_DEVICES}대")

# 통계 카드
c1, c2, c3, c4 = st.columns(4)
c1.metric("전체 기기", f"{len(df)}대")
c2.metric("이상 없음", f"{len(df[df['상태'] == '이상 없음'])}대")
c3.metric("대여 중", f"{len(df[df['상태'] == '대여 중'])}대", delta_color="inverse")
c4.metric("관리 주의", f"{len(df[df['상태'].isin(['파손/점검', '분실'])])}대")

st.markdown("---")

# 학급별 이상 없음 비율
st.subheader("📊 학급별 반납 현황")
status_stats = []
for c in CLASSES:
    class_total = len(df[df['학급'] == c])
    class_ok = len(df[(df['학급'] == c) & (df['상태'] == '이상 없음')])
    rate = (class_ok / class_total) * 100
    status_stats.append({"학급": c, "완료율(%)": round(rate, 1)})

chart_df = pd.DataFrame(status_stats)
st.bar_chart(data=chart_df, x="학급", y="완료율(%)")

# 상세 데이터 테이블
st.subheader("📋 전체 기기 모니터링")
col_search, col_filter = st.columns([2, 1])
with col_search:
    search_q = st.text_input("🔍 학급 또는 기기번호 검색 (예: 2-1)")
with col_filter:
    filter_status = st.multiselect("상태별 보기", ["이상 없음", "대여 중", "파손/점검", "분실"], default=["이상 없음", "대여 중", "파손/점검", "분실"])

# 필터링 로직
view_df = df[df['상태'].isin(filter_status)]
if search_q:
    view_df = view_df[view_df['기기번호'].str.contains(search_q) | view_df['학급'].str.contains(search_q)]

# 테이블 스타일링
def highlight_status(val):
    if val == "분실": return "background-color: #ff4b4b; color: white"
    if val == "파손/점검": return "background-color: #ffa500; color: white"
    if val == "대여 중": return "background-color: #1c83e1; color: white"
    if val == "이상 없음": return "color: #008000"
    return ""

st.dataframe(
    view_df.style.applymap(highlight_status, subset=['상태']),
    use_container_width=True,
    hide_index=True
)

# 하단 도구
st.sidebar.markdown("---")
if st.sidebar.button("⚠️ 데이터 초기화"):
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    st.session_state.clear()
    st.rerun()
