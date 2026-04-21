import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="크롬북 통합 관리", layout="wide")

# 알림 기능을 위한 JavaScript (브라우저 알림 호출)
st.markdown("""
    <script>
    function sendNotification(title, body) {
        if (Notification.permission === "granted") {
            new Notification(title, { body: body });
        } else if (Notification.permission !== "denied") {
            Notification.requestPermission().then(permission => {
                if (permission === "granted") {
                    new Notification(title, { body: body });
                }
            });
        }
    }
    </script>
""", unsafe_allow_html=True)

# UI 스타일 개선
st.markdown("""
    <style>
    div.stButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
    }
    .main-title {
        font-size: 28px;
        font-weight: bold;
        margin-bottom: 20px;
        color: #1E3A8A;
    }
    </style>
""", unsafe_allow_html=True)

DB_FILE = "chromebook_master_db.csv"
CLASSES = ["1-1", "1-2", "2-1", "2-2", "3-1", "3-2"]
TOTAL_DEVICES = 122

def load_data():
    if os.path.exists(DB_FILE):
        try:
            return pd.read_csv(DB_FILE)
        except:
            pass
    
    data = []
    current_id = 1
    per_class = TOTAL_DEVICES // len(CLASSES)
    remainder = TOTAL_DEVICES % len(CLASSES)
    
    for i, cls in enumerate(CLASSES):
        count_for_this_class = per_class + (1 if i < remainder else 0)
        for student_num in range(1, count_for_this_class + 1):
            if current_id <= TOTAL_DEVICES:
                data.append({
                    "기기번호": f"C{current_id:03d}",
                    "학급": cls,
                    "번호": student_num,
                    "상태": "이상 없음",
                    "특이사항": "-",
                    "최종수정": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                current_id += 1
    df = pd.DataFrame(data)
    df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
    return df

if 'df' not in st.session_state:
    st.session_state.df = load_data()
if 'filter_mode' not in st.session_state:
    st.session_state.filter_mode = "전체"

def save_to_file():
    st.session_state.df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')

# --- 2. 사이드바 ---
with st.sidebar:
    st.header("⚡ 학급별 일괄 처리")
    selected_cls = st.selectbox("대상 학급 선택", CLASSES, key="batch_cls_select")
    if st.button(f"✨ {selected_cls} 이상없음 일괄처리"):
        st.session_state.df.loc[st.session_state.df['학급'] == selected_cls, '상태'] = "이상 없음"
        st.session_state.df.loc[st.session_state.df['학급'] == selected_cls, '최종수정'] = datetime.now().strftime("%Y-%m-%d %H:%M")
        save_to_file()
        st.success(f"✅ {selected_cls} 일괄 처리 완료")
        st.rerun()

    st.divider()

    st.header("🛠️ 개별 상태 관리")
    with st.form("single_edit_form"):
        target_id = st.selectbox("기기번호 선택", st.session_state.df['기기번호'].tolist())
        new_status = st.radio("변경할 상태", ["이상 없음", "대여 중", "파손/점검", "분실"], horizontal=False)
        new_note = st.text_input("특이사항 입력")
        
        if st.form_submit_button("💾 상태 업데이트"):
            idx = st.session_state.df[st.session_state.df['기기번호'] == target_id].index[0]
            st.session_state.df.at[idx, '상태'] = new_status
            st.session_state.df.at[idx, '특이사항'] = new_note if new_note else "-"
            st.session_state.df.at[idx, '최종수정'] = datetime.now().strftime("%Y-%m-%d %H:%M")
            save_to_file()
            
            # 파손/점검/분실 시 컴퓨터 알림 발생
            if new_status in ["파손/점검", "분실"]:
                st.components.v1.html(f"""
                    <script>
                    window.parent.sendNotification("🚨 크롬북 이상 발생!", "{target_id}번 기기 상태가 '{new_status}'로 변경되었습니다.");
                    </script>
                """, height=0)
                
            st.success(f"✔️ {target_id} 업데이트 완료")
            st.rerun()

# --- 3. 메인 대시보드 ---
st.markdown('<div class="main-title">💻 크롬북 스마트 통합 관리 시스템</div>', unsafe_allow_html=True)

df = st.session_state.df
c1, c2, c3, c4 = st.columns(4)

with c1:
    if st.button(f"📊 전체\n{len(df)}대"): st.session_state.filter_mode = "전체"
with c2:
    n_count = len(df[df['상태'] == "이상 없음"])
    if st.button(f"✅ 이상없음\n{n_count}대"): st.session_state.filter_mode = "이상 없음"
with c3:
    r_count = len(df[df['상태'] == "대여 중"])
    if st.button(f"🏠 대여중\n{r_count}대"): st.session_state.filter_mode = "대여 중"
with c4:
    e_count = len(df[df['상태'].isin(["파손/점검", "분실"])])
    if st.button(f"🚨 점검필요\n{e_count}대"): st.session_state.filter_mode = "점검필요"

st.divider()
st.subheader(f"📍 {st.session_state.filter_mode} 현황")

view_df = df.copy()
if st.session_state.filter_mode == "이상 없음":
    view_df = view_df[view_df['상태'] == "이상 없음"]
elif st.session_state.filter_mode == "대여 중":
    view_df = view_df[view_df['상태'] == "대여 중"]
elif st.session_state.filter_mode == "점검필요":
    view_df = view_df[view_df['상태'].isin(["파손/점검", "분실"])]

# 표 스타일
def color_status(val):
    if val == "이상 없음": return 'background-color: #DCFCE7; color: #166534'
    if val == "대여 중": return 'background-color: #DBEAFE; color: #1E40AF'
    return 'background-color: #FEE2E2; color: #991B1B'

st.dataframe(
    view_df.style.map(color_status, subset=['상태']),
    use_container_width=True,
    hide_index=True
)
