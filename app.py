import streamlit as st
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain.chat_models import init_chat_model
import os
from dotenv import load_dotenv

# Set up page config FIRST before any other st commands
st.set_page_config(page_title="Enhanced Q&A Chatbot", page_icon="💬", layout="wide")

load_dotenv()

## Langsmith Tracking
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY", "")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Simple Q&A Chatbot With GROQ"

# We will set GROQ_API_KEY dynamically from sidebar or .env
env_api_key = os.getenv("GROQ_API_KEY", "")

## Prompt Template
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant. Please respond to the user queries accurately and clearly."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "Question: {question}")
    ]
)

def build_chain(engine, temperature, max_tokens):
    llm = init_chat_model(engine, temperature=temperature, max_tokens=max_tokens)
    output_parser = StrOutputParser()
    chain = prompt | llm | output_parser
    return chain

## Title and styling
st.title("💬 Enhanced Q&A Chatbot With Groq")
st.markdown("Welcome! Ask me anything, and I'll generate a response using the selected Groq model.")

## Sidebar for settings
with st.sidebar:
    st.header("Settings")
    
    # Ask for Groq API KEY
    api_key = st.text_input("Enter your Groq API Key:", type="password", value=env_api_key)
    
    ## Select the Groq model
    engine = st.selectbox("Select Groq model", ["groq:qwen/qwen3-32b", "groq:openai/gpt-oss-120b", "groq:llama-3.1-8b-instant"])
    
    ## Advanced parameter settings
    with st.expander("Advanced Settings", expanded=False):
        temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.1)
        max_tokens = st.slider("Max Tokens", min_value=50, max_value=2000, value=150, step=50)

    st.divider()
    if st.button("Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Set environmental variable dynamically
if api_key:
    os.environ["GROQ_API_KEY"] = api_key

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if user_input := st.chat_input("Go ahead and ask a question..."):
    if not api_key:
        st.toast("Please enter your Groq API Key in the sidebar!", icon="⚠️")
        st.error("Missing API Key. Please provide it to continue.")
    else:
        # Display user message in chat message container
        st.chat_message("user").markdown(user_input)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            try:
                chain = build_chain(engine, temperature, max_tokens)
                
                # Format conversation history
                chat_history = []
                # Exclude the very last message since it's the current user_input
                for msg in st.session_state.messages[:-1]:
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
                st.error(f"An error occurred: {e}")