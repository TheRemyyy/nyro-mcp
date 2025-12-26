import os
import shutil
import zipfile
from ..server import mcp
from ..utils import logger, safe_path, ToolError, RED, GREEN, BLUE, RESET
from ..config import settings

@mcp.tool()
def create_dir(path: str):
    """Creates a directory, including all necessary parent directories."""
    logger.info(f"Attempting to create directory: {path}")
    try:
        p = safe_path(path)
        p.mkdir(parents=True, exist_ok=True)
        logger.info(f"{BLUE}SUCCESS: Directory '{path}' created (or already matched).{RESET}")
        return {"status": "created_or_exists"}
    except ToolError as e:
        logger.error(f"{RED}Error creating directory '{path}': {e}{RESET}")
        raise
    except Exception as e:
        logger.error(f"{RED}Unexpected error creating directory: {type(e).__name__} - {e}{RESET}")
        raise ToolError(f"internal_error: {e}")

@mcp.tool()
def rename_dir(src_path: str, new_name: str):
    """Renames a directory. The new name must not contain a path."""
    logger.info(f"Attempting to rename directory '{src_path}' to '{new_name}'")
    try:
        if '/' in new_name or '\\' in new_name:
            raise ToolError("invalid_name: New name cannot contain path separators.")

        s = safe_path(src_path)
        if not s.is_dir():
            raise ToolError("not_dir: Source path is not a directory.")

        d = s.resolve().parent / new_name
        if d.exists():
            raise ToolError("already_exists: Destination with this name already exists.")

        s.rename(d)
        logger.info(f"{GREEN}SUCCESS: Directory renamed from '{src_path}' to '{d.relative_to(settings.ROOT)}'.{RESET}")
        return {"status": "renamed", "new_path": str(d.relative_to(settings.ROOT))}
    except ToolError as e:
        logger.error(f"{RED}Error renaming directory '{src_path}': {e}{RESET}")
        raise
    except Exception as e:
        logger.error(f"{RED}Unexpected error renaming directory: {type(e).__name__} - {e}{RESET}")
        raise ToolError(f"internal_error: {e}")

@mcp.tool()
def write_file(path: str, content: str, append: bool = False):
    """Writes or appends text content to a file."""
    mode_str = 'append' if append else 'overwrite'
    logger.info(f"Attempting to write to file: {path} (mode: {mode_str})")
    try:
        p = safe_path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        mode = "a" if append else "w"
        with open(p, mode, encoding="utf-8") as fh:
            chars_written = fh.write(content)
        logger.info(f"{GREEN}SUCCESS: Written {chars_written} chars to '{path}' in '{mode_str}' mode.{RESET}")
        return {"status": "ok", "chars_written": chars_written}
    except ToolError as e:
        logger.error(f"{RED}Error writing to '{path}': {e}{RESET}")
        raise
    except Exception as e:
        logger.error(f"{RED}Unexpected error writing to '{path}': {type(e).__name__} - {e}{RESET}")
        raise ToolError(f"internal_error: {e}")

@mcp.tool()
def create_file(path: str, content: str = ""):
    """Creates a new file with optional initial content. Fails if file already exists."""
    logger.info(f"Attempting to create new file: {path}")
    try:
        p = safe_path(path)
        if p.exists():
            raise ToolError("already_exists: File already exists at this path")

        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")

        logger.info(f"{GREEN}SUCCESS: File '{path}' created with {len(content)} chars.{RESET}")
        return {"status": "created", "path": str(p.relative_to(settings.ROOT))}
    except ToolError as e:
        logger.error(f"{RED}Error creating file '{path}': {e}{RESET}")
        raise
    except Exception as e:
        logger.error(f"{RED}Unexpected error creating file: {type(e).__name__} - {e}{RESET}")
        raise ToolError(f"internal_error: {e}")

@mcp.tool()
def rename_file(src_path: str, new_name: str):
    """Renames a file. The new name must not contain a path."""
    logger.info(f"Attempting to rename file '{src_path}' to '{new_name}'")
    try:
        if '/' in new_name or '\\' in new_name:
            raise ToolError("invalid_name: New name cannot contain path separators.")

        s = safe_path(src_path)
        if not s.is_file():
            raise ToolError("not_file: Source path is not a file.")

        d = s.resolve().parent / new_name
        if d.exists():
            raise ToolError("already_exists: Destination with this name already exists.")

        s.rename(d)
        logger.info(f"{GREEN}SUCCESS: File renamed from '{src_path}' to '{d.relative_to(settings.ROOT)}'.{RESET}")
        return {"status": "renamed", "new_path": str(d.relative_to(settings.ROOT))}
    except ToolError as e:
        logger.error(f"{RED}Error renaming file '{src_path}': {e}{RESET}")
        raise
    except Exception as e:
        logger.error(f"{RED}Unexpected error renaming file: {type(e).__name__} - {e}{RESET}")
        raise ToolError(f"internal_error: {e}")

