import os
import streamlit as st
from dotenv import load_dotenv

def initialize_config():
    """Load env variables and securely set required API keys globally."""
    load_dotenv()
    
    # Set Langsmith variables
    langchain_api_key = get_secret("LANGCHAIN_API_KEY")
    if langchain_api_key:
        os.environ["LANGCHAIN_API_KEY"] = langchain_api_key
        
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_PROJECT"] = "Simple Q&A Chatbot With GROQ"

def get_secret(key_name, default=""):
    """Fetch secret securely, prioritizing Streamlit Cloud secrets then local .env."""
    try:
        if key_name in st.secrets:
            return st.secrets[key_name]
    except Exception:
        pass
    return os.getenv(key_name, default)

def set_groq_api_key(api_key):
    """Set the GROQ API key dynamically into environment variables for LangChain to pick up."""
    if api_key:
        os.environ["GROQ_API_KEY"] = api_key
