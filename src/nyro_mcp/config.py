from pathlib import Path

class Settings:
    """Global application settings."""
    ROOT: Path = None

# Initialize global settings instance
settings = Settings()

# --- Color Configuration ---
GRAY = '\033[90m'
WHITE = '\033[37m'
GREEN = '\033[32m'
RED = '\033[31m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
RESET = '\033[0m'

LEVEL_COLORS = {
    'INFO': GREEN,
    'ERROR': RED,
    'WARNING': YELLOW,
    'CRITICAL': RED,
}
