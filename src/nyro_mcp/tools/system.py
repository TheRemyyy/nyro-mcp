import subprocess
from ..server import mcp
from ..utils import logger, safe_path, ToolError, RED, GREEN, RESET
from ..config import settings

@mcp.tool()
def run_command(cmd: str, cwd: str = ".", timeout: int = 120):
    """Executes a shell command in the specified working directory with a timeout."""
    logger.info(f"Attempting to run command: {cmd} in '{cwd}' with timeout {timeout}s")
    try:
        work_dir = safe_path(cwd)
        if not work_dir.is_dir():
            raise ToolError("not_dir: Working directory does not exist")

        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=False, cwd=str(work_dir), timeout=timeout, encoding='utf-8', errors='ignore')
        
        if result.returncode != 0:
            logger.warning(f"Command ended with error (RC: {result.returncode}). STDERR: {result.stderr.strip()[:200]}...")
            
        logger.info(f"{GREEN}SUCCESS: Command processed (RC: {result.returncode}).{RESET}")
        
        return {"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode}
    except subprocess.TimeoutExpired as e:
        logger.error(f"{RED}Command '{cmd}' timed out after {timeout} seconds.{RESET}")
        return {"stdout": e.stdout, "stderr": e.stderr, "returncode": -1, "error": "timeout"}
    except Exception as e:
        logger.error(f"{RED}Unexpected error running command '{cmd}': {type(e).__name__} - {e}{RESET}")
        raise ToolError(f"internal_error: {e}")
