import streamlit as st
import pandas as pd
import datetime

# 페이지 설정
st.set_page_config(page_title="2026 크롬북 관리 대장", layout="wide")

# 가상 데이터 생성 (실제 사용 시 구글 시트 API 또는 CSV 연결 가능)
# 현재 공유해주신 시트 구조를 바탕으로 샘플 데이터를 구성합니다.
def get_sample_data():
    data = [
        {"이름": "김동율", "학번": "1101", "보관상태": "충전함 보관", "이상유무": "이상 없음", "비고": "", "도우미": "박하민"},
        {"이름": "김민석", "학번": "1102", "보관상태": "대여 중", "이상유무": "이상 없음", "비고": "도서관 사용", "도우미": "손연아"},
        {"이름": "김어진", "학번": "1103", "보관상태": "충전함 보관", "이상유무": "이상 있음", "비고": "액정 파손 의심", "도우미": "박하민"},
        {"이름": "김소현", "학번": "2107", "보관상태": "미반납", "이상유무": "이상 없음", "비고": "가방에 넣고 귀가", "도우미": "진정한"},
    ]
    return pd.DataFrame(data)

# 데이터 로드
if 'df' not in st.session_state:
    st.session_state.df = get_sample_data()

df = st.session_state.df

# --- 헤더 및 알림 섹션 ---
st.title("💻 2026 학생 크롬북 스마트 관리 대장")

# 알림 로직: 이상이 있거나 미반납인 경우
critical_issues = df[(df['이상유무'] == "이상 있음") | (df['보관상태'] == "미반납")]

if not critical_issues.empty:
    st.error(f"🚨 현재 {len(critical_issues)}건의 관리 주의 항목이 있습니다! (미반납 또는 기기 이상)")
    with st.expander("⚠️ 즉시 확인 필요 리스트"):
        st.table(critical_issues[['학번', '이름', '보관상태', '이상유무', '비고']])
else:
    st.success("✅ 모든 크롬북이 정상적으로 반납 및 보관 중입니다.")

# --- 상단 대시보드 (현황판) ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("전체 기기", f"{len(df)}대")
with col2:
    storage_count = len(df[df['보관상태'] == "충전함 보관"])
    st.metric("보관 완료", f"{storage_count}대", delta=f"{storage_count - len(df)}")
with col3:
    issue_count = len(df[df['이상유무'] == "이상 있음"])
    st.metric("수리/이상", f"{issue_count}대", delta_color="inverse")
with col4:
    loan_count = len(df[df['보관상태'] == "대여 중"])
    st.metric("현재 대여", f"{loan_count}대")

st.divider()

# --- 메인 관리 영역 ---
col_sidebar, col_main = st.columns([1, 3])

with col_sidebar:
    st.subheader("🔍 필터링")
    grade_class = st.multiselect("학년/반 선택", options=sorted(df['학번'].str[:2].unique()), default=sorted(df['학번'].str[:2].unique()))
    status_filter = st.multiselect("보관 상태", options=df['보관상태'].unique(), default=df['보관상태'].unique())
    
    st.divider()
    st.subheader("📝 퀵 업데이트")
    target_student = st.selectbox("학생 선택", df['이름'].tolist())
    new_status = st.selectbox("상태 변경", ["충전함 보관", "대여 중", "미반납"])
    if st.button("상태 반영하기"):
        st.session_state.df.loc[st.session_state.df['이름'] == target_student, '보관상태'] = new_status
        st.success(f"{target_student} 학생 상태 변경 완료")
        st.rerun()

with col_main:
    st.subheader("📋 상세 관리 목록")
    
    # 필터 적용
    display_df = df[df['학번'].str[:2].isin(grade_class) & df['보관상태'].isin(status_filter)]
    
    # 데이터프레임 스타일링 (이상 유무에 따라 색상 지정)
    def highlight_issues(val):
        color = 'red' if val == "이상 있음" or val == "미반납" else 'black'
        return f'color: {color}'

    st.dataframe(
        display_df.style.applymap(highlight_issues, subset=['이상유무', '보관상태']),
        use_container_width=True,
        hide_index=True
    )

    # 하단 추가 기능
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📊 오늘자 관리 리포트 생성"):
            st.info("리포트가 생성되었습니다. (PDF/Excel 다운로드 가능)")
    with c2:
        st.write("마지막 업데이트: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
