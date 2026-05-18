import httpx
import json


MCP_SERVER_URL = "https://saivishaltirumala-indian-music-charts-mcp-server.hf.space/mcp"


def _create_session():
    """Initialize MCP session and return session_id."""
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": {"name": "QA-ChatBot", "version": "1.0"},
        },
    }
    resp = httpx.post(MCP_SERVER_URL, json=payload, headers=headers, timeout=15.0)
    session_id = resp.headers.get("mcp-session-id")

    # Send initialized notification
    httpx.post(
        MCP_SERVER_URL,
        json={"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}},
        headers={**headers, "Mcp-Session-Id": session_id},
        timeout=10.0,
    )
    return session_id


def _call_mcp_tool(session_id: str, tool_name: str, arguments: dict) -> str:
    """Call an MCP tool and return the text result."""
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "Mcp-Session-Id": session_id,
    }
    payload = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {"name": tool_name, "arguments": arguments},
    }
    resp = httpx.post(MCP_SERVER_URL, json=payload, headers=headers, timeout=30.0)
    # Parse SSE response
    for line in resp.text.splitlines():
        if line.startswith("data: "):
            data = json.loads(line[6:])
            if "result" in data:
                content_parts = data["result"].get("content", [])
                return "\n".join(part["text"] for part in content_parts if part.get("type") == "text")
    return "No data returned from music charts server."


_session_id = None


def _get_session():
    global _session_id
    if _session_id is None:
        _session_id = _create_session()
    return _session_id


def get_top_songs(genre: str, limit: int = 10) -> str:
    """Get the current top songs chart for an Indian music genre.

    Args:
        genre: Genre name (e.g. "Bollywood", "Telugu", "Tamil", "Punjabi", "Marathi")
        limit: Number of songs to return (1-100, default 10)
    """
    session_id = _get_session()
    return _call_mcp_tool(session_id, "get_top_songs", {"genre": genre, "limit": limit})


def get_top_albums(genre: str, limit: int = 10) -> str:
    """Get the current top albums chart for an Indian music genre.

    Args:
        genre: Genre name (e.g. "Bollywood", "Telugu", "Tamil", "Punjabi", "Marathi")
        limit: Number of albums to return (1-100, default 10)
    """
    session_id = _get_session()
    return _call_mcp_tool(session_id, "get_top_albums", {"genre": genre, "limit": limit})


def list_genres() -> str:
    """List all supported Indian music genres with their iTunes genre IDs."""
    session_id = _get_session()
    return _call_mcp_tool(session_id, "list_genres", {})


def get_top_songs_all_genres() -> str:
    """Get top 5 songs from every supported Indian music genre in one call. Provides a cross-language snapshot of what's trending."""
    session_id = _get_session()
    return _call_mcp_tool(session_id, "get_top_songs_all_genres", {})
