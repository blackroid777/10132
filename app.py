import streamlit as st
import google.generativeai as genai

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="풋볼 AI 버디", page_icon="⚽")
st.title("⚽ 풋볼 AI 버디")
st.caption("축구에 대한 모든 것! 전술, 선수, 역사 등 무엇이든 물어보세요.")

# 2. Streamlit Secrets에서 API 키 불러오기 및 설정
try:
    gemini_api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=gemini_api_key)
except KeyError:
    st.error("⚠️ Streamlit Secrets에 'GEMINI_API_KEY'가 설정되지 않았습니다. 설정을 확인해주세요.")
    st.stop()

# 3. 세션 상태(Session State)로 채팅 기록 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []
    # 챗봇에게 축구 전문가라는 페르소나 부여를 위한 시스템 지침 설정
    st.session_state.system_instruction = (
        "당신은 열정적이고 지식이 풍부한 축구 전문가입니다. "
        "축구 관련 질문에만 친절하고 상세하게 답해주세요. "
        "만약 축구와 전혀 상관없는 질문이 들어오면, 축구와 관련된 이야기로 자연스럽게 유도하거나 "
        "축구 관련 질문만 답변할 수 있다고 정중하게 안내하세요."
    )

# 4. 기존 채팅 기록 화면에 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. 사용자 입력 받기
if user_input := st.chat_input("메시지를 입력하세요 (예: 오프사이드 규칙이 뭐야?, 벵거 볼의 특징은?)"):
    
    # 사용자 메시지 화면 표시 및 저장
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # AI 답변 생성 및 화면 표시
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            # gemini-2.5-flash-lite 모델 설정
            model = genai.GenerativeModel(
                model_name="gemini-2.5-flash-lite",
                system_instruction=st.session_state.system_instruction
            )
            
            # 이전 대화 기록을 Gemini API 형식에 맞게 변환 (role 변환 포함)
            history = []
            for msg in st.session_state.messages[:-1]:  # 현재 입력 직전까지의 기록
                role = "user" if msg["role"] == "user" else "model"
                history.append({"role": role, "parts": [msg["content"]]})
            
            # 채팅 세션 시작 및 답변 요청
            chat = model.start_chat(history=history)
            response = chat.send_message(user_input)
            
            # 답변 출력 및 세션 저장
            ai_response = response.text
            message_placeholder.markdown(ai_response)
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            
        except genai.types.generation_types.APIError as e:
            st.error(f"❌ Google Gemini API 오류가 발생했습니다: {e}")
        except Exception as e:
            st.error(f"❌ 예상치 못한 오류가 발생했습니다: {e}")
