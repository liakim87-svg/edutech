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

# --- 2. 사이드바 ---
with st.sidebar:
    st.header("🏢 학급 선택")
    # 관리할 학급을 먼저 선택하게 하여 실수를 방지합니다.
    active_cls = st.selectbox("관리할 학급을 선택하세요", CLASSES)
    
    st.divider()
    
    st.header("🛠️ 상태 업데이트")
    # 선택된 학급의 기기만 리스트에 노출
    cls_devices = st.session_state.df[st.session_state.df['학급'] == active_cls]
    device_list = cls_devices['기기번호'].tolist()
    
    with st.form("edit_form"):
        target_id = st.selectbox("기기 번호", device_list)
        
        # 선택된 기기의 현재 정보 표시 (사용자 확인용)
        current_info = cls_devices[cls_devices['기기번호'] == target_id].iloc[0]
        st.info(f"선택 정보: {current_info['학급']} 학급 {current_info['번호']}번 학생")
        
        new_status = st.radio("변경 상태", ["이상 없음", "대여 중", "파손/점검", "분실"], index=0)
        new_note = st.text_input("특이사항", value=current_info['특이사항'])
        
        if st.form_submit_button("저장하기"):
            # 데이터프레임에서 정확한 인덱스 찾기 (기기번호 기준)
            idx = st.session_state.df[st.session_state.df['기기번호'] == target_id].index[0]
            
            st.session_state.df.at[idx, '상태'] = new_status
            st.session_state.df.at[idx, '특이사항'] = new_note if new_note else "-"
            st.session_state.df.at[idx, '최종수정'] = datetime.now().strftime("%Y-%m-%d %H:%M")
            save_to_file()
            
            # 알림 발생 로직
            if new_status in ["파손/점검", "분실"]:
                st.components.v1.html(f"""
                    <script>
                    window.parent.sendNotification("🚨 크롬북 이상 알림", "{active_cls} {current_info['번호']}번({target_id}) 기기: {new_status}");
                    </script>
                """, height=0)
            
            st.success(f"업데이트 완료: {target_id}")
            st.rerun()

    if st.button(f"✨ {active_cls} 전원 '이상없음' 처리"):
        st.session_state.df.loc[st.session_state.df['학급'] == active_cls, '상태'] = "이상 없음"
        st.session_state.df.loc[st.session_state.df['학급'] == active_cls, '최종수정'] = datetime.now().strftime("%Y-%m-%d %H:%M")
        save_to_file()
        st.rerun()

# --- 3. 메인 화면 ---
st.title("💻 크롬북 통합 관리")

# 요약 통계
df = st.session_state.df
col1, col2, col3, col4 = st.columns(4)
col1.metric("전체", f"{len(df)}대")
col2.metric("이상 없음", f"{len(df[df['상태']=='이상 없음'])}대")
col3.metric("🏠 대여 중", f"{len(df[df['상태']=='대여 중'])}대")
col4.metric("🚨 점검 필요", f"{len(df[df['상태'].isin(['파손/점검', '분실'])])}대")

# 필터 버튼
f_c1, f_c2, f_c3, f_c4 = st.columns(4)
if f_c1.button("모두 보기"): st.session_state.filter_mode = "전체"
if f_c2.button("이상 없음만"): st.session_state.filter_mode = "이상 없음"
if f_c3.button("🏠 대여 중만"): st.session_state.filter_mode = "대여 중"
if f_c4.button("🚨 점검 필요만"): st.session_state.filter_mode = "점검필요"

# 데이터 필터링 적용
view_df = df.copy()
if st.session_state.filter_mode == "이상 없음":
    view_df = view_df[view_df['상태'] == "이상 없음"]
elif st.session_state.filter_mode == "대여 중":
    view_df = view_df[view_df['상태'] == "대여 중"]
elif st.session_state.filter_mode == "점검필요":
    view_df = view_df[view_df['상태'].isin(["파손/점검", "분실"])]

# 표 출력
def style_row(row):
    color = ''
    if row['상태'] == "이상 없음": color = 'background-color: #f0fff4'
    elif row['상태'] == "대여 중": color = 'background-color: #ebf8ff'
    elif row['상태'] in ["파손/점검", "분실"]: color = 'background-color: #fff5f5'
    return [color] * len(row)

st.dataframe(view_df.style.apply(style_row, axis=1), use_container_width=True, hide_index=True)
