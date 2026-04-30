import streamlit as st
import pandas as pd
from datetime import datetime
import os
import time

# --- 1. 페이지 설정 및 강화된 알림 JS ---
st.set_page_config(page_title="상북중 크롬북 통합 관리", layout="wide")

st.markdown("""
    <script>
    // 알림 권한 요청
    window.requestPermission = function() {
        if (!("Notification" in window)) {
            alert("이 브라우저는 알림을 지원하지 않습니다.");
        } else {
            Notification.requestPermission().then(function (permission) {
                if (permission === "granted") {
                    alert("알림 권한이 허용되었습니다!");
                    new Notification("알림 설정 완료", { body: "이제 기기 이상 시 알림이 전송됩니다." });
                } else {
                    alert("알림 권한이 거부되었습니다. 주소창 왼쪽 자물쇠 아이콘에서 알림을 '허용'으로 바꿔주세요.");
                }
            });
        }
    }

    // 알림 전송 (신뢰성 강화)
    window.sendNotification = function(title, body) {
        if (Notification.permission === "granted") {
            try {
                new Notification(title, { 
                    body: body, 
                    icon: 'https://cdn-icons-png.flaticon.com/512/564/564344.png' 
                });
            } catch (e) {
                console.error("알림 전송 실패:", e);
            }
        }
    }
    </script>
""", unsafe_allow_html=True)

DB_FILE = "chromebook_master_db_v16.csv"

def load_data():
    if os.path.exists(DB_FILE):
        try: return pd.read_csv(DB_FILE, dtype={'학번': str}).fillna("")
        except: pass
    return pd.DataFrame()

if 'df' not in st.session_state:
    st.session_state.df = load_data()
if 'filter_status' not in st.session_state:
    st.session_state.filter_status = "전체"

# --- 2. 사이드바 구성 ---
df = st.session_state.df
CLASSES = sorted(list(set(df['학급']))) if not df.empty else []

with st.sidebar:
    st.header("⚙️ 접속 및 관리")
    is_admin = st.checkbox("교사용 관리자 모드")
    
    if is_admin:
        st.subheader("🔔 알림 설정")
        if st.button("🔔 알림 활성화 하기", use_container_width=True):
            st.components.v1.html("<script>window.parent.requestPermission();</script>", height=0)
        st.caption("※ 버튼을 누르고 브라우저 상단에서 '허용'을 꼭 선택하세요.")
        
        st.divider()
        st.subheader("🚨 데이터 리셋")
        confirm_reset = st.checkbox("초기화 승인")
        if st.button("전체 기록 리셋", use_container_width=True, disabled=not confirm_reset):
            st.session_state.df['상태'] = "이상 없음"
            st.session_state.df['특이사항'] = ""
            st.session_state.df['최종수정'] = datetime.now().strftime("%Y-%m-%d")
            st.session_state.df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
            st.rerun()
    else:
        active_cls = st.selectbox("우리 반 선택", CLASSES, key="side_cls_sel")
        if st.button(f"✨ {active_cls} 전원 이상 없음", use_container_width=True):
            st.session_state.df.loc[st.session_state.df['학급'] == active_cls, ['상태', '특이사항']] = ["이상 없음", ""]
            st.session_state.df.loc[st.session_state.df['학급'] == active_cls, '최종수정'] = datetime.now().strftime("%Y-%m-%d")
            st.session_state.df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
            st.rerun()

    st.divider()
    st.header("🛠️ 상태 보고")
    if not df.empty:
        if is_admin: # 관리자 모드일 때도 학급 선택 가능하게
            active_cls = st.selectbox("보고 대상 학급", CLASSES, key="admin_cls_sel")
            
        cls_df = df[df['학급'] == active_cls]
        student_list = cls_df.apply(lambda x: f"{x['학번']} {x['이름']}", axis=1).tolist()
        selected_student = st.selectbox("학생 선택", student_list, key="side_stu_sel")
        
        target_sid = selected_student.split(" ")[0]
        row = df[df['학번'] == target_sid].iloc[0]
        
        new_status = st.radio("상태 변경", ["이상 없음", "대여", "파손/점검", "분실"], 
                              index=["이상 없음", "대여", "파손/점검", "분실"].index(row['상태']), key="status_radio")
        
        ph = "반납 예정일자를 입력하세요" if new_status == "대여" else "메모 입력"

        with st.form("side_status_form"):
            new_note = st.text_input("특이사항/메모", value=row['특이사항'] if new_status == row['상태'] else "", placeholder=ph)
            
            if st.form_submit_button("상태 저장하기", use_container_width=True):
                idx = df[df['학번'] == target_sid].index[0]
                st.session_state.df.at[idx, '상태'] = new_status
                st.session_state.df.at[idx, '특이사항'] = new_note
                st.session_state.df.at[idx, '최종수정'] = datetime.now().strftime("%Y-%m-%d")
                st.session_state.df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
                
                # [수정 포인트] 알림 전송 후 0.5초 대기하여 브라우저가 알림을 띄울 시간을 줌
                if new_status in ["파손/점검", "분실"]:
                    st.components.v1.html(f"""
                        <script>
                        window.parent.sendNotification('🚨 기기 이상 보고', '{active_cls} {target_sid} {row['이름']}: {new_status}');
                        setTimeout(function(){{ window.parent.location.reload(); }}, 500);
                        </script>
                    """, height=0)
                else:
                    st.rerun()

# --- 3. 메인 화면 (기존 디자인 유지) ---
logo_path = "상북중로고.png"
t_col1, t_col2 = st.columns([1, 8])
with t_col1:
    if os.path.exists(logo_path): st.image(logo_path, width=100)
    else: st.markdown("<h1 style='margin:0;'>🏫</h1>", unsafe_allow_html=True)
with t_col2: st.markdown("<h1 style='margin-top:10px;'>상북중학교 크롬북 통합 현황판</h1>", unsafe_allow_html=True)

# ... (대시보드 버튼 및 표 출력 코드 유지) ...
