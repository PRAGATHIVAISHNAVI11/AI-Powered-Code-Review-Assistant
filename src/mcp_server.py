import asyncio, os, json
from dotenv import load_dotenv
from mcp.server import Server
from mcp.types import Tool, TextContent, CallToolRequest, CallToolResult
from .types import CodeSnippet
from .build_graph import build_reviewer

load_dotenv()

server = Server("ai-code-review-assistant")

graph = None

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(name="review_code", description="Analyze a code snippet and return suggestions (JSON).", inputSchema={
            "type": "object",
            "properties": {
                "path": {"type":"string"},
                "language": {"type":"string"},
                "content": {"type":"string"}
            },
            "required": ["content"]
        })
    ]

@server.call_tool()
async def call_tool(name: str, request: CallToolRequest) -> CallToolResult:
    global graph
    if graph is None:
        graph = build_reviewer("data/corpus", os.getenv("EMBED_MODEL","sentence-transformers/all-MiniLM-L6-v2"))

    if name == "review_code":
        args = request.arguments or {}
        snippet = CodeSnippet(
            path=args.get("path","<buffer>"),
            language=args.get("language","text"),
            content=args["content"]
        )
        state = graph.invoke({"snippet": snippet})
        payload = {
            "suggestions": [s.model_dump() for s in state["merged"]],
            "acceptance_likelihood": state.get("_acceptance_likelihood", 0.6)
        }
        return CallToolResult(content=[TextContent(type="text", text=json.dumps(payload, indent=2))])
    else:
        raise ValueError("Unknown tool")

async def amain():
    # stdio server (works with many MCP clients)
    await server.run_stdio()

if __name__ == "__main__":
    asyncio.run(amain())
