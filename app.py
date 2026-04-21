import streamlit as st
import pandas as pd
from datetime import datetime
import os
import streamlit.components.v1 as components

# --- 1. 페이지 설정 및 상태 초기화 ---
st.set_page_config(page_title="크롬북 스마트 관리", layout="wide")

DB_FILE = "chromebook_db.csv"
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
        // 이 함수는 부모창에서 호출할 수 있도록 설정
        window.parent.sendNotification = function(title, body) {
            if (Notification.permission === 'granted') {
                new Notification(title, { body: body, icon: 'https://cdn-icons-png.flaticon.com/512/683/683133.png' });
                var audio = new Audio('https://actions.google.com/sounds/v1/alarms/beep_short.ogg');
                audio.play();
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
    per_class = TOTAL_DEVICES // len(CLASSES)
    rem = TOTAL_DEVICES % len(CLASSES)
    
    count = 0
    for i, cls in enumerate(CLASSES):
        num_in_cls = per_class + (1 if i < rem else 0)
        for s in range(1, num_in_cls + 1):
            count += 1
            data.append({
                "기기번호": f"CB-{count:03d}",
                "학급": cls,
                "번호": s,
                "상태": "이상 없음",
                "특이사항": "-",
                "최종수정": datetime.now().strftime("%H:%M:%S")
            })
    return pd.DataFrame(data)

if 'df' not in st.session_state:
    st.session_state.df = initialize_data()
    st.session_state.last_update = ""

inject_notification_js()

# --- 2. 사이드바: 입력 및 설정 ---
st.sidebar.title("🛠️ 관리 도우미")

# 알림 권한 요청 버튼 (처음 한 번 실행 필요)
if st.sidebar.button("🔔 알림 권한 허용하기"):
    st.info("브라우저 상단에서 알림 권한을 '허용'으로 설정해주세요.")

with st.sidebar.form("update_form"):
    sel_class = st.selectbox("학급", CLASSES)
    class_df = st.session_state.df[st.session_state.df['학급'] == sel_class]
    sel_device = st.selectbox("기기번호", class_df['기기번호'].tolist())
    
    new_status = st.radio("상태", ["이상 없음", "대여 중", "파손/점검", "분실"])
    new_note = st.text_input("특이사항", placeholder="없으면 비워둠")
    
    submitted = st.form_submit_button("상태 업데이트")
    
    if submitted:
        idx = st.session_state.df[st.session_state.df['기기번호'] == sel_device].index[0]
        st.session_state.df.at[idx, '상태'] = new_status
        st.session_state.df.at[idx, '특이사항'] = new_note if new_note else "-"
        st.session_state.df.at[idx, '최종수정'] = datetime.now().strftime("%H:%M:%S")
        st.session_state.df.to_csv(DB_FILE, index=False)
        
        # 알림 전송 자바스크립트 호출
        msg = f"{sel_class}의 {sel_device} 상태가 '{new_status}'로 변경되었습니다."
        components.html(f"<script>window.parent.sendNotification('기기 상태 업데이트', '{msg}');</script>", height=0)
        
        st.sidebar.success("기록 완료!")
        st.rerun()

# --- 3. 메인 화면 ---
st.title("💻 크롬북 실시간 통합 관리")

# 상단 요약 지표
c1, c2, c3, c4 = st.columns(4)
c1.metric("전체", f"{len(st.session_state.df)}대")
c2.metric("이상 없음", f"{len(st.session_state.df[st.session_state.df['상태'] == '이상 없음'])}대")
c3.metric("대여 중", f"{len(st.session_state.df[st.session_state.df['상태'] == '대여 중'])}대")
c4.metric("관리 주의", f"{len(st.session_state.df[st.session_state.df['상태'].isin(['파손/점검', '분실'])])}대")

st.markdown("---")

# 학급별 현황 그래프
st.subheader("📊 학급별 이상 없음 비율")
stats = []
for c in CLASSES:
    total = len(st.session_state.df[st.session_state.df['학급'] == c])
    ok = len(st.session_state.df[(st.session_state.df['학급'] == c) & (st.session_state.df['상태'] == '이상 없음')])
    stats.append({"학급": c, "완료율(%)": (ok/total)*100})
st.bar_chart(pd.DataFrame(stats), x="학급", y="완료율(%)")

# 데이터 필터 및 테이블
st.subheader("📋 실시간 기기 명부")
search = st.text_input("🔎 학급 또는 기기번호 검색")
view_df = st.session_state.df
if search:
    view_df = view_df[view_df['학급'].str.contains(search) | view_df['기기번호'].str.contains(search)]

def style_df(s):
    bg = ""
    if s == "이상 없음": bg = "color: #2e7d32; font-weight: bold;"
    elif s == "대여 중": bg = "color: #1565c0;"
    elif s == "파손/점검": bg = "background-color: #fff3e0; color: #ef6c00;"
    elif s == "분실": bg = "background-color: #ffebee; color: #c62828;"
    return bg

st.dataframe(
    view_df.style.applymap(style_df, subset=['상태']),
    use_container_width=True,
    hide_index=True
)

if st.sidebar.button("🗑️ 모든 데이터 초기화"):
    if os.path.exists(DB_FILE): os.remove(DB_FILE)
    st.session_state.clear()
    st.rerun()
