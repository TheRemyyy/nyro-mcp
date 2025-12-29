# Security & Sandboxing

Security is the primary design goal of Nyro MCP. It employs multiple layers of defense to ensure that AI agents cannot perform malicious actions or access sensitive data.

## 🔒 ROOT Path Enforcement

The central security mechanism is the `safe_path` function found in `utils.py`.

### How it works:
1.  **Resolution**: Every path provided by an agent is combined with the session `ROOT` and resolved using `pathlib.Path.resolve()`. This eliminates directory traversal attacks (e.g., `../../windows/system32`).
2.  **Boundary Check**: The absolute resolved path must start with the absolute `ROOT` path.
3.  **Blocking**: If the check fails, a `SECURITY ERROR` is logged, and the tool raises an `outside_root` error.

## 🚫 File Blocking

To prevent accidental exposure of credentials or sensitive data, `read_file` implements an extension-based blocklist.

**Blocked Extensions:**
- `.pem`, `.key`, `.pfx` (Private Keys & Certificates)
- `.sqlite`, `.db` (Databases)
- `.p12` (Personal Information Exchange)

## ⏱️ Execution Safety

- **Command Timeouts**: All shell commands have a mandatory timeout (default 120s) to prevent resource exhaustion or hanging tasks.
- **Memory Management**: Large files are read using `offset` and `length` parameters, preventing the server from crashing due to memory spikes when reading multi-gigabyte logs.

## 📝 Secure Logging

Every action performed by an agent is logged to the console with:
- Timestamp.
- Tool name.
- Input parameters (sanitized).
- Outcome (Success/Failure).

This provides a full audit trail for the human operator.
