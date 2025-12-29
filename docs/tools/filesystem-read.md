# Filesystem Tools: Read

These tools allow AI agents to explore the directory structure, inspect file contents, and retrieve metadata.

## 📂 Directory Operations

### `list_dir(path=".")`
Lists the contents of a directory with detailed metadata.
- **Output**: Array of items with `name`, `path` (relative to ROOT), `is_dir`, `size`, and `last_modified`.
- **Sorting**: Directories first, then files (alphabetically).

### `get_dir_size(path=".")`
Calculates the total recursive size of a directory.
- **Benefit**: Helps agents understand disk usage before performing large operations.

## 📖 File Operations

### `read_file(path, offset=0, length=2,000,000)`
Reads file content with support for pagination and binary data.
- **Text Mode**: Returns `content` if the file is UTF-8.
- **Binary Mode**: Automatically detects non-text data and returns `content_b64`.
- **Security**: Blocks access to sensitive extensions (`.pem`, `.key`, `.db`, etc.).

### `get_file_stat(path)`
Retrieves OS-level statistics for a path.
- **Fields**: `size`, `is_dir`, `last_modified`, `created`.

### `calculate_hash(path, algorithm="sha256")`
Calculates the cryptographic hash of a file.
- **Supported Algorithms**: Any algorithm supported by Python's `hashlib`.

## 🔍 Search & Navigation

### `find_files(pattern, base_path=".")`
Recursively finds files matching a glob pattern (e.g., `**/*.py`).
- **Output**: List of matching paths relative to ROOT.

### `search_in_files(search_text, glob_pattern="*", base_path=".")`
Searches for specific text inside multiple files.
- **Output**: Map of file paths to arrays of matching lines (`line_number`, `line_content`).
- **Intelligence**: Automatically skips binary files and unreadable content.
