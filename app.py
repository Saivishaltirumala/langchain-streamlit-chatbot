import streamlit as st
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain.chat_models import init_chat_model
import os
from dotenv import load_dotenv

# Set up page config FIRST before any other st commands
st.set_page_config(page_title="AI Chatbot Assistant", page_icon="⚡", layout="wide")

load_dotenv()

# --- CSS INJECTION FOR PREMIUM DARK "INDIGO/CYBER" THEME ---
custom_css = """
<style>
/* Import Inter font */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"]  {
    font-family: 'Inter', sans-serif;
}

/* App Background - Deepest slate almost black */
.stApp {
    background-color: #020617;
}

/* Hide default streamlit header */
header {
    visibility: hidden;
}

/* Sidebar Background with gradient */
[data-testid="stSidebar"] {
    background-color: #0f172a !important;
    background-image: linear-gradient(180deg, #0f172a 0%, #1e1b4b 100%);
    border-right: 1px solid #1e293b;
}

/* Top Gradient Header Card */
.custom-header-container {
    background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%);
    border-radius: 16px;
    padding: 2rem;
    margin-bottom: 2rem;
    border: 1px solid #4338ca;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
    text-align: left;
}

.custom-title {
    color: #ffffff;
    font-weight: 800;
    font-size: 2.2rem;
    margin-bottom: 0.2rem;
    margin-top: 0;
}

.custom-subtitle {
    color: #a5b4fc;
    font-size: 1rem;
    font-weight: 500;
    margin: 0;
}

/* Secondary Headers in Sidebar */
h1, h2, h3, h4, h5, h6 {
    color: #f8fafc !important;
}
p, span, label {
    color: #cbd5e1 !important;
}

/* Chat Input Styling */
[data-testid="stChatInput"] {
    border-radius: 16px;
    border: 1px solid #4338ca !important;
    background-color: #1e1b4b !important;
    box-shadow: 0 4px 15px rgba(67, 56, 202, 0.4);
}
[data-testid="stChatInput"] textarea {
    color: #ffffff !important;
}
[data-testid="stChatInput"] button {
    background-color: #6366f1 !important;
    color: white !important;
    border-radius: 8px;
}

/* General Input Boxes in Sidebar */
[data-testid="stTextInput"] input {
    background-color: #1e293b !important;
    border: 1px solid #334155 !important;
    color: #f8fafc !important;
    border-radius: 8px !important;
}

[data-baseweb="select"] > div {
    background-color: #1e293b !important;
    border: 1px solid #334155 !important;
    color: #f8fafc !important;
    border-radius: 8px !important;
}

/* Chat Bubbles - Assistant */
[data-testid="stChatMessage"] {
    background-color: #1e293b;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    border: 1px solid #334155;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5);
}

/* Chat Bubbles - User */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background-color: #312e81; /* Deep Indigo */
    border: 1px solid #4338ca;
}

/* Remove default background colors from avatars inside the bubble */
[data-testid="chatAvatarIcon-user"] {
    background-color: transparent !important;
}
[data-testid="chatAvatarIcon-assistant"] {
    background-color: transparent !important;
}

/* Code block matching Figma */
pre {
    background-color: #0f172a !important;
    border: 1px solid #1e293b !important;
    border-radius: 8px !important;
}

/* Custom Buttons */
.stButton button {
    border-radius: 8px !important;
    border: 1px solid #4338ca !important;
    background-color: transparent !important;
    color: #a5b4fc !important;
    transition: all 0.2s ease;
}
.stButton button:hover {
    background-color: #4338ca !important;
    color: white !important;
}

/* Sidebar Dividers */
hr {
    border-color: #334155 !important;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)


# Fetch secret securely, prioritizing Streamlit Cloud secrets then falling back to local .env
def get_secret(key_name, default=""):
    try:
        if key_name in st.secrets:
            return st.secrets[key_name]
    except Exception:
        pass
    return os.getenv(key_name, default)

## Langsmith Tracking
os.environ["LANGCHAIN_API_KEY"] = get_secret("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Simple Q&A Chatbot With GROQ"

# We will set GROQ_API_KEY dynamically from sidebar, secrets, or .env
env_api_key = get_secret("GROQ_API_KEY")

## Prompt Template
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a highly capable AI assistant. Please respond to user queries accurately, professionally, and clearly."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{question}")
    ]
)

def build_chain(engine, temperature, max_tokens):
    llm = init_chat_model(engine, temperature=temperature, max_tokens=max_tokens)
    # We remove StrOutputParser so we can access chunk.response_metadata to check finish_reason
    chain = prompt | llm
    return chain

## Title and styling layout
st.markdown("""
<div class="custom-header-container">
    <h1 class="custom-title">✨ Vishal Chatbot</h1>
    <p class="custom-subtitle">Your Personalized AI Companion</p>