@mcp.tool()
def replace_in_file(path: str, find_text: str, replace_with: str, replace_all: bool = False):
    """Replaces occurrences of a string in a text file. Can replace single or all instances."""
    op_type = "all instances" if replace_all else "first instance"
    logger.info(f"Attempting to replace {op_type} of text in file: {path}")
    try:
        p = safe_path(path)
        if not p.is_file():
            raise ToolError("not_file: File not found")

        content = p.read_text(encoding='utf-8')
        
        replaces_count = content.count(find_text)
        if replaces_count == 0:
            raise ToolError("not_found: Search text not found in file.")

        if replace_all:
            new_content = content.replace(find_text, replace_with)
        else:
            new_content = content.replace(find_text, replace_with, 1)
            replaces_count = 1

        p.write_text(new_content, encoding='utf-8')
        
        logger.info(f"{BLUE}SUCCESS: Replaced {replaces_count} instances in file '{path}'.{RESET}")
        return {"status": "replaced", "replaces_count": replaces_count}
    except ToolError as e:
        logger.error(f"{RED}Error replacing text in '{path}': {e}{RESET}")
        raise
    except UnicodeDecodeError:
        raise ToolError("decode_error: File is not a valid text file (UTF-8).")
    except Exception as e:
        logger.error(f"{RED}Unexpected error replacing text: {type(e).__name__} - {e}{RESET}")
        raise ToolError(f"internal_error: {e}")

@mcp.tool()
def insert_into_file(path: str, content_to_insert: str, at_line: int):
    """Inserts text content at a specific line in a file. Lines are 1-indexed."""
    logger.info(f"Inserting text into file '{path}' at line {at_line}")
    try:
        p = safe_path(path)
        if not p.is_file():
            raise ToolError("not_file: File not found")
        
        # Read lines preserving line endings
        lines = p.read_text(encoding='utf-8').splitlines(True)
        
        if at_line < 1:
            at_line = 1
        
        if at_line > len(lines):
             # Append to end with newline if needed
            if lines and not lines[-1].endswith('\n'):
                lines[-1] += '\n'
            lines.append(content_to_insert)
        else:
            # Insert at specified line (index is 0-based)
            lines.insert(at_line - 1, content_to_insert + '\n')
            
        p.write_text("".join(lines), encoding='utf-8')
        
        logger.info(f"{GREEN}SUCCESS: Content inserted into '{path}' at line {at_line}.{RESET}")
        return {"status": "inserted", "line_number": at_line}
    except ToolError as e:
        logger.error(f"{RED}Error inserting into file '{path}': {e}{RESET}")
        raise
    except UnicodeDecodeError:
        raise ToolError("decode_error: File is not a valid text file (UTF-8).")
    except Exception as e:
        logger.error(f"{RED}Unexpected error inserting into file: {type(e).__name__} - {e}{RESET}")
        raise ToolError(f"internal_error: {e}")

@mcp.tool()
def touch_file(path: str):
    """Updates file timestamp or creates an empty file if it doesn't exist."""
    logger.info(f"Touching file: {path}")
    try:
        p = safe_path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.touch()
        logger.info(f"{GREEN}SUCCESS: File '{path}' touched.{RESET}")
        return {"status": "touched"}
    except Exception as e:
        logger.error(f"{RED}Unexpected error during touch operation: {type(e).__name__} - {e}{RESET}")
        raise ToolError(f"internal_error: {e}")

@mcp.tool()
def delete_path(path: str):
    """Deletes a file or directory (recursively)."""
    logger.info(f"Attempting to delete path: {path}")
    try:
        p = safe_path(path)
        if p == settings.ROOT:
            raise ToolError("cannot_delete_root: Deleting the root directory is not allowed.")

        if p.is_file():
            p.unlink()
            status = "deleted_file"
            logger.info(f"{GREEN}SUCCESS: File '{path}' deleted.{RESET}")
        elif p.is_dir():
            shutil.rmtree(p)
            status = "deleted_dir"
            logger.info(f"{GREEN}SUCCESS: Directory '{path}' recursively deleted.{RESET}")
        else:
            raise ToolError("not_exist: Path does not exist")

        return {"status": status}
    except ToolError as e:
        logger.error(f"{RED}Error deleting '{path}': {e}{RESET}")
        raise
    except Exception as e:
        logger.error(f"{RED}Unexpected error deleting '{path}': {type(e).__name__} - {e}{RESET}")
        raise ToolError(f"internal_error: {e}")

