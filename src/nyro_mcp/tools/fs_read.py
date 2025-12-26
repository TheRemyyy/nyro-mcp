import time
import base64
import hashlib
from ..server import mcp
from ..utils import logger, safe_path, ToolError, RED, GREEN, BLUE, RESET
from ..config import settings

@mcp.tool()
def list_dir(path: str = "."):
    """Lists files and directories in the specified path with details."""
    logger.info(f"Listing directory content: {path}")
    try:
        p = safe_path(path)
        if not p.is_dir():
            raise ToolError("not_dir: Path does not exist or is not a directory")

        items = []
        # Sort by type (directories first) then name
        for c in sorted(p.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
             stat = c.stat()
             items.append({
                 "name": c.name,
                 "path": str(c.relative_to(settings.ROOT)),
                 "is_dir": c.is_dir(),
                 "size": stat.st_size if c.is_file() else None,
                 "last_modified": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stat.st_mtime))
             })

        logger.info(f"{GREEN}SUCCESS: Directory '{path}' listed. Items count: {len(items)}.{RESET}")
        return {"items": items}
    except ToolError as e:
        logger.error(f"{RED}Error listing '{path}': {e}{RESET}")
        raise
    except Exception as e:
        logger.error(f"{RED}Unexpected error listing '{path}': {type(e).__name__} - {e}{RESET}")
        raise ToolError(f"internal_error: {e}")

@mcp.tool()
def get_dir_size(path: str = "."):
    """Calculates the total size of a directory and all its contents recursively."""
    logger.info(f"Calculating size of directory '{path}'...")
    try:
        p = safe_path(path)
        if not p.is_dir():
            raise ToolError("not_dir: Path is not a directory")

        total_size = sum(f.stat().st_size for f in p.glob('**/*') if f.is_file())

        logger.info(f"{GREEN}SUCCESS: Total size of '{path}' is {total_size} bytes.{RESET}")
        return {"path": path, "total_size_bytes": total_size}
    except ToolError as e:
        logger.error(f"{RED}Error calculating size for '{path}': {e}{RESET}")
        raise
    except Exception as e:
        logger.error(f"{RED}Unexpected error calculating size: {type(e).__name__} - {e}{RESET}")
        raise ToolError(f"internal_error: {e}")

@mcp.tool()
def read_file(path: str, offset: int = 0, length: int = 2_000_000):
    """Reads file content, either as text or base64 encoded binary data."""
    logger.info(f"Attempting to read file: {path} (offset: {offset}, length: {length})")
    try:
        p = safe_path(path)
        if not p.is_file():
            raise ToolError("not_file: File not found")

        # Extended security check for sensitive extensions
        if p.suffix.lower() in {".pem", ".key", ".pfx", ".sqlite", ".db", ".p12"}:
            logger.error(f"{RED}File blocked due to extension: {path}{RESET}")
            raise ToolError("blocked_ext: Extension blocked for security reasons")

        with open(p, "rb") as fh:
            fh.seek(offset)
            data = fh.read(length)

        try:
            content = data.decode("utf-8")
            logger.info(f"{GREEN}SUCCESS: File '{path}' read as text. Bytes read: {len(data)}{RESET}")
            return {"is_text": True, "content": content, "offset": offset, "length": len(data), "file_size": p.stat().st_size}
        except UnicodeDecodeError:
            content_b64 = base64.b64encode(data).decode("ascii")
            logger.info(f"{GREEN}SUCCESS: File '{path}' read as binary (B64). Bytes read: {len(data)}{RESET}")
            return {"is_text": False, "content_b64": content_b64, "offset": offset, "length": len(data), "file_size": p.stat().st_size}

    except ToolError as e:
        logger.error(f"{RED}Error reading '{path}': {e}{RESET}")
        raise
    except Exception as e:
        logger.error(f"{RED}Unexpected error reading '{path}': {type(e).__name__} - {e}{RESET}")
        raise ToolError(f"internal_error: {e}")

