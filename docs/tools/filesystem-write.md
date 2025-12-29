# Filesystem Tools: Write

These tools enable AI agents to modify the filesystem, including creating files, editing content, and managing archives.

## 📝 File Modification

### `write_file(path, content, append=False)`
Writes text to a file.
- **Overwrite**: Default behavior.
- **Append**: If `append=True`, content is added to the end of the file.

### `create_file(path, content="")`
Creates a new file. Fails if the file already exists.

### `replace_in_file(path, find_text, replace_with, replace_all=False)`
Powerful tool for precise editing.
- **`replace_all`**: If `true`, all instances are replaced. If `false`, only the first one.

### `insert_into_file(path, content_to_insert, at_line)`
Inserts text at a specific line number (1-indexed).
- **Behavior**: Shifts existing lines down. If `at_line` exceeds file length, it appends to the end.

### `touch_file(path)`
Updates the timestamp or creates an empty file.

## 📁 Management & Moving

### `create_dir(path)`
Creates a directory and any necessary parent directories (`mkdir -p`).

### `rename_dir(src_path, new_name)` / `rename_file(src_path, new_name)`
Renames a path. The `new_name` must be a name only, not a full path.

### `delete_path(path)`
Recursively deletes a file or directory. **Protected**: Cannot delete the `ROOT` directory.

### `move_path(src, dst)` / `copy_path(src, dst)`
Standard move and copy operations (recursive for directories).

## 📦 Archive Support

### `zip_files(archive_path, files_to_add, base_dir=".")`
Creates a ZIP archive from a list of files/directories.

### `unzip_file(archive_path, extract_to_dir)`
Extracts a ZIP archive to a target directory.
