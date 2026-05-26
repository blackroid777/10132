import streamlit as dict_import  # 내부 오류 방지용 기본 라이브러리
import streamlit as st
import pandas as pd
import datetime

# --- 페이지 설정 ---
st.set_page_config(page_title="수행평가 일정 관리 플래너", page_icon="📅", layout="wide")

# --- 세션 상태(데이터 저장소) 초기화 ---
# 앱이 재실행되어도 데이터가 날아가지 않도록 유지합니다.
if "events" not in st.session_state:
    st.session_state.events = pd.DataFrame(
        columns=["과목", "수행평가 내용", "마감일", "D-Day"]
    )

st.title("📅 과목별 수행평가 일정 플래너")
st.markdown("수행평가 일정을 기록하고, 달력과 리스트로 한눈에 확인하세요!")

# --- 레이아웃 분할 (좌측: 입력 창 / 우측: 달력 및 리스트) ---
col1, col2 = st.columns([1, 2])

# --- [좌측] 수행평가 일정 입력 섹션 ---
with col1:
    st.header("📝 새 일정 등록")
    
    with st.form(key="event_form", clear_on_submit=True):
        subject = st.selectbox(
            "과목 선택",
            ["국어", "수학", "영어", "한국사", "과학탐구", "사회탐구", "제2외국어", "기타"]
        )
        content = st.text_input("수행평가 내용", placeholder="예: 과학 실험 보고서 제출")
        due_date = st.date_input("마감일 선택", datetime.date.today())
        
        submit_button = st.form_submit_button(label="일정 추가하기")
        
        if submit_button:
            if content.strip() == "":
                st.error("수행평가 내용을 입력해주세요!")
            else:
                # 새로운 일정 데이터 생성
                new_event = pd.DataFrame([{
                    "과목": subject,
                    "수행평가 내용": content,
                    "마감일": due_date,
                    "D-Day": "" # 하단에서 계산
                }])
                
                # 기존 데이터에 추가
                st.session_state.events = pd.concat([st.session_state.events, new_event], ignore_index=True)
                st.success(f"'{subject}' 수행평가 일정이 추가되었습니다!")

# --- 데이터 가공 (D-Day 계산 및 정렬) ---
df = st.session_state.events.copy()
if not df.empty:
    # 날짜 형식 정렬을 위해 datetime 타입으로 변환
    df["마감일"] = pd.to_datetime(df["마감일"]).dt.date
    today = datetime.date.today()
    
    # D-Day 계산 라이직
    def calculate_dday(date):
        delta = (date - today).days
        if delta == 0:
            return "🔥 D-Day"
        elif delta < 0:
            return f"✅ 완료 ({abs(delta)}일 지남)"
        else:
            return f"⏳ D-{delta}"
            
    df["D-Day"] = df["마감일"].apply(calculate_dday)
    df = df.sort_values(by="마감일") # 날짜순 정렬

# --- [우측] 달력 및 일정 확인 섹션 ---
with col2:
    st.header("🗓️ 이번 달 일정 보기")
    
    # 1. 스트림릿 기본 달력 뷰 (st.date_input 활용)
    # 현재 등록된 마감일들을 달력에 점이나 하이라이트로 보여주는 대안으로, 
    # 날짜를 선택하면 해당 날짜의 일정을 필터링해 보여주는 스마트 달력 기능을 구현했습니다.
    
    selected_date = st.date_input("🗓️ 날짜를 선택하면 해당 날짜의 수행평가를 보여줍니다.", datetime.date.today())
    
    # 2. 전체 일정 표 및 필터링
    st.header("📋 전체 수행평가 리스트")
    
    if df.empty:
        st.info("등록된 수행평가 일정이 없습니다. 좌측에서 첫 일정을 등록해보세요!")
    else:
        # 선택한 날짜 필터링 보여주기
        filtered_df = df[df["마감일"] == selected_date]
        if not filtered_df.empty:
            st.markdown(f"#### 🔍 {selected_date} 선택된 날짜의 일정")
            st.dataframe(filtered_df, use_container_width=True)
            st.markdown("---")
            
        # 전체 테이블 출력
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # 일정 삭제 기능
        st.markdown("### 🗑️ 일정 삭제")
        delete_target = st.selectbox("삭제할 일정을 선택하세요", df["수행평가 내용"].unique())
        if st.button("선택한 일정 삭제"):
            st.session_state.events = st.session_state.events[st.session_state.events["수행평가 내용"] != delete_target]
            st.rerun()
