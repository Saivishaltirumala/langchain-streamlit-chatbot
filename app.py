import streamlit as st
from core.config import initialize_config, set_groq_api_key
from ui.styles import inject_global_css
from ui.components import render_header, render_sidebar
from ui.chat_handler import init_chat_session, render_chat_history, handle_user_input

# 1. Page Configuration MUST be the first Streamlit command
st.set_page_config(page_title="AI Chatbot Assistant", page_icon="⚡", layout="wide")

def main():
    # 2. Inject CSS globally
    inject_global_css()
    
    # 3. Load core environment variables and secrets
    initialize_config()
    
    # 4. Render main layout and fetch user settings from sidebar
    render_header()
    config = render_sidebar()
    
    # 5. Set dynamic keys needed by LangChain
    set_groq_api_key(config["api_key"])
    
    # 6. Initialize chat memory and display history
    init_chat_session()
    render_chat_history()
    
    # 7. Await and handle new user inputs
    handle_user_input(config)

if __name__ == "__main__":
    main()