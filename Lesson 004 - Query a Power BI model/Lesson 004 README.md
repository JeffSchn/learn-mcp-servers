# Lesson 004 - Query a Power BI model

**Objective:** Create an MCP server that connects to Power BI REST APIs to query workspaces, datasets, and run DAX queries.
**Outcome:** Build a server with 4 tools that can discover Power BI workspaces, list datasets, get model definitions, and execute DAX queries.

## Steps

1. Run the Power BI server from the provided code: [powerbi_server.py](powerbi_server.py)
2. The server provides four tools:
   - `list_workspaces` - Find your Power BI workspaces
   - `list_datasets` - Show datasets in a workspace
   - `get_model_definition` - Get dataset schema information
   - `execute_dax_query` - Run DAX queries against datasets
3. Test with prompts like:
   - "show my Power BI workspaces"
   - "list datasets in workspace X"
   - "run this DAX query: EVALUATE VALUES('Date'[Year])"

## Authentication

You'll be prompted for a Power BI API token when first using the server. Get your token from:
- Power BI REST API documentation "Try it" feature
- Azure AD app registration with Power BI API permissions
- PowerShell: `Connect-PowerBIServiceAccount; Get-PowerBIAccessToken`

## What You'll Learn

- How to integrate with REST APIs in MCP servers
- Environment variable handling for authentication
- API response formatting for AI consumption
- Error handling for external API calls