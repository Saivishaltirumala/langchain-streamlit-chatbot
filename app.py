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

/* App Background */
.stApp {
    background-color: #0f172a;
}

/* Sidebar Background */
[data-testid="stSidebar"] {
    background-color: #1a1c24 !important;
    border-right: 1px solid #2d3748;
}

/* Top Gradient Header */
.custom-title {
    background: linear-gradient(135deg, #8b5cf6 0%, #38bdf8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
    font-size: 3rem;
    margin-bottom: 0rem;
    padding-bottom: 0rem;
}

.custom-subtitle {
    color: #94a3b8;
    font-size: 1.1rem;
    font-weight: 500;
    margin-top: 0.2rem;
    margin-bottom: 2rem;
}

/* Secondary Headers */
h1, h2, h3, h4, h5, h6 {
    color: #f8fafc !important;
}
p, span, label {
    color: #cbd5e1 !important;
}

/* Chat Input Styling */
[data-testid="stChatInput"] {
    border-radius: 12px;
    border: 1px solid #334155 !important;
    background-color: #1e293b !important;
}
[data-testid="stChatInput"] textarea {
    color: #ffffff !important;
}

/* General Input Boxes */
.stTextInput input, .stSelectbox select, .stSelectbox div {
    background-color: #1e293b !important;
    border: 1px solid #334155 !important;
    color: #f8fafc !important;
    border-radius: 8px !important;
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
    output_parser = StrOutputParser()
    chain = prompt | llm | output_parser
    return chain

## Title and styling
st.markdown('<h1 class="custom-title">⚡ AI Assistant Interface</h1>', unsafe_allow_html=True)
st.markdown('<p class="custom-subtitle">Powered by advanced Groq open-source models.</p>', unsafe_allow_html=True)

## Sidebar for settings
with st.sidebar:
    st.markdown("### ⚙️ Control Panel")
    
    with st.expander("🔐 Authentication", expanded=True):
        use_admin_key = st.checkbox("Use Default Admin Key", value=True)
        if use_admin_key:
            api_key_input = st.text_input("Groq API Key:", type="password", disabled=True, prompt="Disabled")
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
        max_tokens = st.slider("Max Tokens", min_value=50, max_value=2000, value=150, step=50)

    st.divider()
    
    # Custom Github Review Button
    st.link_button("⭐ Review App on GitHub", "https://github.com/Saivishaltirumala/langchain-streamlit-chatbot", use_container_width=True)
    
    st.divider()
    if st.button("🗑️ Clear Chat Context", use_container_width=True, type="secondary"):
        st.session_state.messages = []
        st.rerun()

# Set environmental variable dynamically
if api_key:
    os.environ["GROQ_API_KEY"] = api_key

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Add a welcoming system message dynamically as a visual affordance
    st.session_state.messages.append({"role": "assistant", "content": "Welcome to the AI Assistant platform! I am securely connected and ready. Ask me anything!"})

# User/Assistant custom avatars
avatar_map = {
    "user": "👤",
    "assistant": "✨"
}

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=avatar_map.get(message["role"])):
        st.markdown(message["content"])

# React to user input
if user_input := st.chat_input("Type your message here..."):
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
                    if msg["content"].startswith("Welcome to the AI Assistant platform"):
                        continue
                        
                    if msg["role"] == "user":
                        chat_history.append(HumanMessage(content=msg["content"]))
                    elif msg["role"] == "assistant":
                        chat_history.append(AIMessage(content=msg["content"]))

                # Use st.write_stream to type out the response
                response_stream = chain.stream({'question': user_input, 'chat_history': chat_history})
                full_response = st.write_stream(response_stream)
                
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                st.error(f"An error occurred while communicating with the model: {e}")