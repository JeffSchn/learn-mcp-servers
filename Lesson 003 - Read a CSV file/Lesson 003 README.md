# Lesson 003 - Read a CSV file

**Objective:** Create an MCP server that can read and analyze CSV files.
**Outcome:** Build a server with a `read_csv` tool that can load CSV files, show their contents, and provide basic information about the data.

## Steps

1. Run the CSV server from the provided code: [csv_server.py](csv_server.py)
2. The server provides one tool: `read_csv` 
3. Test with prompts like:
   - "read my CSV file"
   - "analyze data.csv"
   - "show me what's in the sales file"

## What You'll Learn

- How to handle file operations in MCP servers
- Working with parameters (file paths)
- Using pandas for data processing
- Error handling for missing files

## Example Usage

```
User: "Read the file sales_data.csv"
Server: Shows file contents, row count, column names, and sample data
```