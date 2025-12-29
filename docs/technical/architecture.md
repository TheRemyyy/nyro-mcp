# Internal Architecture

Nyro MCP is built using a modular, functional design on top of the `mcp` Python framework.

## Component Overview

### 1. `main.py` (Entry Point)
Handles the startup sequence, interactive configuration (asking for ROOT path), and initialization of the `FastMCP` server.

### 2. `server.py`
Instantiates the `FastMCP` server object. This central object is imported by all tool modules to register decorators.

### 3. Modular Tools (`tools/`)
Tool definitions are grouped by responsibility:
- `fs_read.py`: Passive inspection tools.
- `fs_write.py`: Active modification tools.
- `system.py`: External command integration.

### 4. `utils.py` (Core Logic)
Provides critical shared functionality:
- `safe_path`: Boundary enforcement logic.
- `CustomFormatter`: Colored logging for the TUI.
- `ToolError`: Standardized exception handling.

## Data Flow

1.  **Request**: An AI agent sends an MCP request (e.g., `list_dir`).
2.  **Dispatch**: `FastMCP` maps the request to the decorated function.
3.  **Security Gate**: The function calls `safe_path()` to validate all provided paths.
4.  **Execution**: The core logic (e.g., `pathlib` or `subprocess`) is executed.
5.  **Telemetry**: The `logger` captures the operation details.
6.  **Response**: The result is serialized to JSON and sent back to the agent.

## Design Philosophy

- **Self-Contained**: No external database or heavy dependencies required.
- **Fail-Fast**: Security violations result in immediate termination of the current tool execution.
- **Transparent**: The server's output is designed to be easily readable by humans during monitoring.
