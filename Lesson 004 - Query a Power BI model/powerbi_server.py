"""
Minimal Power BI MCP Server for querying and discovery (FastMCP)

Example prompts to test this server:
/list_workspaces
/list_datasets workspace_id="your-workspace-id"
/get_model_definition workspace_id="your-workspace-id" dataset_id="your-dataset-id"
/execute_dax_query workspace_id="your-workspace-id" dataset_id="your-dataset-id" query="EVALUATE VALUES('Date'[Year])"
"""

import json
import requests
import os
# Using keyring library
import keyring
# FastMCP for simplified MCP server creation
from fastmcp import FastMCP

# Create FastMCP server instance
mcp = FastMCP("powerbi-server")

# Power BI API configuration
# Power BI API base URL
API_BASE = "https://api.powerbi.com/v1.0/myorg"
# Get token from environment
# TOKEN = os.environ.get("POWERBI_TOKEN", "")
# Get token from keyring
TOKEN = keyring.get_password("powerbi", "token")

def call_powerbi_api(endpoint, method="GET", data=None):
    """Make actual API calls to Power BI"""
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

@mcp.tool()
def list_workspaces() -> str:
    """List all Power BI workspaces you have access to.
    
    Use when: starting analysis, finding workspace IDs, or exploring available workspaces.
    Examples: 'show my workspaces', 'what Power BI workspaces do I have?', 'list workspaces'
    
    Returns:
        String containing list of workspaces with their names and IDs.
    """
    # Call Power BI API to get workspaces
    result = call_powerbi_api("/groups")
    
    # Format response
    if "error" in result:
        return f"Error: {result['error']}"
    
    # Parse workspace list
    workspaces = result.get("value", [])
    output = f"Found {len(workspaces)} workspaces:\n\n"
    # Show first 10
    for ws in workspaces[:10]:
        output += f"- {ws['name']} (ID: {ws['id']})\n"
    
    return output

@mcp.tool()
def list_datasets(workspace_id: str) -> str:
    """List all datasets in a specific workspace.
    
    Use when: exploring workspace contents, finding dataset IDs, or checking available data.
    Examples: 'show datasets in workspace X', 'what data is available?', 'list all datasets'.
    
    Args:
        workspace_id: The ID of the workspace (get from list_workspaces)
    
    Returns:
        String containing list of datasets with their names and IDs.
    """
    # Get datasets for specific workspace
    result = call_powerbi_api(f"/groups/{workspace_id}/datasets")
    
    # Format response
    if "error" in result:
        return f"Error: {result['error']}"
    
    # Parse dataset list
    datasets = result.get("value", [])
    output = f"Found {len(datasets)} datasets:\n\n"
    for ds in datasets:
        output += f"- {ds['name']} (ID: {ds['id']})\n"
    
    return output

@mcp.tool()
def get_model_definition(workspace_id: str, dataset_id: str) -> str:
    """Get the schema/model definition of a dataset including tables, columns, and relationships.
    
    Use when: understanding data structure, checking column names, or planning queries.
    Examples: 'show me the data model', 'what tables are in this dataset?', 'describe the schema'
    
    Args:
        workspace_id: The ID of the workspace
        dataset_id: The ID of the dataset (get from list_datasets)
    
    Returns:
        String containing model schema information.
    """
    # Get dataset schema
    result = call_powerbi_api(f"/groups/{workspace_id}/datasets/{dataset_id}/datasources")
    
    # Format response
    if "error" in result:
        return f"Error: {result['error']}"
    
    # Basic info about the model
    output = f"Dataset {dataset_id} model info retrieved.\n"
    output += f"Datasources: {len(result.get('value', []))}\n"
    
    return output

@mcp.tool()
def execute_dax_query(workspace_id: str, dataset_id: str, query: str) -> str:
    """Execute a DAX query against a Power BI dataset.
    
    Use when: retrieving specific data, calculating measures, or analyzing data.
    Examples: 'get sales by region', 'calculate total revenue', 'show top 10 products'.
    Example DAX Query: EVALUATE SUMMARIZECOLUMNS( 'Date'[Year], 'Date'[Month], \"@Sales\", SUM ( 'Sales'[Amount] ) )
    
    Args:
        workspace_id: The ID of the workspace
        dataset_id: The ID of the dataset
        query: The DAX query to execute (e.g., 'EVALUATE VALUES(Sales[Product])')
    
    Returns:
        String containing query execution results.
    """
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
        return f"Error: {result['error']}"
    
    # Parse query results
    output = f"Query executed successfully.\n"
    results = result.get("results", [])
    if results and "tables" in results[0]:
        output += f"Returned {len(results[0]['tables'])} table(s)\n"
    
    return output

# Run the server when script is executed directly
if __name__ == "__main__":
    # Check for auth token
    if not TOKEN:
        print("Warning: Power BI token not found in keyring")
        print("Set it with: keyring set powerbi token")
        print("Then enter your token when prompted")
    
    mcp.run()