---
title: Langchain Streamlit Chatbot
emoji: 💬
colorFrom: blue
colorTo: indigo
sdk: docker
app_file: app.py
pinned: false
---

# Enhanced Q&A Chatbot

This is a Streamlit chatbot deployed on Hugging Face Spaces using Docker.

## Features

- Multi-model support (Groq: Qwen3, GPT-OSS, LLaMA 3.1)
- Real-time token streaming
- Indian Music Charts integration via MCP (Model Context Protocol)

## MCP Integration

This chatbot connects to a remote MCP server to provide real-time Indian music chart data.

**MCP Server:** https://huggingface.co/spaces/saivishaltirumala/indian-music-charts-mcp-server

**How it connects:**

The chatbot uses a manual HTTP approach to call the MCP server — sending JSON-RPC requests directly via `httpx` to the Streamable HTTP endpoint (`/mcp`). This works well for synchronous apps like Streamlit where the official async MCP SDK introduces event loop conflicts.

```
User asks "Top Telugu songs"
    → LangGraph ReAct Agent decides to call tool
        → core/mcp_tools.py sends POST /mcp to HF Space
            → MCP server fetches from iTunes RSS API
        ← Returns live chart data
    ← Agent formats response
Displayed in Streamlit UI
```

**Alternative (industry-standard) approach:**

For async applications or production systems, the recommended way is to use `langchain-mcp-adapters` which auto-discovers tools and generates LangChain wrappers automatically:

```python
from langchain_mcp_adapters.client import MultiServerMCPClient

async with MultiServerMCPClient(
    {
        "indian-music-charts": {
            "url": "https://saivishaltirumala-indian-music-charts-mcp-server.hf.space/mcp",
            "transport": "streamable_http",
        }
    }
) as client:
    tools = client.get_tools()  # Auto-converts MCP tools → LangChain tools
    agent = create_react_agent(llm, tools)
```

Benefits of the SDK approach:
- Auto-discovers tools (no hardcoding)
- If the MCP server adds new tools, client picks them up automatically
- Proper protocol handling, retries, and error management

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```
