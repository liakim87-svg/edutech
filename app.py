import streamlit as st
import pandas as pd
from datetime import datetime
import os
import streamlit.components.v1 as components

# --- 1. 페이지 설정 및 상태 초기화 ---
st.set_page_config(page_title="Chromebook Manager", layout="wide")

DB_FILE = "chromebook_inventory_v3.csv"
CLASSES = ["1-1", "1-2", "2-1", "2-2", "3-1", "3-2"]
TOTAL_DEVICES = 122

def inject_notification_js():
    """브라우저 알림 자바스크립트 주입"""
    components.html(
        """
        <script>
        window.parent.sendNotification = function(title, body) {
            if (Notification.permission === 'granted') {
                new Notification(title, { body: body });
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

if 'df' not in st.session_state:
    st.session_state.df = initialize_data()

inject_notification_js()

# --- 2. 사이드바: 관리 도구 ---
st.sidebar.title("🛠️ 관리 도구")

# --- 기능 1: 학급별 일괄 업데이트 (추가된 기능) ---
st.sidebar.subheader("학급 일괄 처리")
batch_class = st.sidebar.selectbox("대상 학급 선택", CLASSES, key="batch_cls")
if st.sidebar.button(f"{batch_class} 전체 '이상 없음' 처리"):
    mask = st.session_state.df['학급'] == batch_class
    st.session_state.df.loc[mask, '상태'] = "이상 없음"
    st.session_state.df.loc[mask, '최종수정'] = datetime.now().strftime("%H:%M")
    st.session_state.df.to_csv(DB_FILE, index=False)
    st.sidebar.success(f"{batch_class} 모든 기기가 '이상 없음'으로 변경되었습니다.")
    st.rerun()

st.sidebar.divider()

# --- 기능 2: 개별 기기 업데이트 ---
with st.sidebar.form("update_form", clear_on_submit=True):
    st.write("### 개별 기기 수정")
    sel_class = st.selectbox("학급", CLASSES)
    class_devices = st.session_state.df[st.session_state.df['학급'] == sel_class]['기기번호'].tolist()
    sel_device = st.selectbox("기기번호", class_devices)
    new_status = st.radio("상태", ["이상 없음", "대여 중", "파손/점검", "분실"])
    new_note = st.text_input("특이사항")
    
    submitted = st.form_submit_button("업데이트")
    if submitted:
        idx = st.session_state.df[st.session_state.df['기기번호'] == sel_device].index[0]
        st.session_state.df.at[idx, '상태'] = new_status
        st.session_state.df.at[idx, '특이사항'] = new_note if new_note else "-"
        st.session_state.df.at[idx, '최종수정'] = datetime.now().strftime("%H:%M")
        st.session_state.df.to_csv(DB_FILE, index=False)
        st.rerun()

# --- 3. 메인 화면 ---
st.title("📱 크롬북 통합 관리 시스템")

# 대시보드
cols = st.columns(4)
total = len(st.session_state.df)
ok = len(st.session_state.df[st.session_state.df['상태'] == '이상 없음'])
rent = len(st.session_state.df[st.session_state.df['상태'] == '대여 중'])
issue = total - ok - rent

cols[0].metric("전체 기기", f"{total}대")
cols[1].metric("이상 없음", f"{ok}대", delta=f"{ok-total}", delta_color="off")
cols[2].metric("대여 중", f"{rent}대")
cols[3].metric("점검 필요", f"{issue}대")

st.divider()

# 필터 및 리스트
c1, c2 = st.columns([1, 3])
with c1:
    f_class = st.multiselect("학급 필터", CLASSES, default=CLASSES)
with c2:
    f_search = st.text_input("기기번호 검색 (예: C001)", "")

view_df = st.session_state.df.copy()
if f_class:
    view_df = view_df[view_df['학급'].isin(f_class)]
if f_search:
    view_df = view_df[view_df['기기번호'].str.contains(f_search, case=False)]

def status_style(val):
    colors = {"이상 없음": "color: #2E7D32", "대여 중": "color: #1565C0", "파손/점검": "color: #E65100", "분실": "color: #C62828"}
    return colors.get(val, "")

st.dataframe(
    view_df.style.map(status_style, subset=['상태']),
    use_container_width=True,
    hide_index=True
)

if st.sidebar.button("시스템 전체 초기화"):
    if os.path.exists(DB_FILE): os.remove(DB_FILE)
    st.session_state.clear()
    st.rerun()
