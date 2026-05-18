from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent

from core.mcp_tools import get_top_songs, get_top_albums, list_genres, get_top_songs_all_genres


SYSTEM_PROMPT = (
    "You are a highly capable AI assistant. Answer any question the user asks accurately, "
    "professionally, and clearly.\n\n"
    "You also have access to Indian music chart tools that provide real-time data from iTunes India. "
    "ONLY use these tools when users specifically ask about trending songs, top albums, or music charts "
    "for Indian languages (Telugu, Bollywood/Hindi, Tamil, Punjabi, Marathi, etc.). "
    "For all other questions, answer directly from your knowledge without using any tools. "
    "When you do use music tools, present the results in a clean, readable format."
)


@tool
def tool_get_top_songs(genre: str, limit: int = 10) -> str:
    """Get the current top songs chart for an Indian music genre. Use when user asks about trending/top/popular songs in Indian languages.

    Args:
        genre: Genre name (e.g. "Bollywood", "Telugu", "Tamil", "Punjabi", "Marathi")
        limit: Number of songs to return (1-100, default 10)
    """
    return get_top_songs(genre, limit)


@tool
def tool_get_top_albums(genre: str, limit: int = 10) -> str:
    """Get the current top albums chart for an Indian music genre. Use when user asks about trending/top/popular albums in Indian languages.

    Args:
        genre: Genre name (e.g. "Bollywood", "Telugu", "Tamil", "Punjabi", "Marathi")
        limit: Number of albums to return (1-100, default 10)
    """
    return get_top_albums(genre, limit)


@tool
def tool_list_genres() -> str:
    """List all supported Indian music genres. Use when user asks what genres or languages are available."""
    return list_genres()


@tool
def tool_get_top_songs_all_genres() -> str:
    """Get top 5 songs from every supported Indian music genre in one call. Use when user asks for a broad overview of what's trending across all Indian languages."""
    return get_top_songs_all_genres()


TOOLS = [tool_get_top_songs, tool_get_top_albums, tool_list_genres, tool_get_top_songs_all_genres]


def get_prompt_template():
    """Returns the standard chat prompt configured to use message history."""
    return ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
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


def build_agent(engine, temperature, max_tokens):
    """Instantiates a ReAct agent with MCP music chart tools."""
    llm = init_chat_model(engine, temperature=temperature, max_tokens=max_tokens)
    agent = create_react_agent(llm, TOOLS, prompt=SYSTEM_PROMPT)
    return agent


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


def generate_agent_response(agent, user_input, chat_history):
    """Run the ReAct agent and yield the final response text."""
    messages = chat_history + [{"role": "user", "content": user_input}]
    result = agent.invoke({"messages": messages})
    final_message = result["messages"][-1]
    yield final_message.content
