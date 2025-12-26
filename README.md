
<div align="center">

# 📂 Nyro MCP

**Powerful filesystem & system tools for Model Context Protocol**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

## 📖 Overview

**Nyro MCP** is a robust Model Context Protocol (MCP) server designed to provide LLMs with safe, comprehensive access to filesystem operations and system commands. Built on top of `FastMCP`, it offers a secure bridge for AI agents to interact with your local environment, featuring detailed logging, safety checks, and modular architecture.

## ✨ Features

- **Filesystem Mastery**: Read, write, create, delete, move, and copy files and directories.
- **Advanced Search**: Recursive file finding, content searching with glob patterns, and regex support.
- **Archives**: Create and extract ZIP archives on the fly.
- **Safety First**: Strict `ROOT` path enforcement prevents access outside designated directories.
- **System Integration**: Execute shell commands with timeout protection and output capturing.
- **Detailed Telemetry**: Comprehensive colored logging for all operations.

## 🛠️ Installation

1. **Clone the repository**:

    ```bash
    git clone https://github.com/TheRemyyy/nyro-mcp.git
    cd nyro-mcp
    ```

2. **Install dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

## 🚀 Usage

Nyro MCP is designed to be run as a standalone MCP server.

```bash
# Run using the module entry point
python -m src.nyro_mcp.main
```

### Configuration

The root directory for file operations is currently configured in `src/nyro_mcp/config.py`:

```python
ROOT = Path(r"C:\Users\wNyro_\Documents\Projects\CustomMC\1.21.9-src")
```

*Note: Ensure this path exists or update it to your desired sandbox directory.*

## 📦 Project Structure

```
nyro-mcp/
├── src/
│   └── nyro_mcp/
│       ├── tools/          # Modular tool definitions
│       │   ├── fs_read.py  # Read operations
│       │   ├── fs_write.py # Write operations
│       │   └── system.py   # System command execution
│       ├── config.py       # Configuration & constants
│       ├── main.py         # Application entry point
│       ├── server.py       # FastMCP server instance
│       └── utils.py        # Helper functions & logging
├── requirements.txt
└── README.md
```

## 📄 License

This project is licensed under the MIT License.
