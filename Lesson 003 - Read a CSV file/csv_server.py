"""
Enhanced CSV Reader MCP Server with Aggregation

Example prompts to test this server:
/read_csv file_path="/path/to/your/data.csv"
/aggregate_csv file_path="sample.csv" group_by="Category" agg_column="Sales_Amount" agg_function="sum"
/aggregate_csv file_path="sample.csv" group_by="Region,Customer_Type" agg_column="Units_Sold" agg_function="mean"
"""

#region imports
# For async/await functionality
import asyncio
# For reading and analyzing CSV files
import pandas as pd
# For file path handling
from pathlib import Path
# Correct module for stdio communication
import mcp.server.stdio
from mcp.server import Server, NotificationOptions
# Server initialization config
from mcp.server.models import InitializationOptions
# Type definitions for tools and responses
from mcp.types import Tool, TextContent
#endregion

#region variables
# Create a new MCP server instance
server = Server("csv-reader-server-enhanced")
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
        ),
        Tool(
            name="aggregate_csv",
            description=(
                "Aggregates data in a CSV file by grouping columns and applying aggregation functions. "
                "Use when: calculating totals, averages, counts, or other statistics by category. "
                "Examples: 'sum sales by region', 'average units sold by category', 'count products by type'. "
                "Supported functions: sum, mean, count, min, max, std"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the CSV file to aggregate"
                    },
                    "group_by": {
                        "type": "string",
                        "description": "Column name(s) to group by. Use comma-separated for multiple columns (e.g., 'Category,Region')"
                    },
                    "agg_column": {
                        "type": "string",
                        "description": "Column name to aggregate"
                    },
                    "agg_function": {
                        "type": "string",
                        "description": "Aggregation function to apply: sum, mean, count, min, max, std"
                    }
                },
                "required": ["file_path", "group_by", "agg_column", "agg_function"]
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
    
    elif name == "aggregate_csv":
        try:
            file_path = Path(arguments["file_path"])
            group_by = arguments["group_by"]
            agg_column = arguments["agg_column"]
            agg_function = arguments["agg_function"].lower()
            
            if not file_path.exists():
                return [TextContent(type="text", text=f"Error: File not found at {file_path}")]
            
            # Read the CSV file
            df = pd.read_csv(file_path)
            
            # Parse group_by columns (handle comma-separated values)
            group_columns = [col.strip() for col in group_by.split(',')]
            
            # Validate columns exist
            missing_cols = [col for col in group_columns if col not in df.columns]
            if missing_cols:
                return [TextContent(type="text", text=f"Error: Columns not found: {missing_cols}")]
            
            if agg_column not in df.columns:
                return [TextContent(type="text", text=f"Error: Aggregation column '{agg_column}' not found")]
            
            # Validate aggregation function
            valid_functions = ['sum', 'mean', 'count', 'min', 'max', 'std']
            if agg_function not in valid_functions:
                return [TextContent(type="text", text=f"Error: Invalid function '{agg_function}'. Valid options: {valid_functions}")]
            
            # Perform aggregation
            if agg_function == 'count':
                # For count, we don't need to specify the column
                agg_result = df.groupby(group_columns).size().reset_index(name='count')
                agg_col_name = 'count'
            else:
                # Apply the aggregation function
                agg_result = df.groupby(group_columns)[agg_column].agg(agg_function).reset_index()
                agg_col_name = agg_column
            
            # Build result message
            result = f"Aggregation Results:\n"
            result += f"File: {file_path}\n"
            result += f"Grouped by: {', '.join(group_columns)}\n"
            result += f"Aggregation: {agg_function}({agg_column if agg_function != 'count' else 'rows'})\n\n"
            
            # Format the results
            result += agg_result.to_string(index=False)
            
            # Add summary stats
            if agg_function != 'count':
                total = agg_result[agg_col_name].sum() if agg_function in ['sum', 'mean'] else None
                if total is not None:
                    result += f"\n\nTotal {agg_function}: {total:,.2f}"
            
            return [TextContent(type="text", text=result)]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error aggregating CSV: {str(e)}")]
    
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
                server_name="csv-reader-server-enhanced",
                server_version="0.2.0",
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
