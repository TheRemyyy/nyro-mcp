import sys
from pathlib import Path
from .server import mcp
from .utils import logger, GREEN, RED, RESET, YELLOW
from .config import settings

# Import tools to ensure they are registered with the mcp instance
from .tools import fs_read
from .tools import fs_write
from .tools import system

def main():
    print(f"{GREEN}NyroMCP - Enhanced File System MCP Server{RESET}")
    print(f"{YELLOW}Please enter the ROOT directory path for this session:{RESET}")
    
    while True:
        try:
            path_str = input(f"{YELLOW}ROOT Path > {RESET}").strip()
            if not path_str:
                continue
            
            p = Path(path_str).resolve()
            if not p.exists():
                print(f"{RED}Error: Path does not exist. Please try again.{RESET}")
                continue
            if not p.is_dir():
                print(f"{RED}Error: Path is not a directory. Please try again.{RESET}")
                continue
                
            # Set the ROOT path in settings
            settings.ROOT = p
            logger.info(f"{GREEN}Root directory configured to: {settings.ROOT}{RESET}")
            break
            
        except KeyboardInterrupt:
            print("\nExiting...")
            sys.exit(0)
        except Exception as e:
            print(f"{RED}Invalid path input: {e}{RESET}")

    logger.info(f"{GREEN}NyroMCP is running with extended toolset...{RESET}")
    try:
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        print(f"\n{GREEN}Server stopped by user.{RESET}")
    except Exception as e:
        logger.critical(f"{RED}FATAL ERROR: FastMCP terminated unexpectedly: {e}{RESET}")

if __name__ == "__main__":
    main()
