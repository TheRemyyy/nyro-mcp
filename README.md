<div align="center">

# Nyro MCP

**Powerful filesystem & system tools for Model Context Protocol**

[![Python Version](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

*A secure, interactive bridge for AI agents to master your local environment.*

[Features](#features) • [Installation](#installation) • [Usage](#usage)

</div>

---

## Overview

**Nyro MCP** is a robust Model Context Protocol (MCP) server built to provide LLMs with comprehensive yet safe access to local filesystem operations and system commands. It acts as a controlled interface, featuring a rigorous `ROOT` path sandbox, timeout protection for commands, and detailed colored logging.

### Key Features

- **📂 Filesystem Mastery** — Read, write, create, delete, move, and copy files and directories with ease.
- **🔍 Advanced Search** — Recursively find files and search content using smart glob patterns.
- **📦 Archives** — Create and extract ZIP archives on the fly.
- **🛡️ Safety First** — Strict `ROOT` path enforcement prevents access outside designated directories.
- **⚙️ System Integration** — Execute shell commands with timeout protection and output capturing.
- **📝 Detailed Telemetry** — Comprehensive, colored logging for all operations.

## <a id="installation"></a>📦 Installation

1. **Clone the repository**:

    ```bash
    git clone https://github.com/TheRemyyy/nyro-mcp.git
    cd nyro-mcp
    ```

2. **Install dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

## <a id="usage"></a>🚀 Usage

Nyro MCP is designed to be run as a standalone MCP server.

```bash
# Run using the module entry point
python -m src.nyro_mcp.main
```

### Configuration

Upon starting the server, you will be interactively prompted to specify the **ROOT** directory. This directory acts as a secure sandbox; all file operations are restricted to this path to ensure safety.

```text
NyroMCP - Enhanced File System MCP Server
Please enter the ROOT directory path for this session:
ROOT Path > C:\path\to\your\sandbox
```

## <a id="structure"></a>🏗️ Project Structure

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

## License

This project is licensed under the MIT License.

---

<div align="center">
<sub>Built with ❤️ and Python</sub>
</div>
