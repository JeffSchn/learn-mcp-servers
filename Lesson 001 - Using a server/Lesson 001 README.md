# Lesson 001 - Your First MCP Server

**Objective:** Use an MCP host with a local and a remote MCP server.
**Outcome:** Search the Microsoft Docs and run the local server from [Lesson 002](<../Lesson 002 - Your first MCP server>), which just simply returns a variation test text of `hello world`.

## Steps

1. Download and install Claude Desktop and VS Code with initial setup if needed. Subscriptions and licenses might be required, depending on what you want to do and what models that you want to use; this is an area changing rapidly so I will provide no advice or guidance about licensing.
2. Download and install [Python](http://python.org).
3. Install the required Python libraries by running this command in your terminal:
    ```bash
    pip install -r requirements.txt
    ```
    or
    ```bash
    python -m pip install -r requirements.txt
    ```
    or (on a Mac)
    ```bash
    python3 -m pip install -r requirements.txt
    ```
    - This will install all the necessary dependencies listed in the `requirements.txt` file in the root directory
    - If you're using a virtual environment (recommended), activate it first before running the pip command
4. Create the config files. There are several examples:
    - [claude_config.json](claude_config.json) (Lesson 002 example local server only)
    - [.vscode/mcp.json](../.vscode/mcp.json) 