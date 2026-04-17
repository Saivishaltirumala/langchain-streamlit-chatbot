import streamlit as st

def inject_global_css():
    """Inject premium dark modern CSS globally."""
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
