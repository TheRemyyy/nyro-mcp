import logging
from pathlib import Path
from .config import LEVEL_COLORS, GRAY, WHITE, RESET, RED, settings

class ToolError(Exception):
    """Custom exception for specific tool errors."""
    pass

class CustomFormatter(logging.Formatter):
    def format(self, record):
        color = LEVEL_COLORS.get(record.levelname, WHITE)
        time_part = self.formatTime(record, "%H:%M")
        log_fmt = (
            f"{GRAY}{time_part}{RESET} "
            f"{color}{record.levelname}{RESET} "
            f"{GRAY}NyroMCP:{RESET} "
            f"{WHITE}{record.getMessage()}{RESET}"
        )
        return log_fmt

def setup_logger():
    logger = logging.getLogger("nyro_mcp")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(CustomFormatter())
    logger.propagate = False
    logger.addHandler(handler)
    return logger

logger = setup_logger()

def safe_path(p: Path | str) -> Path:
    """
    Ensures the path is within the defined ROOT directory. 
    Critical for security to prevent directory traversal.
    """
    if settings.ROOT is None:
        raise ToolError("internal_error: ROOT path not initialized.")

    if isinstance(p, str):
        p = settings.ROOT / p
    
    p = p.resolve()
    
    # Check if the resolved path starts with the ROOT path
    if not str(p).startswith(str(settings.ROOT)):
        logger.error(f"{RED}SECURITY ERROR: Attempted access outside ROOT directory: {p}{RESET}")
        raise ToolError("outside_root")
    return p
