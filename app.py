import streamlit as st
import google.generativeai as genai

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="🎮 GameBot: AI 게임 가이드", page_icon="🎮")
st.title("🎮 GameBot: 무엇이든 물어보세요!")
st.caption("게임 추천, 공략, 스토리 등 게임에 대한 모든 것을 알려드립니다.")

# 2. Streamlit Secrets에서 API 키 불러오기 및 설정
try:
    # Streamlit Cloud 배포 환경 또는 로컬 .streamlit/secrets.toml 환경
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except KeyError:
    st.error("❌ API 키를 찾을 수 없습니다. Streamlit Secrets에 'GEMINI_API_KEY'를 설정해주세요.")
    st.stop()

# 3. 세션 상태(Session State)로 채팅 기록 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant", 
            "content": "안녕하세요! 당신의 AI 게임 가이드입니다. 어떤 게임이 궁금하신가요? (예: '요즘 할 만한 RPG 추천해줘', '리그 오브 레전드 초보자 팁 있어?')"
        }
    ]

# 4. 기존 채팅 기록 화면에 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. 사용자 입력 처리
if user_input := st.chat_input("메시지를 입력하세요..."):
    # 사용자가 입력한 메시지 화면에 표시 및 저장
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # AI 응답 생성 중임을 표시하는 애니메이션
    with st.chat_message("assistant"):
        with st.spinner("생각 중..."):
            try:
                # 모델 설정 (gemini-2.5-flash-lite)
                # 💡 다른 주제로 바꾸고 싶다면 아래 system_instruction 내용을 수정하세요!
                model = genai.GenerativeModel(
                    model_name="gemini-2.5-flash-lite",
                    system_instruction=(
                        "당신은 친절하고 유머러스한 게임 전문가 챗봇입니다. "
                        "게임 추천, 공략법, 이스터에그, 게임 역사 등 게임 관련 질문에 깊이 있고 재미있게 답변해야 합니다. "
                        "게임 외의 질문을 받으면 게임과 연관 지어 재치 있게 답변하거나, 게임 전문가로서 정중히 거절하세요."
                    )
                )

                # 대화 맥락 유지를 위해 전체 대화 기록을 기반으로 응답 생성
                # Gemini API 형식에 맞게 변환 (user -> user, assistant -> model)
                chat_history = []
                for msg in st.session_state.messages[:-1]: # 방금 입력한 것 제외한 이전 기록
                    role = "user" if msg["role"] == "user" else "model"
                    chat_history.append({"role": role, "parts": [msg["content"]]})

                # 채팅 세션 시작 및 응답 요구
                chat = model.start_chat(history=chat_history)
                response = chat.send_message(user_input)
                
                # 결과 출력 및 저장
                ai_response = response.text
                st.markdown(ai_response)
                st.session_state.messages.append({"role": "assistant", "content": ai_response})

            except Exception as e:
                # 오류 처리 (API 한도 초과, 네트워크 에러 등)
                error_msg = f"⚠️ 에러가 발생했습니다: {str(e)}\n잠시 후 다시 시도해주세요."
                st.error(error_msg)
