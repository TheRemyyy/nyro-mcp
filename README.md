<div align="center">

# Nyro MCP

**Powerful filesystem & system tools for Model Context Protocol**

[![Python Version](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

*A secure, interactive bridge for AI agents to master your local environment.*

[Features](#features) • [Installation](#installation) • [Usage](#usage) • [Documentation](#documentation)

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

### Prerequisites

- Python 3.10 or higher.

### Setup

```bash
git clone https://github.com/TheRemyyy/nyro-mcp.git
cd nyro-mcp
pip install -r requirements.txt
```

## <a id="usage"></a>🚀 Usage

Run the utility using the module entry point:

```bash
python -m src.nyro_mcp.main
```

Upon starting, you will be prompted to enter the **ROOT** directory path. This directory acts as the secure sandbox for all future operations.

---

## <a id="documentation"></a>📄 Documentation

For deep-dive information on every tool and security measure, please refer to our documentation:

### Tool Manuals
- 📂 **[Filesystem: Read](docs/tools/filesystem-read.md)** — Listing, reading, searching, and metadata.
- 📝 **[Filesystem: Write](docs/tools/filesystem-write.md)** — Creating, modifying, moving, and deleting.
- ⚙️ **[System Operations](docs/tools/system.md)** — Shell command execution and timeouts.

### Technical & Security
- 📖 **[Documentation Overview](docs/overview.md)** — Project summary and structure.
- 🔒 **[Security & Sandboxing](docs/technical/security.md)** — **READ THIS FIRST**.
- 🏗️ **[Architecture](docs/technical/architecture.md)** — Internal design principles.
- ⚙️ **[Configuration Reference](docs/technical/configuration.md)** — Settings and startup.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">
<sub>Built with ❤️ and Python</sub>
</div>