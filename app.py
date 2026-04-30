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
                    new Notification("관리자 알림 활성화 완료!", {
                        body: "이제 기기 이상 보고 시 실시간 알림이 전송됩니다.",
                        icon: 'https://cdn-icons-png.flaticon.com/512/564/564344.png'
                    });
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
    # 초기 학생 명단 데이터 (선생님 데이터 유지)
    init_data = []
    # (STUDENT_LIST 기반 생성 로직 동일)
    return pd.DataFrame() 

if 'df' not in st.session_state:
    from __main__ import STUDENT_LIST # 기존 리스트 참조용
    st.session_state.df = load_data()
    if st.session_state.df.empty: # 파일 없을시 생성
        init_data = []
        for sid, info in STUDENT_LIST.items():
            init_data.append({"학번": sid, "이름": info[0], "기기번호": f"CEU{info[1]}", "학급": f"{sid[0]}-{int(sid[1])}", "상태": "이상 없음", "특이사항": "", "최종수정": datetime.now().strftime("%Y-%m-%d %H:%M")})
        st.session_state.df = pd.DataFrame(init_data)
        st.session_state.df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')

if 'filter_status' not in st.session_state:
    st.session_state.filter_status = "전체"

# --- 2. 사이드바 (관리자/학생 기능 통합) ---
CLASSES = sorted(list(set(st.session_state.df['학급'])))

with st.sidebar:
    st.header("⚙️ 접속 모드")
    is_admin = st.checkbox("교사용 관리자 모드")
    
    if is_admin:
        st.divider()
        st.subheader("🔔 교사 알림")
        if st.button("알림 활성화", use_container_width=True):
            st.components.v1.html("<script>window.parent.requestPermission();</script>", height=0)
        
        st.divider()
        st.subheader("🚨 리셋")
        confirm_reset = st.checkbox("전체 초기화 승인")
        if st.button("🔥 전교생 리셋", use_container_width=True, disabled=not confirm_reset):
            st.session_state.df['상태'] = "이상 없음"; st.session_state.df['특이사항'] = ""; st.session_state.df['최종수정'] = datetime.now().strftime("%Y-%m-%d %H:%M")
            st.session_state.df.to_csv(DB_FILE, index=False, encoding='utf-8-sig'); st.rerun()

        st.divider()
        st.subheader("📋 학급 일괄")
        active_cls = st.selectbox("학급 선택", CLASSES, key="admin_cls")
        if st.button(f"✨ {active_cls} 전원 이상없음", use_container_width=True):
            st.session_state.df.loc[st.session_state.df['학급'] == active_cls, ['상태', '특이사항']] = ["이상 없음", ""]
            st.session_state.df.loc[st.session_state.df['학급'] == active_cls, '최종수정'] = datetime.now().strftime("%Y-%m-%d %H:%M")
            st.session_state.df.to_csv(DB_FILE, index=False, encoding='utf-8-sig'); st.rerun()
    else:
        st.divider()
        st.info("학생용 모드")
        active_cls = st.selectbox("우리 반 선택", CLASSES, key="student_cls")
        if st.button(f"✨ {active_cls} 전원 이상 없음 확인", use_container_width=True):
            st.session_state.df.loc[st.session_state.df['학급'] == active_cls, ['상태', '특이사항']] = ["이상 없음", ""]
            st.session_state.df.loc[st.session_state.df['학급'] == active_cls, '최종수정'] = datetime.now().strftime("%Y-%m-%d %H:%M")
            st.session_state.df.to_csv(DB_FILE, index=False, encoding='utf-8-sig'); st.rerun()

    st.divider()
    st.subheader("🛠️ 개별 상태 보고")
    cls_df = st.session_state.df[st.session_state.df['학급'] == active_cls]
    student_options = cls_df.apply(lambda x: f"{x['학번']} - {x['이름']}", axis=1).tolist()
    selected_student = st.selectbox("학생 선택", student_options)
    target_sid = selected_student.split(" - ")[0]
    row = st.session_state.df[st.session_state.df['학번'] == target_sid].iloc[0]
    
    new_status = st.radio("기기 상태", ["이상 없음", "대여", "파손/점검", "분실"], index=["이상 없음", "대여", "파손/점검", "분실"].index(row['상태']))

    with st.form("edit_form"):
        ph = "반납 예정일자를 쓰시오" if new_status == "대여" else ""
        new_note = st.text_input("특이사항/메모", value=row['특이사항'], placeholder=ph)
        if st.form_submit_button("저장하기"):
            idx = st.session_state.df[st.session_state.df['학번'] == target_sid].index[0]
            st.session_state.df.at[idx, '상태'] = new_status
            st.session_state.df.at[idx, '특이사항'] = new_note
            st.session_state.df.at[idx, '최종수정'] = datetime.now().strftime("%Y-%m-%d %H:%M")
            st.session_state.df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
            if new_status in ["파손/점검", "분실"]:
                st.components.v1.html(f"""<script>window.parent.sendNotification("🚨 크롬북 이상", "{active_cls} {row['이름']}: {new_status}");</script>""", height=0)
            st.rerun()

# --- 3. 메인 화면: 버튼형 대형 현황판 ---
st.title("🛡️ 상북중 크롬북 통합 현황판")

df = st.session_state.df
total = len(df); ok = len(df[df['상태']=='이상 없음']); rental = len(df[df['상태']=='대여']); repair = len(df[df['상태']=='파손/점검']); lost = len(df[df['상태']=='분실'])

# 스타일 정의
st.markdown("""
    <style>
    div.stButton > button {
        width: 100%; height: 120px; border-radius: 15px; border: 1px solid #ddd;
        background-color: white; transition: all 0.3s;
    }
    div.stButton > button:hover { border-color: #4CAF50; background-color: #f9f9f9; transform: translateY(-5px); }
    .btn-text { font-size: 16px; color: #666; margin-bottom: 5px; }
    .btn-num { font-size: 28px; font-weight: bold; color: #333; }
    </style>
""", unsafe_allow_html=True)

m_cols = st.columns(5)
with m_cols[0]:
    if st.button(f"📄 전체\n{total}대"): st.session_state.filter_status = "전체"
with m_cols[1]:
    if st.button(f"🟢 정상\n{ok}대"): st.session_state.filter_status = "이상 없음"
with m_cols[2]:
    if st.button(f"🏠 대여\n{rental}대"): st.session_state.filter_status = "대여"
with m_cols[3]:
    if st.button(f"🛠️ 파손\n{repair}대"): st.session_state.filter_status = "파손/점검"
with m_cols[4]:
    if st.button(f"🔍 분실\n{lost}대"): st.session_state.filter_status = "분실"

st.divider()
st.subheader(f"📍 현재 보기: {st.session_state.filter_status}")

# 필터링 및 표 출력
display_df = df if st.session_state.filter_status == "전체" else df[df['상태'] == st.session_state.filter_status]

def style_status(row):
    color = ''
    if row['상태'] == "이상 없음": color = 'background-color: #f0fff4;'
    elif row['상태'] == "대여": color = 'background-color: #ebf8ff;'
    elif row['상태'] == "파손/점검": color = 'background-color: #fff5f5; color: #742a2a; font-weight: bold;'
    elif row['상태'] == "분실": color = 'background-color: #2d3748; color: white; font-weight: bold;'
    return [color] * len(row)

st.dataframe(display_df.style.apply(style_status, axis=1), use_container_width=True, hide_index=True)
