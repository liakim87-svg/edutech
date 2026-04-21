import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- 1. 페이지 설정 및 초기화 ---
st.set_page_config(page_title="크롬북 통합 관리", layout="wide")

# 알림 기능을 위한 JavaScript
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

# --- 2. 사이드바 (UI 구조 핵심 수정) ---
with st.sidebar:
    st.header("🏫 학급 관리")
    # 1단계: 관리할 학급 선택
    active_cls = st.selectbox("관리할 학급 선택", CLASSES)
    
    # 2단계: 해당 학급 일괄 처리 버튼 (학급 밑으로 이동)
    st.markdown(f"**[{active_cls}]** 학급 전체 관리")
    if st.button(f"✨ {active_cls} 전원 '이상 없음'으로 초기화", use_container_width=True):
        st.session_state.df.loc[st.session_state.df['학급'] == active_cls, '상태'] = "이상 없음"
        st.session_state.df.loc[st.session_state.df['학급'] == active_cls, '최종수정'] = datetime.now().strftime("%Y-%m-%d %H:%M")
        save_to_file()
        st.success(f"{active_cls} 학급이 초기화되었습니다.")
        st.rerun()
    
    st.divider()
    
    # 3단계: 개별 기기 상태 업데이트
    st.header("🛠️ 개별 상태 수정")
    cls_devices = st.session_state.df[st.session_state.df['학급'] == active_cls]
    device_options = cls_devices['기기번호'].tolist()
    
    if not device_options:
        st.warning("선택한 학급에 등록된 기기가 없습니다.")
    else:
        with st.form("edit_form"):
            target_id = st.selectbox("대상 기기 번호", device_options)
            
            # 선택된 기기의 실시간 데이터 추출
            current_row = st.session_state.df[st.session_state.df['기기번호'] == target_id].iloc[0]
            st.caption(f"현재 정보: {current_row['학급']}반 {current_row['번호']}번 학생 기기")
            
            new_status = st.radio("상태 변경", ["이상 없음", "대여 중", "파손/점검", "분실"], 
                                 index=["이상 없음", "대여 중", "파손/점검", "분실"].index(current_row['상태']))
            new_note = st.text_input("특이사항", value=current_row['특이사항'])
            
            if st.form_submit_button("상태 저장"):
                idx = st.session_state.df[st.session_state.df['기기번호'] == target_id].index[0]
                
                st.session_state.df.at[idx, '상태'] = new_status
                st.session_state.df.at[idx, '특이사항'] = new_note if new_note else "-"
                st.session_state.df.at[idx, '최종수정'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                save_to_file()
                
                # 브라우저 알림 전송 (파손/분실 시)
                if new_status in ["파손/점검", "분실"]:
                    st.components.v1.html(f"""
                        <script>
                        window.parent.sendNotification("🚨 크롬북 이상 발견", "{active_cls} {current_row['번호']}번({target_id}): {new_status}");
                        </script>
                    """, height=0)
                
                st.success(f"{target_id} 수정 완료")
                st.rerun()

# --- 3. 메인 화면 ---
st.title("💻 크롬북 통합 현황판")

# 상단 대시보드
df = st.session_state.df
col1, col2, col3, col4 = st.columns(4)
col1.metric("전체 기기", f"{len(df)}대")
col2.metric("🟢 정상", f"{len(df[df['상태']=='이상 없음'])}대")
col3.metric("🏠 대여중", f"{len(df[df['상태']=='대여 중'])}대")
col4.metric("🚨 점검/분실", f"{len(df[df['상태'].isin(['파손/점검', '분실'])])}대")

st.divider()

# 필터 및 테이블 컨트롤
f1, f2, f3, f4, f5 = st.columns([1,1,1,1,2])
if f1.button("전체 보기", use_container_width=True): st.session_state.filter_mode = "전체"
if f2.button("🟢 정상만", use_container_width=True): st.session_state.filter_mode = "이상 없음"
if f3.button("🏠 대여중만", use_container_width=True): st.session_state.filter_mode = "대여 중"
if f4.button("🚨 점검필요", use_container_width=True): st.session_state.filter_mode = "점검필요"

# 데이터 필터링 로직
view_df = df.copy()
if st.session_state.filter_mode == "이상 없음":
    view_df = view_df[view_df['상태'] == "이상 없음"]
elif st.session_state.filter_mode == "대여 중":
    view_df = view_df[view_df['상태'] == "대여 중"]
elif st.session_state.filter_mode == "점검필요":
    view_df = view_df[view_df['상태'].isin(["파손/점검", "분실"])]

# 가독성을 위한 스타일 적용
def style_status(row):
    color = ''
    if row['상태'] == "이상 없음": color = 'background-color: #f0fff4; color: #22543d'
    elif row['상태'] == "대여 중": color = 'background-color: #ebf8ff; color: #2a4365'
    elif row['상태'] in ["파손/점검", "분실"]: color = 'background-color: #fff5f5; color: #742a2a; font-weight: bold'
    return [color] * len(row)

st.dataframe(
    view_df.style.apply(style_status, axis=1), 
    use_container_width=True, 
    hide_index=True,
    height=600
)
