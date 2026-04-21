import streamlit as st
import pandas as pd
from datetime import datetime
import os
import streamlit.components.v1 as components

# --- 1. 페이지 설정 및 상태 초기화 ---
st.set_page_config(page_title="크롬북 스마트 관리", layout="wide")

DB_FILE = "chromebook_db_v2.csv" # 버전 관리를 위해 파일명 변경
CLASSES = ["1-1", "1-2", "2-1", "2-2", "3-1", "3-2"]
TOTAL_DEVICES = 122

# 브라우저 알림을 위한 자바스크립트 함수
def inject_notification_js():
    components.html(
        """
        <script>
        function askPermission() {
            if (Notification.permission !== 'granted') {
                Notification.requestPermission();
            }
        }
        // 부모 창에서 호출할 수 있도록 설정
        window.parent.sendNotification = function(title, body) {
            if (Notification.permission === 'granted') {
                new Notification(title, { 
                    body: body, 
                    icon: 'https://cdn-icons-png.flaticon.com/512/683/683133.png' 
                });
                var audio = new Audio('https://actions.google.com/sounds/v1/alarms/beep_short.ogg');
                audio.play();
            } else {
                console.log("알림 권한이 없습니다.");
            }
        }
        askPermission();
        </script>
        """,
        height=0,
    )

def initialize_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    
    data = []
    # 기기번호를 C001부터 C122까지 생성
    per_class = TOTAL_DEVICES // len(CLASSES)
    rem = TOTAL_DEVICES % len(CLASSES)
    
    count = 0
    for i, cls in enumerate(CLASSES):
        num_in_cls = per_class + (1 if i < rem else 0)
        for s in range(1, num_in_cls + 1):
            count += 1
            data.append({
                "기기번호": f"C{count:03d}", # C001, C002... 형식
                "학급": cls,
                "번호": s,
                "상태": "이상 없음",
                "특이사항": "-",
                "최종수정": datetime.now().strftime("%H:%M:%S")
            })
    df = pd.DataFrame(data)
    df.to_csv(DB_FILE, index=False)
    return df

if 'df' not in st.session_state:
    st.session_state.df = initialize_data()

inject_notification_js()

# --- 2. 사이드바: 입력 및 설정 ---
st.sidebar.title("🛠️ 관리 도우미")

# 알림 권한 유도 버튼
if st.sidebar.button("🔔 알림 권한 허용하기"):
    st.info("브라우저 상단(주소창 옆)에 뜨는 '권한 요청'에서 [허용]을 눌러주세요.")

with st.sidebar.form("update_form"):
    st.write("### 상태 업데이트")
    sel_class = st.selectbox("학급 선택", CLASSES)
    # 선택된 학급에 해당하는 기기만 필터링
    filtered_devices = st.session_state.df[st.session_state.df['학급'] == sel_class]['기기번호'].tolist()
    sel_device = st.selectbox("기기번호 선택", filtered_devices)
    
    new_status = st.radio("기기 상태", ["이상 없음", "대여 중", "파손/점검", "분실"])
    new_note = st.text_input("특이사항", placeholder="고장 증상 등 입력")
    
    submitted = st.form_submit_button("데이터 기록 및 알림 전송")
    
    if submitted:
        idx = st.session_state.df[st.session_state.df['기기번호'] == sel_device].index[0]
        st.session_state.df.at[idx, '상태'] = new_status
        st.session_state.df.at[idx, '특이사항'] = new_note if new_note else "-"
        st.session_state.df.at[idx, '최종수정'] = datetime.now().strftime("%H:%M:%S")
        st.session_state.df.to_csv(DB_FILE, index=False)
        
        # 관리자 브라우저에 알림 전송
        msg = f"[{sel_class}] {sel_device}가 '{new_status}' 상태로 변경되었습니다."
        components.html(f"<script>window.parent.sendNotification('크롬북 상태 변경', '{msg}');</script>", height=0)
        
        st.sidebar.success(f"{sel_device} 업데이트 완료!")
        st.rerun()

# --- 3. 메인 화면 ---
st.title("💻 크롬북 실시간 통합 관리 시스템")

# 상단 지표 요약
m1, m2, m3, m4 = st.columns(4)
m1.metric("전체 기기", f"{len(st.session_state.df)}대")
m2.metric("이상 없음", f"{len(st.session_state.df[st.session_state.df['상태'] == '이상 없음'])}대")
m3.metric("대여 중", f"{len(st.session_state.df[st.session_state.df['상태'] == '대여 중'])}대")
m4.metric("수리/분실", f"{len(st.session_state.df[st.session_state.df['상태'].isin(['파손/점검', '분실'])])}대")

st.markdown("---")

# 검색 필터
st.subheader("📋 전체 기기 명부")
search_query = st.text_input("🔎 기기번호(예: C001) 또는 학급 검색", "")
view_df = st.session_state.df
if search_query:
    view_df = view_df[view_df['기기번호'].str.contains(search_query, case=False) | view_df['학급'].str.contains(search_query)]

# 데이터프레임 스타일링 함수
def apply_color(val):
    color = "black"
    if val == "이상 없음": color = "#2e7d32"
    elif val == "대여 중": color = "#1565c0"
    elif val == "파손/점검": color = "#ef6c00"
    elif val == "분실": color = "#c62828"
    return f'color: {color}; font-weight: bold'

st.dataframe(
    view_df.style.applymap(apply_color, subset=['상태']),
    use_container_width=True,
    hide_index=True
)

# 데이터 초기화 버튼
if st.sidebar.button("⚠️ 전체 데이터 초기화"):
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    st.session_state.clear()
    st.rerun()
