"""
Minimal Power BI MCP Server for querying and discovery

Example prompts to test this server:
/list_workspaces
/list_datasets workspace_id="your-workspace-id"
/get_model_definition workspace_id="your-workspace-id" dataset_id="your-dataset-id"
/execute_dax_query workspace_id="your-workspace-id" dataset_id="your-dataset-id" query="EVALUATE VALUES('Date'[Year])"
"""

#region imports
import asyncio
import json
import requests
import os

# Using keyring library
import keyring

import mcp.server.stdio
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.types import Tool, TextContent
#endregion


#region variables
# Create MCP server instance
server = Server("powerbi-server")

# Power BI API configuration
# Power BI API base URL
API_BASE = "https://api.powerbi.com/v1.0/myorg"
# Get token from environment
# TOKEN = os.environ.get("POWERBI_TOKEN", "")
# Get token from keyring
TOKEN = keyring.get_password("powerbi", "token")
#endregion


#region MCP functions

## Define available Power BI tools
@server.list_tools()
async def list_tools():
    # Return list of Power BI analysis tools
    return [
        Tool(
            name="list_workspaces",
            description=(
                "List all Power BI workspaces you have access to. "
                "Use when: starting analysis, finding workspace IDs, or exploring available workspaces. "
                "Examples: 'show my workspaces', 'what Power BI workspaces do I have?', 'list workspaces'"
            ),
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="list_datasets",  
            description=(
                "List all datasets in a specific workspace. "
                "Use when: exploring workspace contents, finding dataset IDs, or checking available data. "
                "Examples: 'show datasets in workspace X', 'what data is available?', 'list all datasets'. "
                "Requires: workspace_id"
            ),
            inputSchema={
                "type": "object", 
                "properties": {
                    "workspace_id": {
                        "type": "string",
                        "description": "The ID of the workspace (get from list_workspaces)"
                    }
                },
                "required": ["workspace_id"]
            }
        ),
        Tool(
            name="get_model_definition",  
            description=(
                "Get the schema/model definition of a dataset including tables, columns, and relationships. "
                "Use when: understanding data structure, checking column names, or planning queries. "
                "Examples: 'show me the data model', 'what tables are in this dataset?', 'describe the schema'"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    # Required workspace ID
                    "workspace_id": {
                        "type": "string", 
                        "description": "The ID of the workspace"
                    },
                    # Required dataset ID
                    "dataset_id": {
                        "type": "string",
                        "description": "The ID of the dataset (get from list_datasets)"
                    }
                },
                "required": ["workspace_id", "dataset_id"]
            }
        ),
        Tool(
            name="execute_dax_query",
            description=(
                "Execute a DAX query against a Power BI dataset. "
                "Use when: retrieving specific data, calculating measures, or analyzing data. "
                "Examples: 'get sales by region', 'calculate total revenue', 'show top 10 products'. "
                "Example DAX Query: EVALUATE SUMMARIZECOLUMNS( 'Date'[Year], 'Date'[Month], \"@Sales\", SUM ( 'Sales'[Amount] ) )"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    # Required workspace ID
                    "workspace_id": {
                        "type": "string",
                        "description": "The ID of the workspace"
                    },
                    # Required dataset ID
                    "dataset_id": {
                        "type": "string", 
                        "description": "The ID of the dataset"
                    },
                    # Required DAX query
                    "query": {
                        "type": "string",
                        "description": "The DAX query to execute (e.g., 'EVALUATE VALUES(Sales[Product])')"
                    }
                },
                "required": ["workspace_id", "dataset_id", "query"]
            }
        )
    ]

## Make actual API calls to Power BI
def call_powerbi_api(endpoint, method="GET", data=None):
    # Set up headers with auth token
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Make the API request
    try:
        if method == "GET":
            response = requests.get(f"{API_BASE}{endpoint}", headers=headers)
        else:
            response = requests.post(f"{API_BASE}{endpoint}", headers=headers, json=data)
        
        # Return JSON response if successful
        if response.ok:
            return response.json()
        else:
            return {"error": f"API error: {response.status_code} - {response.text}"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}

## Handle tool execution - calls real Power BI APIs
@server.call_tool()
async def call_tool(name, arguments):
    
    if name == "list_workspaces":
        # Call Power BI API to get workspaces
        result = call_powerbi_api("/groups")
        
        # Format response
        if "error" in result:
            return [TextContent(type="text", text=f"Error: {result['error']}")]
        
        # Parse workspace list
        workspaces = result.get("value", [])
        output = f"Found {len(workspaces)} workspaces:\n\n"
        # Show first 10
        for ws in workspaces[:10]:
            output += f"- {ws['name']} (ID: {ws['id']})\n"
        
        return [TextContent(type="text", text=output)]
    
    elif name == "list_datasets":
        # Get datasets for specific workspace
        workspace_id = arguments["workspace_id"]
        result = call_powerbi_api(f"/groups/{workspace_id}/datasets")
        
        # Format response
        if "error" in result:
            return [TextContent(type="text", text=f"Error: {result['error']}")]
        
        # Parse dataset list
        datasets = result.get("value", [])
        output = f"Found {len(datasets)} datasets:\n\n"
        for ds in datasets:
            output += f"- {ds['name']} (ID: {ds['id']})\n"
        
        return [TextContent(type="text", text=output)]
    
    elif name == "get_model_definition":
        # Get dataset schema
        workspace_id = arguments["workspace_id"]
        dataset_id = arguments["dataset_id"]
        
        # Call datasources endpoint for schema info
        result = call_powerbi_api(f"/groups/{workspace_id}/datasets/{dataset_id}/datasources")
        
        # Format response
        if "error" in result:
            return [TextContent(type="text", text=f"Error: {result['error']}")]
        
        # Basic info about the model
        output = f"Dataset {dataset_id} model info retrieved.\n"
        output += f"Datasources: {len(result.get('value', []))}\n"
        
        return [TextContent(type="text", text=output)]
    
    elif name == "execute_dax_query":
        # Execute DAX query
        workspace_id = arguments["workspace_id"]
        dataset_id = arguments["dataset_id"]
        query = arguments["query"]
        
        # Prepare query payload
        data = {
            "queries": [{
                "query": query
            }]
        }
        
        # Call execute queries endpoint
        result = call_powerbi_api(
            f"/groups/{workspace_id}/datasets/{dataset_id}/executeQueries",
            method="POST",
            data=data
        )
        
        # Format response
        if "error" in result:
            return [TextContent(type="text", text=f"Error: {result['error']}")]
        
        # Parse query results
        output = f"Query executed successfully.\n"
        results = result.get("results", [])
        if results and "tables" in results[0]:
            output += f"Returned {len(results[0]['tables'])} table(s)\n"
        
        return [TextContent(type="text", text=output)]
    
    # Return error for unknown tools
    return [TextContent(type="text", text=f"Unknown tool: {name}")]
#endregion


#region functions
## Main entry point
async def main():
    # Check for auth token
    if not TOKEN:
        print("Warning: Power BI token not found in keyring")
        print("Set it with: keyring set powerbi token")
        print("Then enter your token when prompted")
    
    # Use the stdio_server context manager to get read/write streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        # Run the server with streams and initialization options as positional arguments
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="powerbi-server",
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