@mcp.tool()
def move_path(src: str, dst: str):
    """Moves a file or directory from source to destination."""
    logger.info(f"Attempting to move: from '{src}' to '{dst}'")
    try:
        s = safe_path(src)
        d = safe_path(dst)
        if not s.exists():
            raise ToolError("not_exist: Source path does not exist.")
        
        shutil.move(str(s), str(d))
        logger.info(f"{GREEN}SUCCESS: Move from '{src}' to '{dst}' completed.{RESET}")
        return {"status": "moved"}
    except ToolError as e:
        logger.error(f"{RED}Error moving '{src}' to '{dst}': {e}{RESET}")
        raise
    except Exception as e:
        logger.error(f"{RED}Unexpected error moving path: {type(e).__name__} - {e}{RESET}")
        raise ToolError(f"internal_error: {e}")

@mcp.tool()
def copy_path(src: str, dst: str):
    """Copies a file or directory from source to destination."""
    logger.info(f"Attempting to copy: from '{src}' to '{dst}'")
    try:
        s = safe_path(src)
        d = safe_path(dst)
        if not s.exists():
            raise ToolError("not_exist: Source path does not exist.")

        if s.is_file():
            shutil.copy2(str(s), str(d))
            status = "copied_file"
        elif s.is_dir():
            shutil.copytree(str(s), str(d))
            status = "copied_dir"
        else:
             raise ToolError("not_file_or_dir: Source is neither file nor directory.")

        logger.info(f"{GREEN}SUCCESS: Copy from '{src}' to '{dst}' completed.{RESET}")
        return {"status": status}
    except ToolError as e:
        logger.error(f"{RED}Error copying '{src}' to '{dst}': {e}{RESET}")
        raise
    except Exception as e:
        logger.error(f"{RED}Unexpected error copying path: {type(e).__name__} - {e}{RESET}")
        raise ToolError(f"internal_error: {e}")

@mcp.tool()
def zip_files(archive_path: str, files_to_add: list[str], base_dir: str = "."):
    """Creates a zip archive from a list of files or directories."""
    logger.info(f"Creating zip archive '{archive_path}' from {len(files_to_add)} items.")
    try:
        archive_p = safe_path(archive_path)
        base_p = safe_path(base_dir)

        with zipfile.ZipFile(archive_p, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in files_to_add:
                full_path = safe_path(base_p / file_path)
                if not full_path.exists():
                    logger.warning(f"Item '{file_path}' does not exist and will be skipped.")
                    continue
                    
                if full_path.is_file():
                    arcname = full_path.relative_to(base_p)
                    zipf.write(full_path, arcname)
                elif full_path.is_dir():
                    for root, dirs, files in os.walk(full_path):
                        for file in files:
                            abs_file_path = Path(root) / file
                            arcname = abs_file_path.relative_to(base_p)
                            zipf.write(abs_file_path, arcname)

        logger.info(f"{GREEN}SUCCESS: Archive '{archive_path}' created.{RESET}")
        return {"status": "created", "archive_path": str(archive_p.relative_to(settings.ROOT))}
    except ToolError as e:
        logger.error(f"{RED}Error creating zip archive: {e}{RESET}")
        raise
    except Exception as e:
        logger.error(f"{RED}Unexpected error creating zip: {type(e).__name__} - {e}{RESET}")
        raise ToolError(f"internal_error: {e}")

@mcp.tool()
def unzip_file(archive_path: str, extract_to_dir: str):
    """Extracts a zip archive to the specified directory."""
    logger.info(f"Extracting archive '{archive_path}' to '{extract_to_dir}'")
    try:
        archive_p = safe_path(archive_path)
        extract_p = safe_path(extract_to_dir)
        
        if not archive_p.is_file():
            raise ToolError("not_file: Archive not found")
        extract_p.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(archive_p, 'r') as zipf:
            zipf.extractall(extract_p)
            
        logger.info(f"{GREEN}SUCCESS: Archive extracted to '{extract_to_dir}'.{RESET}")
        return {"status": "extracted"}
    except zipfile.BadZipFile:
        raise ToolError("bad_zip_file: File is not a valid zip archive.")
    except ToolError as e:
        logger.error(f"{RED}Error extracting archive: {e}{RESET}")
        raise
    except Exception as e:
        logger.error(f"{RED}Unexpected error extracting archive: {type(e).__name__} - {e}{RESET}")
        raise ToolError(f"internal_error: {e}")
