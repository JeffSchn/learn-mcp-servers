from fastmcp import FastMCP

# Server instance
mcp = FastMCP("hello-world")

## Tool Registry
@mcp.tool
def say_hello(name: str = "World") -> str:
    """Says hellow to demonstrate MCP is working"""
    return f"Hello, {name}! MCP server is working!"

if __name__ == "__main__":
    mcp.run()