</div>
""", unsafe_allow_html=True)

## Sidebar for settings
with st.sidebar:
    st.markdown("### ⚙️ Control Panel")
    
    with st.expander("🔐 Authentication", expanded=False):
        use_admin_key = st.checkbox("Use Default Admin Key", value=True)
        if use_admin_key:
            api_key_input = st.text_input("Groq API Key:", type="password", disabled=True, placeholder="Disabled")
            api_key = env_api_key
            if api_key:
                st.success("Admin Key Active ✓")
            else:
                st.warning("Admin Key missing.")
        else:
            api_key = st.text_input("Groq API Key:", type="password")
    
    st.markdown("### 🧠 Model Preferences")
    ## Select the Groq model
    engine = st.selectbox("Engine", ["groq:qwen/qwen3-32b", "groq:openai/gpt-oss-120b", "groq:llama-3.1-8b-instant"], index=1)
    
    ## Advanced parameter settings
    with st.expander("🔧 Advanced Settings", expanded=False):
        temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.1)
        max_tokens = st.slider("Max Tokens", min_value=50, max_value=4000, value=1000, step=50)

    st.divider()
    
    # Custom Github Review Button
    st.link_button("⭐ Review App on GitHub", "https://github.com/Saivishaltirumala/langchain-streamlit-chatbot", use_container_width=True)
    
    st.divider()
    if st.button("🗑️ Clear Chat Context", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Set environmental variable dynamically
if api_key:
    os.environ["GROQ_API_KEY"] = api_key

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Add a welcoming system message dynamically as a visual affordance
    st.session_state.messages.append({"role": "assistant", "content": "Hello, I'm **Vishal Chatbot**! ✨ I am your personalized AI assistant, ready to help you analyze, troubleshoot, and build. How can I accelerate your work today?"})

# User/Assistant custom avatars
# Ensure you save your image file as "gibli_avatar.png" in the 1-QA-ChatBot folder!
avatar_map = {
    "user": "gibli_avatar.png",
    "assistant": "🤖"
}

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=avatar_map.get(message["role"])):
        st.markdown(message["content"])

# React to user input
if user_input := st.chat_input("Type your message..."):
    if not api_key:
        st.toast("Please configure your Groq API Key in the sidebar or check 'Use Default Admin Key'.", icon="⚠️")
    else:
        # Display user message in chat message container
        st.chat_message("user", avatar=avatar_map["user"]).markdown(user_input)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Display assistant response in chat message container
        with st.chat_message("assistant", avatar=avatar_map["assistant"]):
            try:
                chain = build_chain(engine, temperature, max_tokens)
                
                # Format conversation history
                chat_history = []
                # Exclude the very last message since it's the current user_input, and the first intro message if it's the default
                for msg in st.session_state.messages[:-1]:
                    # Don't send our artificial welcoming message to the API context history to save tokens
                    if msg["content"].startswith("Hello, I'm **Vishal Chatbot**"):
                        continue
                        
                    if msg["role"] == "user":
                        chat_history.append(HumanMessage(content=msg["content"]))
                    elif msg["role"] == "assistant":
                        chat_history.append(AIMessage(content=msg["content"]))

                # Custom stream generator to intercept finish_reason and append warning
                def generate_response():
                    finish_reason = None
                    for chunk in chain.stream({'question': user_input, 'chat_history': chat_history}):
                        if hasattr(chunk, "response_metadata") and chunk.response_metadata:
                            if "finish_reason" in chunk.response_metadata and chunk.response_metadata["finish_reason"]:
                                finish_reason = chunk.response_metadata["finish_reason"]
                        if chunk.content:
                            yield chunk.content
                    
                    if finish_reason in ["length", "max_tokens"]:
                        yield "\n\n> ⚠️ **Notice:** *This response was truncated due to the current Max Tokens limit. Please increase the Max Tokens slider in the Advanced Settings to see longer responses.*"

                # Use st.write_stream to type out the response
                full_response = st.write_stream(generate_response())
                
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                st.error(f"An error occurred while communicating with the model: {e}")