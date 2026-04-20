import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

# 1. 페이지 설정 및 초기 데이터 구성
st.set_page_config(page_title="크롬북 스마트 관리 대장", layout="wide")

# 앱 실행 시 세션 상태에 데이터 저장 (실제 서비스 시에는 DB나 Google Sheets 연동)
if 'chromebook_data' not in st.session_state:
    # 초기 샘플 데이터 생성
    initial_data = []
    # 1반부터 5반까지 샘플 학생 생성
    for class_num in range(1, 6):
        for student_num in range(1, 21):
            student_id = f"1{class_num:01d}{student_num:02d}"
            initial_data.append({
                "학번": student_id,
                "이름": f"학생{student_id}",
                "반": f"{class_num}반",
                "상태": "보관 중",
                "이상유무": "정상",
                "상세내용": "",
                "업데이트시간": datetime.datetime.now().strftime("%H:%M")
            })
    st.session_state.chromebook_data = pd.DataFrame(initial_data)

df = st.session_state.chromebook_data

# --- 사이드바: 도우미 입력 메뉴 ---
with st.sidebar:
    st.header("🛠️ 도우미 입력 메뉴")
    st.info("자기 반을 선택하고 점검 내용을 입력하세요.")
    
    with st.form("input_form"):
        target_class = st.selectbox("우리 반 선택", options=sorted(df['반'].unique()))
        
        # 선택한 반의 학생들만 필터링
        class_students = df[df['반'] == target_class]
        target_student_id = st.selectbox("학생 선택 (학번)", options=class_students['학번'].tolist())
        
        new_status = st.radio("기기 상태", ["보관 중", "대여 중", "미반납"])
        new_issue = st.radio("이상 유무", ["정상", "이상 있음 (고장)"])
        issue_detail = st.text_input("고장 사유/비고", placeholder="예: 액정 파손, 충전 안됨")
        
        submit_button = st.form_submit_button("상태 업데이트")
        
        if submit_button:
            # 데이터 업데이트 로직
            idx = df[df['학번'] == target_student_id].index[0]
            df.at[idx, '상태'] = new_status
            df.at[idx, '이상유무'] = new_issue
            df.at[idx, '상세내용'] = issue_detail
            df.at[idx, '업데이트시간'] = datetime.datetime.now().strftime("%H:%M")
            st.session_state.chromebook_data = df
            st.success(f"{target_student_id} 업데이트 완료!")

    st.divider()
    st.caption("2026 Smart Chromebook Management System v1.0")

# --- 메인 화면: 시각화 대시보드 ---
st.title("📊 크롬북 통합 관리 현황판")

# 2. 알림 섹션 (이상이 있거나 미반납인 경우 상단 노출)
critical_df = df[(df['이상유무'] == "이상 있음 (고장)") | (df['상태'] == "미반납")]
if not critical_df.empty:
    st.warning(f"🚨 주의 필요 항목: {len(critical_df)}건 (고장 또는 미반납)")
    with st.expander("세부 내역 보기"):
        st.table(critical_df[['학번', '이름', '상태', '이상유무', '상세내용']])

# 3. 최상단 핵심 지표 (Metrics)
m_col1, m_col2, m_col3, m_col4 = st.columns(4)
with m_col1:
    st.metric("전체 기기", len(df))
with m_col2:
    st.metric("보관 중", len(df[df['상태'] == "보관 중"]))
with m_col3:
    st.metric("대여 중", len(df[df['상태'] == "대여 중"]), delta=len(df[df['상태'] == "미반납"]), delta_color="inverse")
with m_col4:
    st.metric("수리 필요", len(df[df['이상유무'] == "이상 있음 (고장)"]), delta_color="off")

st.divider()

# 4. 차트 시각화 영역
chart_col1, chart_col2 = st.columns([1, 1])

with chart_col1:
    st.subheader("📍 기기 보관 상태 비율")
    fig_pie = px.pie(df, names='상태', color='상태',
                 color_discrete_map={'보관 중':'#2ecc71', '대여 중':'#3498db', '미반납':'#e74c3c'},
                 hole=0.4)
    st.plotly_chart(fig_pie, use_container_width=True)

with chart_col2:
    st.subheader("🏫 반별 점검 진행률 (보관 비율)")
    # 반별로 보관 중인 비율 계산
    class_stats = df.groupby('반')['상태'].apply(lambda x: (x == '보관 중').mean() * 100).reset_index()
    class_stats.columns = ['반', '보관율']
    fig_bar = px.bar(class_stats, x='반', y='보관율', 
                     range_y=[0, 100],
                     labels={'보관율': '보관 완료 (%)'},
                     color='보관율', color_continuous_scale='RdYlGn')
    st.plotly_chart(fig_bar, use_container_width=True)

# 5. 하단 상세 테이블 (필터 기능 포함)
st.divider()
st.subheader("📑 실시간 전체 명단")
search_query = st.text_input("🔍 이름 또는 학번으로 검색")

if search_query:
    filtered_df = df[df['이름'].str.contains(search_query) | df['학번'].str.contains(search_query)]
else:
    filtered_df = df

# 가독성을 위해 스타일링 적용
def style_status(val):
    if val == "이상 있음 (고장)": return "background-color: #ffcccc"
    if val == "미반납": return "background-color: #ffe5cc"
    if val == "대여 중": return "color: #3498db"
    return ""

st.dataframe(
    filtered_df.style.applymap(style_status, subset=['상태', '이상유무']),
    use_container_width=True,
    hide_index=True
)