@mcp.tool()
def find_files(pattern: str, base_path: str = "."):
    """Recursively finds files matching a glob pattern."""
    logger.info(f"Searching for files matching pattern '{pattern}' in '{base_path}'")
    try:
        p = safe_path(base_path)
        if not p.is_dir():
            raise ToolError("not_dir: Base path is not a directory")

        found_paths = [str(f.relative_to(settings.ROOT)) for f in p.rglob(pattern) if f.is_file()]

        logger.info(f"{BLUE}SUCCESS: Found {len(found_paths)} files matching '{pattern}'.{RESET}")
        return {"found_files": found_paths, "count": len(found_paths)}
    except ToolError as e:
        logger.error(f"{RED}Error finding files: {e}{RESET}")
        raise
    except Exception as e:
        logger.error(f"{RED}Unexpected error finding files: {type(e).__name__} - {e}{RESET}")
        raise ToolError(f"internal_error: {e}")

@mcp.tool()
def search_in_files(search_text: str, glob_pattern: str = "*", base_path: str = "."):
    """Searches file content (matching pattern) and returns lines where text was found."""
    logger.info(f"Searching files '{glob_pattern}' in '{base_path}' for text '{search_text}'")
    try:
        p = safe_path(base_path)
        results = {}
        files_searched = 0
        
        for file_path in p.rglob(glob_pattern):
            if file_path.is_file():
                files_searched += 1
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line_num, line in enumerate(f, 1):
                            if search_text in line:
                                relative_path_str = str(file_path.relative_to(settings.ROOT))
                                if relative_path_str not in results:
                                    results[relative_path_str] = []
                                results[relative_path_str].append({"line_number": line_num, "line_content": line.strip()})
                except (UnicodeDecodeError, IOError):
                    # Ignore binary files or files that cannot be read
                    continue
        
        logger.info(f"{BLUE}SUCCESS: Searched {files_searched} files. Matches found in {len(results)} files.{RESET}")
        return {"search_results": results, "files_with_matches": len(results)}
    except Exception as e:
        logger.error(f"{RED}Unexpected error searching files: {type(e).__name__} - {e}{RESET}")
        raise ToolError(f"internal_error: {e}")

@mcp.tool()
def get_file_stat(path: str):
    """Retrieves metadata about a file or directory (size, dates, etc.)."""
    logger.info(f"Getting stats for: {path}")
    try:
        p = safe_path(path)
        if not p.exists():
            raise ToolError("not_exist: Path does not exist")

        stat = p.stat()
        def format_time(t):
            return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t))

        result = {
            "path": str(p.relative_to(settings.ROOT)),
            "size": stat.st_size,
            "is_dir": p.is_dir(),
            "last_modified": format_time(stat.st_mtime),
            "created": format_time(stat.st_ctime)
        }

        logger.info(f"{BLUE}SUCCESS: Stats for '{path}' retrieved (Size: {result['size']} bytes).{RESET}")
        return result
    except ToolError as e:
        logger.error(f"{RED}Error getting stats for '{path}': {e}{RESET}")
        raise
    except Exception as e:
        logger.error(f"{RED}Unexpected error getting stats: {type(e).__name__} - {e}{RESET}")
        raise ToolError(f"internal_error: {e}")

@mcp.tool()
def calculate_hash(path: str, algorithm: str = "sha256"):
    """Calculates file hash using the specified algorithm."""
    logger.info(f"Calculating {algorithm} hash for file: {path}")
    try:
        if algorithm not in hashlib.algorithms_available:
            raise ToolError(f"invalid_algorithm: Algorithm {algorithm} is not supported")

        p = safe_path(path)
        if not p.is_file():
            raise ToolError("not_file: File not found")

        hasher = hashlib.new(algorithm)
        blocksize = 65536
        with open(p, 'rb') as afile:
            buf = afile.read(blocksize)
            while len(buf) > 0:
                hasher.update(buf)
                buf = afile.read(blocksize)

        result_hash = hasher.hexdigest()
        logger.info(f"{BLUE}SUCCESS: Calculated {algorithm} hash for '{path}'.{RESET}")
        return {"hash": result_hash, "algorithm": algorithm}
    except ToolError as e:
        logger.error(f"{RED}Error calculating hash for '{path}': {e}{RESET}")
        raise
    except Exception as e:
        logger.error(f"{RED}Unexpected error calculating hash: {type(e).__name__} - {e}{RESET}")
        raise ToolError(f"internal_error: {e}")
