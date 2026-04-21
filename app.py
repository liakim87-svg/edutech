import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- 1. 설정 및 데이터 로드 ---
st.set_page_config(page_title="크롬북 관리 시스템", layout="wide")

DB_FILE = "chromebook_logs.csv"

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    # 초기 데이터가 없을 경우 생성
    data = []
    for c in range(1, 4):  # 1~3반
        for s in range(1, 21):  # 1~20번
            student_id = f"{c}{s:02d}"
            data.append({
                "학번": student_id,
                "이름": f"학생{student_id}",
                "반": f"{c}반",
                "상태": "정상 반납",
                "특이사항": "-",
                "업데이트": datetime.now().strftime("%Y-%m-%d %H:%M")
            })
    return pd.DataFrame(data)

if 'df' not in st.session_state:
    st.session_state.df = load_data()

df = st.session_state.df

# --- 2. 사이드바: 도우미 입력 메뉴 ---
st.sidebar.header("🛠️ 도우미 입력 메뉴")

with st.sidebar.form("input_form"):
    sel_class = st.selectbox("우리 반 선택", ["1반", "2반", "3반"])
    
    # 선택한 반 학생만 필터링
    class_df = df[df['반'] == sel_class]
    sel_student = st.selectbox("학생 선택", class_df['학번'].tolist())
    
    new_status = st.radio("기기 상태", ["정상 반납", "대여 중", "분실", "파손"])
    new_detail = st.text_input("특이 사항 (파손 부위 등)")
    
    submit = st.form_submit_button("상태 업데이트")
    
    if submit:
        idx = df[df['학번'] == sel_student].index[0]
        df.at[idx, '상태'] = new_status
        df.at[idx, '특이사항'] = new_detail if new_detail else "-"
        df.at[idx, '업데이트'] = datetime.now().strftime("%H:%M")
        df.to_csv(DB_FILE, index=False)
        st.session_state.df = df
        st.sidebar.success("✅ 업데이트 완료!")
        st.rerun()

# --- 3. 메인 화면: 시각화 및 현황 ---
st.title("📊 크롬북 통합 관리 현황판")

# 상단 알림 (분실/파손 발생 시)
critical = df[df['상태'].isin(["분실", "파손"])]
if not critical.empty:
    st.error(f"🚨 점검 필요 항목이 {len(critical)}건 있습니다!")

# 통계 지표
m1, m2, m3, m4 = st.columns(4)
m1.metric("전체 기기", len(df))
m2.metric("정상 반납", len(df[df['상태'] == "정상 반납"]))
m3.metric("대여 중", len(df[df['상태'] == "대여 중"]))
m4.metric("점검 필요", len(critical))

st.divider()

# 간단한 시각화 (반별 반납률)
st.subheader("🏫 반별 반납 진행률")
return_rates = []
classes = ["1반", "2반", "3반"]
for c in classes:
    total = len(df[df['반'] == c])
    done = len(df[(df['반'] == c) & (df['상태'] == "정상 반납")])
    rate = (done / total) * 100
    return_rates.append(rate)

chart_data = pd.DataFrame({"반": classes, "반납률(%)": return_rates})
st.bar_chart(data=chart_data, x="반", y="반납률(%)")

# 상세 리스트
st.divider()
st.subheader("📑 실시간 전체 명단")
search = st.text_input("🔍 학번 또는 이름 검색")
if search:
    display_df = df[df['학번'].str.contains(search) | df['이름'].str.contains(search)]
else:
    display_df = df

# 상태에 따라 색상 입히기
def color_status(val):
    if val == "분실": return "background-color: #ffcccc"
    if val == "파손": return "background-color: #ffe5cc"
    if val == "대여 중": return "color: #3498db"
    return ""

st.dataframe(
    display_df.style.applymap(color_status, subset=['상태']),
    use_container_width=True,
    hide_index=True
)
