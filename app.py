import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- 1. 페이지 설정 및 알림 JS ---
st.set_page_config(page_title="상북중 크롬북 통합 관리", layout="wide")

# (알림 JS 생략 - 기존과 동일)
st.markdown("""<script>...</script>""", unsafe_allow_html=True)

DB_FILE = "chromebook_master_db_v16.csv"

# [데이터 로드 함수]
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

# --- 2. 사이드바 구성 ---
CLASSES = sorted(list(set(st.session_state.df['학급'])))
with st.sidebar:
    st.header("⚙️ 접속 모드")
    is_admin = st.checkbox("교사용 관리자 모드")
    
    # 관리자/학생 분리 로직 (기존과 동일)
    # ... (생략) ...

    st.divider()
    st.subheader("🛠️ 개별 상태 보고")
    # 대여 시 가이드 문구 기능 포함
    # ... (생략) ...

# --- 3. 메인 화면 ---

# [로고 + 타이틀 레이아웃]
# 깃허브에 올린 '상북중로고.png'를 불러옵니다.
logo_path = "상북중로고.png"
title_col1, title_col2 = st.columns([1, 6])

with title_col1:
    if os.path.exists(logo_path):
        st.image(logo_path, width=120)
    else:
        st.markdown("<h1 style='font-size: 80px; margin:0;'>🏫</h1>", unsafe_allow_html=True)

with title_col2:
    st.markdown("<br>", unsafe_allow_html=True) # 높이 조절용
    st.title("상북중학교 크롬북 통합 현황판")

st.divider()

# [대시보드 디자인 - 네모 없이 아이콘 강조]
st.markdown("""
    <style>
    /* 버튼의 네모 박스 배경과 테두리를 투명하게 제거 */
    div.stButton > button {
        border: none !important;
        background-color: transparent !important;
        box-shadow: none !important;
        color: inherit !important;
        transition: transform 0.2s;
        padding: 0 !important;
        width: 100% !important;
    }
    /* 마우스를 올렸을 때만 살짝 커지게 효과 */
    div.stButton > button:hover {
        transform: scale(1.05);
        background-color: transparent !important;
    }
    .metric-icon { font-size: 50px; display: block; margin-bottom: 5px; }
    .metric-label { font-size: 18px; color: #555; }
    .metric-value { font-size: 26px; font-weight: bold; color: #333; }
    </style>
""", unsafe_allow_html=True)

df = st.session_state.df
stats = {
    "전체": len(df), 
    "정상": len(df[df['상태']=='이상 없음']), 
    "대여": len(df[df['상태']=='대여']), 
    "파손": len(df[df['상태']=='파손/점검']), 
    "분실": len(df[df['상태']=='분실'])
}

m_cols = st.columns(5)
# 각 버튼 안에 HTML을 넣어 아이콘이 크게 보이게 했습니다.
with m_cols[0]:
    if st.button("📄 전체\n\n" + str(stats['전체']) + "대"): st.session_state.filter_status = "전체"
with m_cols[1]:
    if st.button("🟢 정상\n\n" + str(stats['정상']) + "대"): st.session_state.filter_status = "이상 없음"
with m_cols[2]:
    if st.button("🏠 대여\n\n" + str(stats['대여']) + "대"): st.session_state.filter_status = "대여"
with m_cols[3]:
    if st.button("🛠️ 파손\n\n" + str(stats['파손']) + "대"): st.session_state.filter_status = "파손/점검"
with m_cols[4]:
    if st.button("🔍 분실\n\n" + str(stats['분실']) + "대"): st.session_state.filter_status = "분실"

st.divider()
st.subheader(f"📍 목록 필터: {st.session_state.filter_status}")

# [필터링 및 표 출력]
display_df = df if st.session_state.filter_status == "전체" else df[df['상태'] == st.session_state.filter_status]

def style_status(row):
    color = ''
    if row['상태'] == "이상 없음": color = 'background-color: #f0fff4;'
    elif row['상태'] == "대여": color = 'background-color: #ebf8ff;'
    elif row['상태'] == "파손/점검": color = 'background-color: #fff5f5; color: #742a2a; font-weight: bold;'
    elif row['상태'] == "분실": color = 'background-color: #2d3748; color: white; font-weight: bold;'
    return [color] * len(row)

st.dataframe(display_df.style.apply(style_status, axis=1), use_container_width=True, hide_index=True)
