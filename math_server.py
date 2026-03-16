from mcp.server.fastmcp import FastMCP

# MCP server create
mcp = FastMCP("Math Server")

# Tool 1
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

# Tool 2
@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b

if __name__ == "__main__":
    mcp.run()