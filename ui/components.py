import streamlit as st
from core.config import get_secret

def render_header():
    """Renders the main title and logo area."""
    st.markdown("""
    <div class="custom-header-container">
        <h1 class="custom-title">✨ Vishal Chatbot</h1>
        <p class="custom-subtitle">Your Personalized AI Companion</p>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Renders the sidebar and returns configuration settings."""
    env_api_key = get_secret("GROQ_API_KEY")
    api_key = None
    
    with st.sidebar:
        st.markdown("### ⚙️ Control Panel")
        
        with st.expander("🔐 Authentication", expanded=False):
            use_admin_key = st.checkbox("Use Default Admin Key", value=True)
            if use_admin_key:
                api_key = env_api_key
                st.text_input("Groq API Key:", type="password", disabled=True, placeholder="Disabled")
                if api_key:
                    st.success("Admin Key Active ✓")
                else:
                    st.warning("Admin Key missing.")
            else:
                api_key = st.text_input("Groq API Key:", type="password")
        
        st.markdown("### 🧠 Model Preferences")
        engine = st.selectbox("Engine", ["groq:qwen/qwen3-32b", "groq:openai/gpt-oss-120b", "groq:llama-3.1-8b-instant"], index=1)
        
        with st.expander("🔧 Advanced Settings", expanded=False):
            temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.1)
            max_tokens = st.slider("Max Tokens", min_value=50, max_value=4000, value=1000, step=50)

        st.divider()
        st.link_button("⭐ Review App on GitHub", "https://github.com/Saivishaltirumala/langchain-streamlit-chatbot", use_container_width=True)
        st.divider()
        
        if st.button("🗑️ Clear Chat Context", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
            
    return {
        "api_key": api_key,
        "engine": engine,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
