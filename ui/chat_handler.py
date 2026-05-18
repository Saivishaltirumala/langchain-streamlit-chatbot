import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from core.llm_chain import build_agent, generate_agent_response

AVATAR_MAP = {
    "user": "gibli_avatar.png",
    "assistant": "🤖"
}

def init_chat_session():
    """Initializes the chat history state context."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.append({
            "role": "assistant",
            "content": "Hello, I'm **Vishal Chatbot**! ✨ I am your personalized AI assistant, ready to help you analyze, troubleshoot, and build. I can also tell you what's trending in Indian music — just ask about top Telugu, Bollywood, Tamil, Punjabi songs or albums!"
        })

def render_chat_history():
    """Renders the previous messages visually into the DOM."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar=AVATAR_MAP.get(message["role"])):
            st.markdown(message["content"])

def handle_user_input(config):
    """Processes new user input and streams assistant response."""
    user_input = st.chat_input("Type your message...")
    if not user_input:
        return

    if not config.get("api_key"):
        st.toast("Please configure your Groq API Key in the sidebar or check 'Use Default Admin Key'.", icon="⚠️")
        return

    # 1. Display user message visibly
    st.chat_message("user", avatar=AVATAR_MAP["user"]).markdown(user_input)
    # 2. Append to state
    st.session_state.messages.append({"role": "user", "content": user_input})

    # 3. Format conversational memory for the agent
    chat_history = []
    for msg in st.session_state.messages[:-1]:
        if msg["content"].startswith("Hello, I'm **Vishal Chatbot**"):
            continue
        chat_history.append({"role": msg["role"], "content": msg["content"]})

    # 4. Invoke agent and write response
    with st.chat_message("assistant", avatar=AVATAR_MAP["assistant"]):
        try:
            agent = build_agent(config["engine"], config["temperature"], config["max_tokens"])
            response_gen = generate_agent_response(agent, user_input, chat_history)

            full_response = st.write_stream(response_gen)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"An error occurred: {e}")
