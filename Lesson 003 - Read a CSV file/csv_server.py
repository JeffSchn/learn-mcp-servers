"""
Minimal CSV Reader MCP Server

Example prompts to test this server:
/read_csv file_path="/path/to/your/data.csv"
/read_csv file_path="sales_data.csv"
"""

#region imports
import asyncio
# For reading and analyzing CSV files
import pandas as pd
# For file path handling
from pathlib import Path

import mcp.server.stdio
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.types import Tool, TextContent
#endregion


#region variables
# Create a new MCP server instance
server = Server("csv-reader-server")
#endregion


#region MCP functions
## Define available tools for the LLM
@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="read_csv",
            description=(
                "Reads a CSV file and returns its contents and basic info. "
                "Use when: analyzing data files, checking CSV structure, or viewing data samples. "
                "Examples: 'read sales.csv', 'analyze the data file', 'show me what's in the CSV'"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {  
                        "type": "string",
                        "description": "Path to the CSV file to read. Can be absolute (/Users/name/data.csv) or relative (data/sales.csv)"
                    }
                },
                "required": ["file_path"]
            }
        )
    ]


## Handle tool execution requests
@server.call_tool()
async def call_tool(name, arguments):
    if name == "read_csv":
        try:
            file_path = Path(arguments["file_path"])
            
            if not file_path.exists():
                return [TextContent(type="text", text=f"Error: File not found at {file_path}")]
            
            # Read the CSV file into a dataframe
            df = pd.read_csv(file_path)
            
            # Build result message with file info
            result = f"Successfully read CSV: {file_path}\n"
            result += f"Shape: {df.shape[0]} rows × {df.shape[1]} columns\n"
            result += f"Columns: {', '.join(df.columns)}\n\n"
            
            # Add first 5 rows as preview
            result += "First 5 rows:\n"
            result += df.head().to_string()
            
            return [TextContent(type="text", text=result)]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error reading CSV: {str(e)}")]
    
    return [TextContent(type="text", text=f"Unknown tool: {name}")]
#endregion


#region functions
## Main entry point
async def main():
    # Use the stdio_server context manager to get read/write streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        # Run the server with streams and initialization options as positional arguments
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="csv-reader-server",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            ),
        )

# Run the server when script is executed directly
if __name__ == "__main__":
    asyncio.run(main())
#endregion