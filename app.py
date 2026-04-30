import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- 1. 페이지 설정 및 초기화 ---
st.set_page_config(page_title="상북중 크롬북 통합 관리", layout="wide")

# 알림 기능을 위한 JavaScript (원본 유지)
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

# 보내주신 원본 학생 명단 데이터 (학번: [이름, CEU번호])
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

# 학급 리스트 자동 추출 (1-1, 1-2 형식으로 변환)
def get_class_name(student_id):
    grade = student_id[0]
    cls = int(student_id[1])
    return f"{grade}-{cls}"

CLASSES = sorted(list(set(get_class_name(sid) for sid in STUDENT_LIST.keys())))

def load_data():
    if os.path.exists(DB_FILE):
        try:
            return pd.read_csv(DB_FILE, dtype={'학번': str}) # 학번을 문자열로 읽어야 함
        except:
            pass
    
    # DB 파일이 없을 경우 초기 생성
    data = []
    for sid, info in STUDENT_LIST.items():
        data.append({
            "학번": sid,
            "이름": info[0],
            "기기번호": f"CEU{info[1]}",
            "학급": get_class_name(sid),
            "상태": "이상 없음",
            "특이사항": "-",
            "최종수정": datetime.now().strftime("%Y-%m-%d %H:%M")
        })
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
    st.header("🏫 학급 관리")
    active_cls = st.selectbox("관리할 학급 선택", CLASSES)
    
    st.markdown(f"**[{active_cls}]** 학급 전체 관리")
    if st.button(f"✨ {active_cls} 전원 '이상 없음'으로 초기화", use_container_width=True):
        st.session_state.df.loc[st.session_state.df['학급'] == active_cls, '상태'] = "이상 없음"
        st.session_state.df.loc[st.session_state.df['학급'] == active_cls, '최종수정'] = datetime.now().strftime("%Y-%m-%d %H:%M")
        save_to_file()
        st.success(f"{active_cls} 학급이 초기화되었습니다.")
        st.rerun()
    
    st.divider()
    
    st.header("🛠️ 개별 상태 수정")
    # 해당 학급 학생들만 필터링
    cls_students = st.session_state.df[st.session_state.df['학급'] == active_cls]
    # '학번 - 이름' 형식으로 리스트 생성
    student_options = cls_students.apply(lambda x: f"{x['학번']} - {x['이름']}", axis=1).tolist()
    
    if not student_options:
        st.warning("선택한 학급에 등록된 학생이 없습니다.")
    else:
        with st.form("edit_form"):
            selected_student = st.selectbox("대상 학생 선택", student_options)
            target_sid = selected_student.split(" - ")[0]
            
            current_row = st.session_state.df[st.session_state.df['학번'] == target_sid].iloc[0]
            st.caption(f"기기 번호: {current_row['기기번호']}")
            
            new_status = st.radio("상태 변경", ["이상 없음", "대여 중", "파손/점검", "분실"], 
                                 index=["이상 없음", "대여 중", "파손/점검", "분실"].index(current_row['상태']))
            new_note = st.text_input("특이사항", value=current_row['특이사항'])
            
            if st.form_submit_button("상태 저장"):
                idx = st.session_state.df[st.session_state.df['학번'] == target_sid].index[0]
                
                st.session_state.df.at[idx, '상태'] = new_status
                st.session_state.df.at[idx, '특이사항'] = new_note if new_note else "-"
                st.session_state.df.at[idx, '최종수정'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                save_to_file()
                
                if new_status in ["파손/점검", "분실"]:
                    st.components.v1.html(f"""
                        <script>
                        window.parent.sendNotification("🚨 크롬북 이상 발견", "{active_cls} {current_row['이름']}({current_row['기기번호']}): {new_status}");
                        </script>
                    """, height=0)
                
                st.success(f"{current_row['이름']} 학생 기기 수정 완료")
                st.rerun()

# --- 3. 메인 화면 ---
st.title("💻 크롬북 통합 현황판 (상북중)")

df = st.session_state.df
col1, col2, col3, col4 = st.columns(4)
col1.metric("전체 기기", f"{len(df)}대")
col2.metric("🟢 정상", f"{len(df[df['상태']=='이상 없음'])}대")
col3.metric("🏠 대여중", f"{len(df[df['상태']=='대여 중'])}대")
col4.metric("🚨 점검/분실", f"{len(df[df['상태'].isin(['파손/점검', '분실'])])}대")

st.divider()

f1, f2, f3, f4 = st.columns(4)
if f1.button("전체 보기", use_container_width=True): st.session_state.filter_mode = "전체"
if f2.button("🟢 정상만", use_container_width=True): st.session_state.filter_mode = "이상 없음"
if f3.button("🏠 대여중만", use_container_width=True): st.session_state.filter_mode = "대여 중"
if f4.button("🚨 점검필요", use_container_width=True): st.session_state.filter_mode = "점검필요"

view_df = df.copy()
if st.session_state.filter_mode == "이상 없음":
    view_df = view_df[view_df['상태'] == "이상 없음"]
elif st.session_state.filter_mode == "대여 중":
    view_df = view_df[view_df['상태'] == "대여 중"]
elif st.session_state.filter_mode == "점검필요":
    view_df = view_df[view_df['상태'].isin(["파손/점검", "분실"])]

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
