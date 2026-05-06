import streamlit as st
import pandas as pd
from datetime import datetime

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="크롬북 관리 시스템", layout="wide")
st.title("💻 상북중학교 크롬북 관리 대시보드")

# 2. 데이터 불러오기 (실제로는 구글 시트 연결 함수가 들어갈 자리)
# 여기서는 예시를 위해 세션 상태에 데이터를 생성합니다.
if 'df' not in st.session_state:
    # 실제 운영 시 이 부분에 구글 시트 로드 코드가 들어갑니다.
    data = {
        '학급': ['1-1', '1-2', '2-1', '2-2'],
        '기기번호': ['CB-01', 'CB-02', 'CB-03', 'CB-04'],
        '상태': ['정상', '수리필요', '정상', '분실'],
        '점검일': ['2026-05-01', '2026-05-02', '2026-05-03', '2026-05-04'],
        '비고': ['', '액정 파손', '', '체육관 뒤 확인 필요']
    }
    st.session_state.df = pd.DataFrame(data)

# 사이드바: 관리자/학생 설정
st.sidebar.header("⚙️ 관리자/학생 설정")
admin_mode = st.sidebar.checkbox("교사용 관리자 모드")

# ---------------------------------------------------------
# [학생용 화면] - 상태 입력 창
# ---------------------------------------------------------
if not admin_mode:
    st.subheader("📝 오늘의 크롬북 상태 기록")
    
    with st.form("check_form"):
        # 오류 방지를 위한 컬럼 존재 확인
        if '학급' in st.session_state.df.columns:
            all_classes = st.session_state.df['학급'].unique()
            active_cls = st.selectbox("우리 반 선택", all_classes)
        else:
            st.error("데이터에 '학급' 정보가 없습니다. 관리자에게 문의하세요.")
            st.stop()
            
        status = st.radio("기기 상태", ["정상", "수리필요", "분실"])
        note = st.text_input("상세 내용 (수리 필요 시 기재)")
        submit = st.form_submit_button("기록하기 ✨")
        
        if submit:
            # 데이터 업데이트 로직 (87번 줄 부근 오류 해결 지점)
            st.session_state.df.loc[st.session_state.df['학급'] == active_cls, '상태'] = status
            st.session_state.df.loc[st.session_state.df['학급'] == active_cls, '비고'] = note
            st.session_state.df.loc[st.session_state.df['학급'] == active_cls, '점검일'] = datetime.now().strftime("%Y-%m-%d")
            st.success(f"{active_cls} 반 기록이 완료되었습니다!")

# ---------------------------------------------------------
# [관리자 화면] - 대시보드 및 데이터 활용
# ---------------------------------------------------------
else:
    st.subheader("📊 전체 기기 관리 현황")
    
    # 첫 번째 핵심: 한눈에 들어오는 대시보드
    col1, col2, col3 = st.columns(3)
    total_count = len(st.session_state.df)
    repair_count = len(st.session_state.df[st.session_state.df['상태'] == '수리필요'])
    lost_count = len(st.session_state.df[st.session_state.df['상태'] == '분실'])
    
    col1.metric("전체 기기", f"{total_count}대")
    col2.metric("수리 필요 🛠️", f"{repair_count}대", delta=repair_count, delta_color="inverse")
    col3.metric("분실 위험 ⚠️", f"{lost_count}대", delta=lost_count, delta_color="inverse")
    
    st.divider()
    
    # 데이터 표 출력
    st.dataframe(st.session_state.df, use_container_width=True)
    
    # 두 번째 핵심: 데이터 활용 (CSV 다운로드)
    csv = st.session_state.df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 수리 목록 CSV 내려받기",
        data=csv,
        file_name=f"chromebook_status_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

    # 향후 숙제: 알림 기능 예시 (PC 브라우저 알림 호출 가능)
    if repair_count > 0:
        st.warning(f"현재 수리가 필요한 기기가 {repair_count}대 있습니다. 확인해 주세요!")
