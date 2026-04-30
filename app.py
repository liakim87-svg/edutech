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
            new Notification(title, { 
                body: body, 
                icon: 'https://cdn-icons-png.flaticon.com/512/564/564344.png' 
            });
        }
    }
    </script>
""", unsafe_allow_html=True)

# 충돌 방지를 위해 v12로 파일명 변경
DB_FILE = "chromebook_master_db_v12.csv"

# [데이터] 상북중 학생 명단
STUDENT_LIST = {
    "1101": ["김동율", "020"], "1102": ["김민석", "031"], "1103": ["김어진", "016"], "1104": ["김타냐", "008"], "1105": ["노아", "102"],
    "1106": ["박하민", "011"], "1107": ["손연아", "128"], "1108": ["양승호", "014"], "1109": ["원상현", "022"], "1110": ["윤소연", "033"],
    "1111": ["이성제", "007"], "1112": ["이정후", "026"], "1113": ["이하경", "124"], "1114": ["임태산", "030"], "1115": ["정채준", "034"],
    "1116": ["주선우", "027"], "1117": ["최예빈", "017"], "1118": ["최재혁", "010"], "1119": ["허민서", "021"],
    "1201": ["김가람", "018"], "1202": ["김들", "114"], "1203": ["김서후", "009"], "1204": ["김재빈", "029"], "1205": ["박마루", "112"],
    "1206": ["박지은", "025"], "1207": ["배서윤", "013"], "1208": ["원세준", "003"], "1209": ["윤하정", "117"], "1210": ["이예원", "037"],
    "1211": ["이준환", "036"], "1212": ["임시우", "052"], "1213": ["장주혁", "048"], "1214": ["정유진", "028"], "1215": ["정현석", "103"],
    "1216": ["최아영", "032"], "1217": ["최은지", "070"], "1218": ["허동혁", "066"], "1219": ["황승미", "073"],
    "2101": ["ANSHENGBIN", "062"], "2102": ["곽고은", "045"], "2103": ["김가림", "126"], "2104": ["김리안", "047"], "2105": ["김무성", "012"],
    "2106": ["김미설", "038"], "2107": ["김소현", "023"], "2108": ["김태은", "087"], "2109": ["박예은", "051"], "2110": ["신민준", "078"],
    "2111": ["양지연", "035"], "2112": ["오동건", "063"], "2113": ["윤채환", "080"], "2114": ["윤현정", "076"], "2115": ["이나원", "060"],
    "2116": ["이대현", "001"], "2117": ["이아영", "042"], "2118": ["이정희", "054"], "2119": ["정가인", "122"], "2120": ["정민기", "069"],
    "2121": ["진정한", "065"], "2122": ["허동진", "055"],
    "2201": ["강주원", "050"], "2202": ["고대균", "071"], "2203": ["곽유찬", "043"], "2204": ["김건희", "058"], "2205": ["김경은", "130"],
    "2206": ["김대우", "074"], "2207": ["김도형", "075"], "2208": ["김라온", "039"], "2209": ["김민성", "053"], "2210": ["김민현", "127"],
    "2211": ["김시현", "059"], "2212": ["김지후", "040"], "2213": ["박소영", "072"], "2214": ["박태양", "068"], "2215": ["백재욱", "077"],
    "2216": ["손예림", "061"], "2217": ["송다임", "079"], "2218": ["이지향", "064"], "2219": ["이혜진", "067"], "2220": ["이효아", "096"],
    "2221": ["정다윤", "049"], "2222": ["정승현", "132"], "2223": ["정하린", "057"],
    "3101": ["강보민", "101"], "3102": ["김가온", "088"], "3103": ["김미래", "105"], "3104": ["김민건", "104"], "3105": ["김민준", "002"],
    "3106": ["김연호", "139"], "3107": ["김은화", "092"], "3108": ["남혁주", "081"], "3109": ["문시윤", "118"], "3110": ["박민체", "085"],
    "3111": ["원영준", "111"], "3112": ["원태경", "110"], "3113": ["유도겸", "084"], "3114": ["이지우", "097"], "3115": ["이지윤", "120"],
    "3116": ["전서원", "083"], "3117": ["정수연", "116"], "3118": ["정아단", "004"], "3119": ["진유빈", "137"],
    "3201": ["KOONKOKKRUAD THANAWUT", "005"], "3202": ["공지연", "089"], "3203": ["김나로", "090"], "3204": ["김연서", "091"], "3205": ["김지호", "106"],
    "3206": ["김채은", "107"], "3207": ["남세빈", "113"], "3208": ["문채혁", "086"], "3209": ["박수경", "093"], "3210": ["서다울", "108"],
    "3211": ["서지원", "109"], "3212": ["송요찬", "094"], "3213": ["신하원", "134"], "3214": ["이규민", "095"], "3215": ["이은수", "136"],
    "3216": ["이해린", "115"], "3217": ["정혜빈", "082"], "3218": ["주승현", "100"], "3219": ["진채원", "099"], "3220": ["이온리", "121"]
}

def load_data():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE, dtype={'학번': str})
            # '학급' 열이 있는지 확인하고 없으면 새로 생성 (안전장치)
            if '학급' not in df.columns:
                df['학급'] = df['학번'].apply(lambda x: f"{x[0]}-{int(x[1])}")
            df['특이사항'] = df['특이사항'].fillna("")
            return df
        except:
            pass
    # 데이터가 없거나 열이 꼬였을 때 새로 생성
    init_data = []
    for sid, info in STUDENT_LIST.items():
        init_data.append({
            "학번": sid, "이름": info[0], "기기번호": f"CEU{info[1]}",
            "학급": f"{sid[0]}-{int(sid[1])}", "상태": "이상 없음", "특이사항": "",
            "최종수정": datetime.now().strftime("%Y-%m-%d %H:%M")
        })
    df = pd.DataFrame(init_data)
    df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
    return df

# 데이터 로드
if 'df' not in st.session_state:
    st.session_state.df = load_data()

def save_to_file():
    st.session_state.df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')

# --- 2. 사이드바 구성 ---
CLASSES = sorted(list(set(st.session_state.df['학급'])))

with st.sidebar:
    st.header("⚙️ 접속 모드")
    is_admin = st.checkbox("교사용 관리자 모드")
    
    if is_admin:
        st.divider()
        st.subheader("🔔 교사용 알림")
        if st.button("알림 활성화", use_container_width=True):
            st.components.v1.html("<script>window.parent.requestPermission();</script>", height=0)
        
        st.divider()
        st.subheader("🚨 데이터 리셋")
        confirm_reset = st.checkbox("전체 초기화 승인")
        if st.button("🔥 전교생 데이터 초기화", use_container_width=True, disabled=not confirm_reset):
            st.session_state.df['상태'] = "이상 없음"
            st.session_state.df['특이사항'] = ""
            st.session_state.df['최종수정'] = datetime.now().strftime("%Y-%m-%d %H:%M")
            save_to_file()
            st.rerun()
    else:
        st.divider()
        st.info("학생용: 우리 반 기기 확인")
        active_cls = st.selectbox("우리 반 선택", CLASSES)
        
        if st.button(f"✨ {active_cls} 전원 이상 없음 확인", use_container_width=True):
            st.session_state.df.loc[st.session_state.df['학급'] == active_cls, '상태'] = "이상 없음"
            st.session_state.df.loc[st.session_state.df['학급'] == active_cls, '특이사항'] = ""
            st.session_state.df.loc[st.session_state.df['학급'] == active_cls, '최종수정'] = datetime.now().strftime("%Y-%m-%d %H:%M")
            save_to_file()
            st.success("확인 완료!")
            st.rerun()

    st.divider()
    st.subheader("🛠️ 개별 상태 보고")
    if is_admin:
        active_cls = st.selectbox("조회할 학급 선택", CLASSES, key="admin_cls_sel")

    cls_df = st.session_state.df[st.session_state.df['학급'] == active_cls]
    student_options = cls_df.apply(lambda x: f"{x['학번']} - {x['이름']}", axis=1).tolist()
    
    STATUS_LIST = ["이상 없음", "대여", "파손/점검", "분실"]
    selected_student = st.selectbox("학생 선택", student_options)
    target_sid = selected_student.split(" - ")[0]
    row = st.session_state.df[st.session_state.df['학번'] == target_sid].iloc[0]
    
    with st.form("edit_form"):
        # 라디오 버튼
        new_status = st.radio("기기 상태", STATUS_LIST, 
                             index=STATUS_LIST.index(row['상태']) if row['상태'] in STATUS_LIST else 0)
        
        # [핵심] Placeholder 설정 (클릭 시 사라지는 안내 문구)
        ph_text = "반납예정일자를 쓰시오" if new_status == "대여" else ""
        new_note = st.text_input("특이사항/메모", value=row['특이사항'], placeholder=ph_text)
        
        if st.form_submit_button("저장하기"):
            idx = st.session_state.df[st.session_state.df['학번'] == target_sid].index[0]
            st.session_state.df.at[idx, '상태'] = new_status
            st.session_state.df.at[idx, '특이사항'] = new_note
            st.session_state.df.at[idx, '최종수정'] = datetime.now().strftime("%Y-%m-%d %H:%M")
            save_to_file()
            
            if new_status in ["파손/점검", "분실"]:
                st.components.v1.html(f"""
                    <script>
                    window.parent.sendNotification("🚨 크롬북 이상 보고됨", "{active_cls} {row['이름']}: {new_status}");
                    </script>
                """, height=0)
            st.success(f"{row['이름']} 보고 완료!")
            st.rerun()

# --- 3. 메인 화면 ---
st.title("🛡️ 상북중 크롬북 통합 현황판")

# 대시보드 표시
df = st.session_state.df
if is_admin:
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("전체", f"{len(df)}대")
    m2.metric("🟢 정상", f"{len(df[df['상태']=='이상 없음'])}대")
    m3.metric("🏠 대여", f"{len(df[df['상태']=='대여'])}대")
    m4.metric("🛠️ 파손", f"{len(df[df['상태']=='파손/점검'])}대")
    m5.metric("🔍 분실", f"{len(df[df['상태']=='분실'])}대")
else:
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("🟢 정상 기기", f"{len(df[df['상태']=='이상 없음'])}대")
    m2.metric("🏠 현재 대여중", f"{len(df[df['상태']=='대여'])}대")
    m3.metric("🛠️ 수리 중", f"{len(df[df['상태']=='파손/점검'])}대")
    m4.metric("🔍 분실됨", f"{len(df[df['상태']=='분실'])}대")
st.divider()

# 표 스타일
def style_status(row):
    color = ''
    if row['상태'] == "이상 없음": color = 'background-color: #f0fff4;'
    elif row['상태'] == "대여": color = 'background-color: #ebf8ff;'
    elif row['상태'] == "파손/점검": color = 'background-color: #fff5f5; color: #742a2a; font-weight: bold;'
    elif row['상태'] == "분실": color = 'background-color: #2d3748; color: white; font-weight: bold;'
    return [color] * len(row)

st.dataframe(st.session_state.df.style.apply(style_status, axis=1), use_container_width=True, hide_index=True)
