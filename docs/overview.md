# Nyro MCP Documentation

Welcome to the official documentation for **Nyro MCP**, a high-performance Model Context Protocol (MCP) server. Nyro MCP provides AI agents with a secure, sandboxed bridge to interact with your local filesystem and system commands.

## Documentation Map

### 🛠️ Tool Manuals
- 📂 **[Filesystem: Read](tools/filesystem-read.md)**: Listing, reading, searching, and metadata.
- 📝 **[Filesystem: Write](tools/filesystem-write.md)**: Creating, modifying, moving, and deleting.
- ⚙️ **[System Operations](tools/system.md)**: Shell command execution and timeouts.

### 🛡️ Security & Technical
- 🏗️ **[Internal Architecture](technical/architecture.md)**: Design principles and module structure.
- 🔒 **[Security & Sandboxing](technical/security.md)**: How `ROOT` enforcement and file blocking works.
- ⚙️ **[Configuration](technical/configuration.md)**: Environment variables and startup settings.

## Core Features

### 1. Secure Sandboxing
Nyro MCP operates within a strict `ROOT` directory. Every path provided by an AI agent is resolved and verified against this boundary. Attempts to access files outside the sandbox are intercepted and blocked.

### 2. Smart File Handling
Support for reading both text (UTF-8) and binary files (Base64). Includes built-in protection against reading sensitive files like private keys or database files.

### 3. Advanced Search
Provides recursive file finding and content searching using glob patterns, allowing agents to navigate large codebases efficiently.

### 4. Interactive Command execution
Enables controlled shell command execution with configurable timeouts to prevent runaway processes.

## Why Nyro MCP?

Nyro MCP is built for production environments where AI needs system access but safety is paramount. It combines the flexibility of `FastMCP` with custom-built security layers, ensuring a robust bridge between LLMs and the local OS.
