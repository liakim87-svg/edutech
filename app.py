import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- 1. 페이지 설정 및 알림 JS ---
st.set_page_config(page_title="상북중 크롬북 통합 관리", layout="wide")

st.markdown("""
    <script>
    window.requestPermission = function() {
        if (!("Notification" in window)) {
            alert("이 브라우저는 알림을 지원하지 않습니다.");
        } else {
            Notification.requestPermission().then(function (permission) {
                if (permission === "granted") {
                    new Notification("관리자 알림 활성화 완료!");
                }
            });
        }
    }
    window.sendNotification = function(title, body) {
        if (Notification.permission === "granted") {
            new Notification(title, { body: body, icon: 'https://cdn-icons-png.flaticon.com/512/564/564344.png' });
        }
    }
    </script>
""", unsafe_allow_html=True)

DB_FILE = "chromebook_master_db_v16.csv"

# [데이터 로드]
def load_data():
    if os.path.exists(DB_FILE):
        try:
            return pd.read_csv(DB_FILE, dtype={'학번': str}).fillna("")
        except: pass
    return pd.DataFrame()

if 'df' not in st.session_state:
    st.session_state.df = load_data()
if 'filter_status' not in st.session_state:
    st.session_state.filter_status = "전체"

# --- 2. 사이드바 (모든 입력창 집중 배치) ---
df = st.session_state.df
CLASSES = sorted(list(set(df['학급']))) if not df.empty else []

with st.sidebar:
    st.header("⚙️ 접속 및 관리")
    is_admin = st.checkbox("교사용 관리자 모드")
    
    if is_admin:
        st.subheader("🔔 교사 알림")
        if st.button("알림 활성화", use_container_width=True):
            st.components.v1.html("<script>window.parent.requestPermission();</script>", height=0)
        
        st.subheader("🚨 데이터 초기화")
        confirm_reset = st.checkbox("리셋 승인")
        if st.button("🔥 전교생 기록 초기화", use_container_width=True, disabled=not confirm_reset):
            st.session_state.df['상태'] = "이상 없음"
            st.session_state.df['특이사항'] = ""
            st.session_state.df['최종수정'] = datetime.now().strftime("%Y-%m-%d")
            st.session_state.df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
            st.rerun()
            
        st.subheader("📋 학급 일괄")
        admin_cls = st.selectbox("일괄 처리 학급", CLASSES, key="admin_cls_side")
        if st.button(f"✨ {admin_cls} 전원 정상", use_container_width=True):
            st.session_state.df.loc[st.session_state.df['학급'] == admin_cls, ['상태', '특이사항']] = ["이상 없음", ""]
            st.session_state.df.loc[st.session_state.df['학급'] == admin_cls, '최종수정'] = datetime.now().strftime("%Y-%m-%d")
            st.session_state.df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
            st.rerun()
    
    st.divider()
    st.header("🛠️ 기기 상태 보고")
    if not df.empty:
        # 사이드바에서 학급 및 학생 선택
        active_cls = st.selectbox("우리 반 선택", CLASSES, key="side_cls_sel")
        cls_df = df[df['학급'] == active_cls]
        student_list = cls_df.apply(lambda x: f"{x['학번']} {x['이름']}", axis=1).tolist()
        selected_student = st.selectbox("학생 선택", student_list, key="side_stu_sel")
        
        target_sid = selected_student.split(" ")[0]
        row = df[df['학번'] == target_sid].iloc[0]
        
        st.caption(f"현재: {row['상태']} | {row['특이사항']}")
        
        with st.form("side_status_form"):
            new_status = st.radio("변경 상태", ["이상 없음", "대여", "파손/점검", "분실"], 
                                  index=["이상 없음", "대여", "파손/점검", "분실"].index(row['상태']))
            
            # 대여 시 가이드 문구 자동화
            ph = "반납 예정일자를 입력하세요" if new_status == "대여" else "메모 입력"
            new_note = st.text_input("특이사항/메모", value=row['특이사항'], placeholder=ph)
            
            if st.form_submit_button("상태 저장하기", use_container_width=True):
                idx = df[df['학번'] == target_sid].index[0]
                st.session_state.df.at[idx, '상태'] = new_status
                st.session_state.df.at[idx, '특이사항'] = new_note
                st.session_state.df.at[idx, '최종수정'] = datetime.now().strftime("%Y-%m-%d")
                st.session_state.df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
                
                if new_status in ["파손/점검", "분실"]:
                    st.components.v1.html(f"<script>window.parent.sendNotification('🚨 이상 보고', '{active_cls} {target_sid}: {new_status}');</script>", height=0)
                st.rerun()

# --- 3. 메인 화면 상단 (로고 + 타이틀) ---
logo_path = "상북중로고.png"
t_col1, t_col2 = st.columns([1, 8])
with t_col1:
    if os.path.exists(logo_path):
        st.image(logo_path, width=100)
    else:
        st.markdown("<h1 style='margin:0;'>🏫</h1>", unsafe_allow_html=True)
with t_col2:
    st.markdown("<h1 style='margin-top:10px;'>상북중학교 크롬북 통합 현황판</h1>", unsafe_allow_html=True)

# --- 4. 투명 대시보드 ---
st.markdown("""
    <style>
    div.stButton > button {
        border: none !important; background-color: transparent !important;
        box-shadow: none !important; color: inherit !important;
        transition: transform 0.2s; width: 100% !important; text-align: center;
    }
    div.stButton > button:hover { transform: scale(1.05); color: #004080 !important; }
    </style>
""", unsafe_allow_html=True)

stats = {
    "전체": len(df), "정상": len(df[df['상태']=='이상 없음']), 
    "대여": len(df[df['상태']=='대여']), "파손": len(df[df['상태']=='파손/점검']), 
    "분실": len(df[df['상태']=='분실'])
}

m_cols = st.columns(5)
with m_cols[0]:
    if st.button(f"📄 전체\n\n{stats['전체']}대"): st.session_state.filter_status = "전체"
with m_cols[1]:
    if st.button(f"🟢 정상\n\n{stats['정상']}대"): st.session_state.filter_status = "이상 없음"
with m_cols[2]:
    if st.button(f"🏠 대여\n\n{stats['대여']}대"): st.session_state.filter_status = "대여"
with m_cols[3]:
    if st.button(f"🛠️ 파손\n\n{stats['파손']}대"): st.session_state.filter_status = "파손/점검"
with m_cols[4]:
    if st.button(f"🔍 분실\n\n{stats['분실']}대"): st.session_state.filter_status = "분실"

st.divider()

# --- 5. 목록 표시 (와이드 뷰) ---
st.subheader(f"📍 목록 필터: {st.session_state.filter_status}")
display_df = df if st.session_state.filter_status == "전체" else df[df['상태'] == st.session_state.filter_status]

def style_status(row):
    color = ''
    if row['상태'] == "이상 없음": color = 'background-color: #f0fff4;'
    elif row['상태'] == "대여": color = 'background-color: #ebf8ff;'
    elif row['상태'] == "파손/점검": color = 'background-color: #fff5f5; color: #742a2a; font-weight: bold;'
    elif row['상태'] == "분실": color = 'background-color: #2d3748; color: white; font-weight: bold;'
    return [color] * len(row)

st.dataframe(display_df.style.apply(style_status, axis=1), use_container_width=True, hide_index=True)
