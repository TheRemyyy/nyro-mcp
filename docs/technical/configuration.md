# Configuration Reference

Nyro MCP is designed for zero-config startup but provides flexibility through its interactive initialization.

## Startup Configuration

When you run `python -m src.nyro_mcp.main`, the server performs the following steps:

1.  **Title Display**: Shows the NyroMCP banner.
2.  **ROOT Prompt**: Asks the user to input the root directory for the session.
3.  **Initialization**: Sets up the logging and registers all tools.

## Environmental Settings

Currently, settings are managed in `config.py`.

### Security Constants
- `BLOCKLIST_EXTENSIONS`: `{".pem", ".key", ".pfx", ".sqlite", ".db", ".p12"}`.
- `DEFAULT_TIMEOUT`: `120` seconds for shell commands.

### Logging Levels
Logging is set to `INFO` by default to ensure all agent actions are visible.

## Development Settings

To run the server in a specific mode, you can modify `src/nyro_mcp/config.py`:

```python
class Settings:
    ROOT: Path = None  # Initialized at runtime
    # Add more static settings here
```

## Running the Server

```bash
python -m src.nyro_mcp.main
```
*(Note: Ensure you run as a module so that internal relative imports work correctly.)*
