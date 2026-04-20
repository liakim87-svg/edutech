import streamlit as st
import pandas as pd
from datetime import datetime
import os
import streamlit.components.v1 as components

# 1. 화면 구성 설정
st.set_page_config(page_title="에듀테크 도우미", layout="wide", page_icon="🔔")

# 데이터 저장용 파일 이름
DB_FILE = "logs.csv"

# --- 브라우저 알림 자바스크립트 함수 ---
def send_notification(title, message):
    # 브라우저 알림을 띄우는 JS 코드
    js_code = f"""
    <script>
    function showNotification() {{
        if (!("Notification" in window)) {{
            console.log("이 브라우저는 알림을 지원하지 않습니다.");
        }} else if (Notification.permission === "granted") {{
            new Notification("{title}", {{ body: "{message}", icon: "https://cdn-icons-png.flaticon.com/512/564/564619.png" }});
        }} else if (Notification.permission !== "denied") {{
            Notification.requestPermission().then(permission => {{
                if (permission === "granted") {{
                    new Notification("{title}", {{ body: "{message}" }});
                }}
            }});
        }}
    }}
    showNotification();
    </script>
    """
    components.html(js_code, height=0)

# 데이터 로드/저장 함수
def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["날짜", "학반", "유형", "기기번호", "작성자", "내용"])

def save_data(df):
    df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')

# --- UI 시작 ---
st.title("🚀 에듀테크 스마트 도우미")

# 사이드바 메뉴
menu = st.sidebar.selectbox("메뉴 선택", ["🏠 메인 화면", "🚨 고장 신고", "📊 누적 기록"])

# 알림 권한 요청 버튼 (처음 한 번은 눌러줘야 함)
if st.sidebar.button("🔔 알림 권한 허용하기"):
    components.html("""
    <script>
        Notification.requestPermission().then(p => {
            if(p==='granted') alert('알림 권한이 허용되었습니다!');
        });
    </script>
    """, height=0)

df = load_data()

if menu == "🏠 메인 화면":
    st.subheader("📅 오늘 학반별 점검 현황")
    classes = ["1-1", "1-2", "2-1", "2-2", "3-1", "3-2"]
    cols = st.columns(len(classes))
    
    # 오늘 날짜 데이터만 필터링
    today = datetime.now().strftime("%Y-%m-%d")
    today_checks = df[(df['날짜'].str.contains(today)) & (df['유형'] == "정기점검")]

    for i, cls in enumerate(classes):
        with cols[i]:
            is_done = cls in today_checks['학반'].values
            if is_done:
                st.success(f"**{cls}**\n\n완료")
            else:
                st.warning(f"**{cls}**\n\n미완료")
                if st.button(f"확인", key=f"chk_{cls}"):
                    name = st.text_input("성함", key=f"nm_{cls}")
                    if name:
                        new_row = {"날짜": datetime.now().strftime("%Y-%m-%d %H:%M"), "학반": cls, "유형": "정기점검", "기기번호": "-", "작성자": name, "내용": "이상 없음"}
                        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                        save_data(df)
                        send_notification("✅ 점검 완료", f"{cls}반 점검이 완료되었습니다.")
                        st.rerun()

elif menu == "🚨 고장 신고":
    st.subheader("🚨 기기 고장 리포트")
    with st.form("report_form"):
        f_class = st.selectbox("학반", ["1-1", "1-2", "2-1", "2-2", "3-1", "3-2"])
        f_num = st.number_input("기기 번호", min_value=1, max_value=40)
        f_user = st.text_input("신고자 성함")
        f_desc = st.text_area("증상 설명")
        
        if st.form_submit_button("신고하기"):
            if f_user and f_desc:
                new_row = {"날짜": datetime.now().strftime("%Y-%m-%d %H:%M"), "학반": f_class, "유형": "고장신고", "기기번호": f_num, "작성자": f_user, "내용": f_desc}
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                save_data(df)
                
                # 📢 신고 완료 시 브라우저 알림 전송!
                send_notification("🚨 고장 신고 접수!", f"[{f_class}] {f_num}번 기기: {f_desc}")
                
                st.success("고장 리포트가 전송되었습니다.")
            else:
                st.error("이름과 내용을 입력해주세요.")

elif menu == "📊 누적 기록":
    st.subheader("📊 전체 관리 기록")
    st.dataframe(df.sort_values("날짜", ascending=False), use_container_width=True)
```

---

### 2. 사용 전 주의사항 (필독!)

1.  **알림 권한 허용**: 앱을 처음 실행하면 사이드바에 있는 **[🔔 알림 권한 허용하기]** 버튼을 꼭 눌러주세요. 브라우저에서 알림 허용 여부를 물으면 '허용'을 클릭해야 합니다.
2.  **창을 열어두어야 함**: 브라우저 알림은 **해당 웹사이트가 크롬 탭에 열려 있을 때만** 작동합니다. (창을 닫으면 알림이 오지 않아요.)
3.  **방해 금지 모드**: 윈도우나 맥의 '방해 금지 모드' 또는 '집중 모드'가 켜져 있으면 알림 소리나 팝업이 뜨지 않을 수 있습니다.



### 3. `requirements.txt` 확인
이 코드를 쓰려면 `requirements.txt`에 한 줄이 더 추가되어야 합니다. (아래 내용으로 바꾸세요)
```text
streamlit
pandas
