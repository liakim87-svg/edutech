import streamlit as st
import pandas as pd
from datetime import datetime
import os
import streamlit.components.v1 as components

# --- 1. 페이지 설정 및 상태 초기화 ---
st.set_page_config(page_title="Chromebook Manager", layout="wide")

# 데이터 파일 및 설정
DB_FILE = "chromebook_inventory_v3.csv"
CLASSES = ["1-1", "1-2", "2-1", "2-2", "3-1", "3-2"]
TOTAL_DEVICES = 122

def inject_notification_js():
    """브라우저 알림 자바스크립트 주입 (에러 방지를 위해 문자열 내 이모지 제거)"""
    components.html(
        """
        <script>
        window.parent.sendNotification = function(title, body) {
            if (Notification.permission === 'granted') {
                new Notification(title, { body: body });
                try {
                    var audio = new Audio('https://actions.google.com/sounds/v1/alarms/beep_short.ogg');
                    audio.play();
                } catch (e) { console.log("Audio play failed"); }
            }
        }
        if (Notification.permission !== 'granted' && Notification.permission !== 'denied') {
            Notification.requestPermission();
        }
        </script>
        """,
        height=0,
    )

def initialize_data():
    """C001 ~ C122 번호 체계로 데이터 초기화"""
    if os.path.exists(DB_FILE):
        try:
            return pd.read_csv(DB_FILE)
        except:
            pass
    
    data = []
    per_class = TOTAL_DEVICES // len(CLASSES)
    rem = TOTAL_DEVICES % len(CLASSES)
    
    count = 1
    for i, cls in enumerate(CLASSES):
        num_in_cls = per_class + (1 if i < rem else 0)
        for s in range(1, num_in_cls + 1):
            if count <= TOTAL_DEVICES:
                data.append({
                    "기기번호": f"C{count:03d}",
                    "학급": cls,
                    "번호": s,
                    "상태": "이상 없음",
                    "특이사항": "-",
                    "최종수정": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                count += 1
    df = pd.DataFrame(data)
    df.to_csv(DB_FILE, index=False)
    return df

# 세션 상태 초기화
if 'df' not in st.session_state:
    st.session_state.df = initialize_data()

inject_notification_js()

# --- 2. 사이드바: 업데이트 폼 ---
st.sidebar.title("도우미 전용")
st.sidebar.info(f"대상 학급: {', '.join(CLASSES)}")

with st.sidebar.form("update_form", clear_on_submit=True):
    st.write("### 상태 업데이트")
    sel_class = st.selectbox("학급 선택", CLASSES)
    
    # 해당 학급 기기 필터링
    class_devices = st.session_state.df[st.session_state.df['학급'] == sel_class]['기기번호'].tolist()
    sel_device = st.selectbox("기기번호 선택", class_devices)
    
    new_status = st.radio("상태 변경", ["이상 없음", "대여 중", "파손/점검", "분실"])
    new_note = st.text_input("특이사항 (선택사항)")
    
    submitted = st.form_submit_button("기록하기")
    
    if submitted:
        # 데이터 업데이트
        idx = st.session_state.df[st.session_state.df['기기번호'] == sel_device].index[0]
        st.session_state.df.at[idx, '상태'] = new_status
        st.session_state.df.at[idx, '특이사항'] = new_note if new_note else "-"
        st.session_state.df.at[idx, '최종수정'] = datetime.now().strftime("%H:%M")
        
        # 파일 저장
        st.session_state.df.to_csv(DB_FILE, index=False)
        
        # 알림 전송 (JS 호출)
        msg = f"{sel_device}가 {new_status} 상태로 변경되었습니다."
        components.html(f"<script>window.parent.sendNotification('Chromebook Update', '{msg}');</script>", height=0)
        
        st.success(f"{sel_device} 업데이트 완료")
        st.rerun()

# --- 3. 메인 화면 ---
st.title("크롬북 통합 관리 현황")

# 상단 대시보드 (에러 방지를 위해 간단하게 구현)
cols = st.columns(4)
cols[0].metric("전체", f"{len(st.session_state.df)}대")
cols[1].metric("사용 가능", f"{len(st.session_state.df[st.session_state.df['상태'] == '이상 없음'])}대")
cols[2].metric("대여중", f"{len(st.session_state.df[st.session_state.df['상태'] == '대여 중'])}대")
cols[3].metric("점검필요", f"{len(st.session_state.df[st.session_state.df['상태'].isin(['파손/점검', '분실'])])}대")

st.divider()

# 검색 및 상세 리스트
st.subheader("전체 기기 명부")
search = st.text_input("검색 (기기번호 또는 학급)", "")

view_df = st.session_state.df.copy()
if search:
    view_df = view_df[view_df['기기번호'].str.contains(search, case=False) | view_df['학급'].str.contains(search)]

# Pandas 버전에 따른 스타일링 호환성 처리 (map 사용)
def status_style(val):
    if val == "이상 없음": return 'color: green'
    if val == "대여 중": return 'color: blue'
    if val == "파손/점검": return 'color: orange'
    if val == "분실": return 'color: red'
    return ''

st.dataframe(
    view_df.style.map(status_style, subset=['상태']),
    use_container_width=True,
    hide_index=True
)

# 데이터 리셋 기능 (사이드바 하단)
if st.sidebar.button("데이터 초기화"):
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    st.session_state.clear()
    st.rerun()
