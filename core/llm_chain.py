from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chat_models import init_chat_model

def get_prompt_template():
    """Returns the standard chat prompt configured to use message history."""
    return ChatPromptTemplate.from_messages(
        [
            ("system", "You are a highly capable AI assistant. Please respond to user queries accurately, professionally, and clearly."),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{question}")
        ]
    )

def build_chain(engine, temperature, max_tokens):
    """Instantiates the model and chain without an output parser to allow metadata streaming."""
    llm = init_chat_model(engine, temperature=temperature, max_tokens=max_tokens)
    prompt = get_prompt_template()
    chain = prompt | llm
    return chain

def generate_streaming_response(chain, user_input, chat_history):
    """Custom stream generator to intercept finish_reason and append a warning if token limited."""
    finish_reason = None
    for chunk in chain.stream({'question': user_input, 'chat_history': chat_history}):
        if hasattr(chunk, "response_metadata") and chunk.response_metadata:
            if "finish_reason" in chunk.response_metadata and chunk.response_metadata["finish_reason"]:
                finish_reason = chunk.response_metadata["finish_reason"]
        if chunk.content:
            yield chunk.content
    
    if finish_reason in ["length", "max_tokens"]:
        yield "\n\n> ⚠️ **Notice:** *This response was truncated due to the current Max Tokens limit. Please increase the Max Tokens slider in the Advanced Settings to see longer responses.*"
