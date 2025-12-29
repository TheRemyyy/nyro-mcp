# Changelog

All notable changes to **Nyro MCP** will be documented in this file.

## [1.0.0] - 2025-12-29

### Added
- **Initial Release**
- **Enhanced Filesystem Read**: Support for `list_dir`, `get_dir_size`, `read_file`, `find_files`, and `search_in_files`.
- **Enhanced Filesystem Write**: Support for `create_file`, `write_file`, `replace_in_file`, `insert_into_file`, `touch_file`, `delete_path`, `move_path`, and `copy_path`.
- **Archive Management**: Built-in support for `zip_files` and `unzip_file`.
- **System Commands**: `run_command` tool with timeout and sandbox protection.
- **Strict Sandboxing**: Path resolution and boundary verification via `safe_path`.
- **Security Blocklist**: Extension-based blocking for sensitive files.
- **Colored Logging**: Professional TUI output for audit trails.
- **Documentation**: Comprehensive documentation suite in the `docs/` directory.

---
*Built for secure AI-native automation.*
