import os
from pathlib import Path
import base64
import shutil
import subprocess
import time
import logging
import hashlib
import zipfile
# Závislost 'psutil' byla odstraněna, protože systémové nástroje jsou pryč.

# Import FastMCP frameworku
from mcp.server.fastmcp import FastMCP

# --- Nastavení barev a loggeru (beze změny) ---
# Tato část zůstává stejná, protože je dobře napsaná.
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

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(CustomFormatter())
logger.propagate = False
logger.addHandler(handler)

class Error(Exception):
    """Vlastní výjimka pro specifické chyby nástrojů."""
    pass

# --- Základní konfigurace ---
# Cesta k pracovnímu adresáři projektu. Všechny operace jsou omezeny na tento adresář.
ROOT = Path(r"C:\Users\wNyro_\Documents\Projects\CustomMC\1.21.9-src").resolve()
mcp = FastMCP(name="mcp_fs_enhanced")

def safe_path(p: Path) -> Path:
    """Zajišťuje, že cesta je uvnitř definovaného ROOT adresáře. Kritické pro bezpečnost."""
    p = p.resolve()
    if not str(p).startswith(str(ROOT)):
        logger.error(f"{RED}SECURITY ERROR: Pokus o přístup mimo ROOT adresář: {p}{RESET}")
        raise Error("outside_root")
    return p

# --- NÁSTROJE PRO MANIPULACI SE SOUBOROVÝM SYSTÉMEM ---

# --- Adresářové operace ---

@mcp.tool()
def list_dir(path: str = "."):
    """Vypíše soubory a adresáře v zadané cestě s detaily."""
    logger.info(f"Vypisuji obsah adresáře: {path}")
    try:
        p = safe_path(ROOT / path)
        if not p.is_dir():
            raise Error("not_dir: Cesta neexistuje nebo není adresář")

        items = []
        for c in sorted(p.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
             stat = c.stat()
             items.append({
                 "name": c.name,
                 "path": str(c.relative_to(ROOT)),
                 "is_dir": c.is_dir(),
                 "size": stat.st_size if c.is_file() else None,
                 "last_modified": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stat.st_mtime))
             })

        logger.info(f"{GREEN}ÚSPĚCH: Adresář '{path}' vypsán. Počet položek: {len(items)}.{RESET}")
        return {"items": items}
    except Error as e:
        logger.error(f"{RED}Chyba při výpisu '{path}': {e}{RESET}")
        raise
    except Exception as e:
        logger.error(f"{RED}Neočekávaná chyba při výpisu '{path}': {type(e).__name__} - {e}{RESET}")
        raise Error(f"internal_error: {e}")

@mcp.tool()
def create_dir(path: str):
    """Vytvoří adresář, včetně všech potřebných nadřazených adresářů."""
    logger.info(f"Pokouším se vytvořit adresář: {path}")
    try:
        p = safe_path(ROOT / path)
        p.mkdir(parents=True, exist_ok=True)
        logger.info(f"{BLUE}ÚSPĚCH: Adresář '{path}' vytvořen (nebo již existoval).{RESET}")
        return {"status": "created_or_exists"}
    except Error as e:
        logger.error(f"{RED}Chyba při vytváření adresáře '{path}': {e}{RESET}")
        raise
    except Exception as e:
        logger.error(f"{RED}Neočekávaná chyba při vytváření adresáře: {type(e).__name__} - {e}{RESET}")
        raise Error(f"internal_error: {e}")

@mcp.tool()
def get_dir_size(path: str = "."):
    """Vypočítá celkovou velikost adresáře a veškerého jeho obsahu rekurzivně."""
    logger.info(f"Vypočítávám velikost adresáře '{path}'...")
    try:
        p = safe_path(ROOT / path)
        if not p.is_dir():
            raise Error("not_dir: Cesta není adresář")

        total_size = sum(f.stat().st_size for f in p.glob('**/*') if f.is_file())

        logger.info(f"{GREEN}ÚSPĚCH: Celková velikost '{path}' je {total_size} bytů.{RESET}")
        return {"path": path, "total_size_bytes": total_size}
    except Error as e:
        logger.error(f"{RED}Chyba při výpočtu velikosti '{path}': {e}{RESET}")
        raise
    except Exception as e:
        logger.error(f"{RED}Neočekávaná chyba při výpočtu velikosti: {type(e).__name__} - {e}{RESET}")
        raise Error(f"internal_error: {e}")

@mcp.tool()
def rename_dir(src_path: str, new_name: str):
    """Přejmenuje adresář. Nové jméno nesmí obsahovat cestu."""
    logger.info(f"Pokouším se přejmenovat adresář '{src_path}' na '{new_name}'")
    try:
        if '/' in new_name or '\\' in new_name:
            raise Error("invalid_name: Nové jméno nesmí obsahovat oddělovače cesty.")

        s = safe_path(ROOT / src_path)
        if not s.is_dir():
            raise Error("not_dir: Zdrojová cesta není adresář.")

        d = s.resolve().parent / new_name
        if d.exists():
            raise Error("already_exists: Cíl s tímto jménem již existuje.")

        s.rename(d)
        logger.info(f"{GREEN}ÚSPĚCH: Adresář přejmenován z '{src_path}' na '{d.relative_to(ROOT)}'.{RESET}")
        return {"status": "renamed", "new_path": str(d.relative_to(ROOT))}
    except Error as e:
        logger.error(f"{RED}Chyba při přejmenování adresáře '{src_path}': {e}{RESET}")
        raise
    except Exception as e:
        logger.error(f"{RED}Neočekávaná chyba při přejmenování adresáře: {type(e).__name__} - {e}{RESET}")
        raise Error(f"internal_error: {e}")


# --- Operace se soubory (čtení, zápis, modifikace) ---

@mcp.tool()
def read_file(path: str, offset: int = 0, length: int = 2_000_000):
    """Čte obsah souboru, buď jako text nebo jako base64 kódovaná binární data."""
    logger.info(f"Pokouším se číst soubor: {path} (offset: {offset}, délka: {length})")
    try:
        p = safe_path(ROOT / path)
        if not p.is_file():
            raise Error("not_file: Soubor nenalezen")

        # Rozšířená bezpečnostní kontrola
        if p.suffix.lower() in {".pem", ".key", ".pfx", ".sqlite", ".db", ".p12"}:
            logger.error(f"{RED}Blokovaný soubor kvůli příponě: {path}{RESET}")
            raise Error("blocked_ext: Přípona je z bezpečnostních důvodů blokována")

        with open(p, "rb") as fh:
            fh.seek(offset)
            data = fh.read(length)

        try:
            content = data.decode("utf-8")
            logger.info(f"{GREEN}ÚSPĚCH: Soubor '{path}' přečten jako text. Přečteno bajtů: {len(data)}{RESET}")
            return {"is_text": True, "content": content, "offset": offset, "length": len(data), "file_size": p.stat().st_size}
        except UnicodeDecodeError:
            content_b64 = base64.b64encode(data).decode("ascii")
            logger.info(f"{GREEN}ÚSPĚCH: Soubor '{path}' přečten jako binární (B64). Přečteno bajtů: {len(data)}{RESET}")
            return {"is_text": False, "content_b64": content_b64, "offset": offset, "length": len(data), "file_size": p.stat().st_size}

    except Error as e:
        logger.error(f"{RED}Chyba při čtení '{path}': {e}{RESET}")
        raise
    except Exception as e:
        logger.error(f"{RED}Neočekávaná chyba při čtení '{path}': {type(e).__name__} - {e}{RESET}")
        raise Error(f"internal_error: {e}")

@mcp.tool()
def write_file(path: str, content: str, append: bool = False):
    """Zapíše nebo připojí textový obsah do souboru."""
    mode_str = 'připojení' if append else 'přepsání'
    logger.info(f"Pokouším se zapsat do souboru: {path} (režim: {mode_str})")
    try:
        p = safe_path(ROOT / path)
        p.parent.mkdir(parents=True, exist_ok=True)
        mode = "a" if append else "w"
        with open(p, mode, encoding="utf-8") as fh:
            chars_written = fh.write(content)
        logger.info(f"{GREEN}ÚSPĚCH: Zapsáno {chars_written} znaků do souboru '{path}' v režimu '{mode_str}'.{RESET}")
        return {"status": "ok", "chars_written": chars_written}
    except Error as e:
        logger.error(f"{RED}Chyba při zápisu do '{path}': {e}{RESET}")
        raise
    except Exception as e:
        logger.error(f"{RED}Neočekávaná chyba při zápisu do '{path}': {type(e).__name__} - {e}{RESET}")
        raise Error(f"internal_error: {e}")

@mcp.tool()
def create_file(path: str, content: str = ""):
    """Vytvoří nový soubor s volitelným počátečním obsahem. Selže, pokud soubor již existuje."""
    logger.info(f"Pokouším se vytvořit nový soubor: {path}")
    try:
        p = safe_path(ROOT / path)
        if p.exists():
            raise Error("already_exists: Soubor na této cestě již existuje")

        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")

        logger.info(f"{GREEN}ÚSPĚCH: Soubor '{path}' vytvořen s {len(content)} znaky.{RESET}")
        return {"status": "created", "path": str(p.relative_to(ROOT))}
    except Error as e:
        logger.error(f"{RED}Chyba při vytváření souboru '{path}': {e}{RESET}")
        raise
    except Exception as e:
        logger.error(f"{RED}Neočekávaná chyba při vytváření souboru: {type(e).__name__} - {e}{RESET}")
        raise Error(f"internal_error: {e}")

@mcp.tool()
def rename_file(src_path: str, new_name: str):
    """Přejmenuje soubor. Nové jméno nesmí obsahovat cestu."""
    logger.info(f"Pokouším se přejmenovat soubor '{src_path}' na '{new_name}'")
    try:
        if '/' in new_name or '\\' in new_name:
            raise Error("invalid_name: Nové jméno nesmí obsahovat oddělovače cesty.")

        s = safe_path(ROOT / src_path)
        if not s.is_file():
            raise Error("not_file: Zdrojová cesta není soubor.")

        d = s.resolve().parent / new_name
        if d.exists():
            raise Error("already_exists: Cíl s tímto jménem již existuje.")

        s.rename(d)
        logger.info(f"{GREEN}ÚSPĚCH: Soubor přejmenován z '{src_path}' na '{d.relative_to(ROOT)}'.{RESET}")
        return {"status": "renamed", "new_path": str(d.relative_to(ROOT))}
    except Error as e:
        logger.error(f"{RED}Chyba při přejmenování souboru '{src_path}': {e}{RESET}")
        raise
    except Exception as e:
        logger.error(f"{RED}Neočekávaná chyba při přejmenování souboru: {type(e).__name__} - {e}{RESET}")
        raise Error(f"internal_error: {e}")

@mcp.tool()
def replace_in_file(path: str, find_text: str, replace_with: str, replace_all: bool = False):
    """Nahradí výskyty řetězce v textovém souboru. Lze nahradit jen první nebo všechny."""
    op_type = "všech výskytů" if replace_all else "prvního výskytu"
    logger.info(f"Pokouším se o nahrazení {op_type} textu v souboru: {path}")
    try:
        p = safe_path(ROOT / path)
        if not p.is_file():
            raise Error("not_file: Soubor nenalezen")

        content = p.read_text(encoding='utf-8')
        
        replaces_count = content.count(find_text)
        if replaces_count == 0:
            raise Error("not_found: Hledaný text nebyl v souboru nalezen.")

        if replace_all:
            new_content = content.replace(find_text, replace_with)
        else:
            new_content = content.replace(find_text, replace_with, 1)
            replaces_count = 1

        p.write_text(new_content, encoding='utf-8')
        
        logger.info(f"{BLUE}ÚSPĚCH: Nahrazeno {replaces_count} výskytů v souboru '{path}'.{RESET}")
        return {"status": "replaced", "replaces_count": replaces_count}
    except Error as e:
        logger.error(f"{RED}Chyba při nahrazování textu v '{path}': {e}{RESET}")
        raise
    except UnicodeDecodeError:
        raise Error("decode_error: Soubor není platný textový soubor (UTF-8).")
    except Exception as e:
        logger.error(f"{RED}Neočekávaná chyba při nahrazování textu: {type(e).__name__} - {e}{RESET}")
        raise Error(f"internal_error: {e}")
        
@mcp.tool()
def insert_into_file(path: str, content_to_insert: str, at_line: int):
    """Vloží textový obsah na specifický řádek v souboru. Řádky jsou číslovány od 1."""
    logger.info(f"Vkládám text do souboru '{path}' na řádek {at_line}")
    try:
        p = safe_path(ROOT / path)
        if not p.is_file():
            raise Error("not_file: Soubor nenalezen")
        
        # Načtení řádků se zachováním konců řádků
        lines = p.read_text(encoding='utf-8').splitlines(True)
        
        if at_line < 1:
            at_line = 1
        
        if at_line > len(lines):
             # Přidání na konec s novým řádkem, pokud je potřeba
            if lines and not lines[-1].endswith('\n'):
                lines[-1] += '\n'
            lines.append(content_to_insert)
        else:
            # Vložení na zadaný řádek (index je o 1 menší)
            lines.insert(at_line - 1, content_to_insert + '\n')
            
        p.write_text("".join(lines), encoding='utf-8')
        
        logger.info(f"{GREEN}ÚSPĚCH: Obsah byl vložen do '{path}' na řádek {at_line}.{RESET}")
        return {"status": "inserted", "line_number": at_line}
    except Error as e:
        logger.error(f"{RED}Chyba při vkládání do souboru '{path}': {e}{RESET}")
        raise
    except UnicodeDecodeError:
        raise Error("decode_error: Soubor není platný textový soubor (UTF-8).")
    except Exception as e:
        logger.error(f"{RED}Neočekávaná chyba při vkládání do souboru: {type(e).__name__} - {e}{RESET}")
        raise Error(f"internal_error: {e}")

@mcp.tool()
def touch_file(path: str):
    """Vytvoří prázdný soubor, pokud neexistuje, nebo aktualizuje jeho časovou značku."""
    logger.info(f"Provádím 'touch' na soubor: {path}")
    try:
        p = safe_path(ROOT / path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.touch()
        logger.info(f"{GREEN}ÚSPĚCH: Soubor '{path}' byl 'touchnut'.{RESET}")
        return {"status": "touched"}
    except Exception as e:
        logger.error(f"{RED}Neočekávaná chyba při operaci touch: {type(e).__name__} - {e}{RESET}")
        raise Error(f"internal_error: {e}")


# --- Vyhledávací a informační operace ---

@mcp.tool()
def find_files(pattern: str, base_path: str = "."):
    """Najde soubory rekurzivně odpovídající glob vzoru."""
    logger.info(f"Hledám soubory odpovídající vzoru '{pattern}' v '{base_path}'")
    try:
        p = safe_path(ROOT / base_path)
        if not p.is_dir():
            raise Error("not_dir: Základní cesta není adresář")

        found_paths = [str(f.relative_to(ROOT)) for f in p.rglob(pattern) if f.is_file()]

        logger.info(f"{BLUE}ÚSPĚCH: Nalezeno {len(found_paths)} souborů odpovídajících '{pattern}'.{RESET}")
        return {"found_files": found_paths, "count": len(found_paths)}
    except Error as e:
        logger.error(f"{RED}Chyba při hledání souborů: {e}{RESET}")
        raise
    except Exception as e:
        logger.error(f"{RED}Neočekávaná chyba při hledání souborů: {type(e).__name__} - {e}{RESET}")
        raise Error(f"internal_error: {e}")

@mcp.tool()
def search_in_files(search_text: str, glob_pattern: str = "*", base_path: str = "."):
    """Prohledá obsah souborů (odpovídajících vzoru) a vrátí řádky, kde byl text nalezen."""
    logger.info(f"Prohledávám soubory '{glob_pattern}' v '{base_path}' pro text '{search_text}'")
    try:
        p = safe_path(ROOT / base_path)
        results = {}
        files_searched = 0
        
        for file_path in p.rglob(glob_pattern):
            if file_path.is_file():
                files_searched += 1
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line_num, line in enumerate(f, 1):
                            if search_text in line:
                                relative_path_str = str(file_path.relative_to(ROOT))
                                if relative_path_str not in results:
                                    results[relative_path_str] = []
                                results[relative_path_str].append({"line_number": line_num, "line_content": line.strip()})
                except (UnicodeDecodeError, IOError):
                    # Ignorovat binární soubory nebo soubory, které nelze číst
                    continue
        
        logger.info(f"{BLUE}ÚSPĚCH: Prohledáno {files_searched} souborů. Nálezy v {len(results)} souborech.{RESET}")
        return {"search_results": results, "files_with_matches": len(results)}
    except Exception as e:
        logger.error(f"{RED}Neočekávaná chyba při prohledávání souborů: {type(e).__name__} - {e}{RESET}")
        raise Error(f"internal_error: {e}")

@mcp.tool()
def get_file_stat(path: str):
    """Získá metadata o souboru nebo adresáři (velikost, data atd.)."""
    logger.info(f"Získávám statistiky pro: {path}")
    try:
        p = safe_path(ROOT / path)
        if not p.exists():
            raise Error("not_exist: Cesta neexistuje")

        stat = p.stat()
        def format_time(t):
            return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t))

        result = {
            "path": str(p.relative_to(ROOT)),
            "size": stat.st_size,
            "is_dir": p.is_dir(),
            "last_modified": format_time(stat.st_mtime),
            "created": format_time(stat.st_ctime)
        }

        logger.info(f"{BLUE}ÚSPĚCH: Statistiky pro '{path}' získány (Velikost: {result['size']} bytů).{RESET}")
        return result
    except Error as e:
        logger.error(f"{RED}Chyba při získávání statistik pro '{path}': {e}{RESET}")
        raise
    except Exception as e:
        logger.error(f"{RED}Neočekávaná chyba při získávání statistik: {type(e).__name__} - {e}{RESET}")
        raise Error(f"internal_error: {e}")

@mcp.tool()
def calculate_hash(path: str, algorithm: str = "sha256"):
    """Vypočítá hash souboru pomocí zadaného algoritmu."""
    logger.info(f"Vypočítávám {algorithm} hash pro soubor: {path}")
    try:
        if algorithm not in hashlib.algorithms_available:
            raise Error(f"invalid_algorithm: Algoritmus {algorithm} není podporován")

        p = safe_path(ROOT / path)
        if not p.is_file():
            raise Error("not_file: Soubor nenalezen")

        hasher = hashlib.new(algorithm)
        blocksize = 65536
        with open(p, 'rb') as afile:
            buf = afile.read(blocksize)
            while len(buf) > 0:
                hasher.update(buf)
                buf = afile.read(blocksize)

        result_hash = hasher.hexdigest()
        logger.info(f"{BLUE}ÚSPĚCH: Vypočítán {algorithm} hash pro '{path}'.{RESET}")
        return {"hash": result_hash, "algorithm": algorithm}
    except Error as e:
        logger.error(f"{RED}Chyba při výpočtu hashe pro '{path}': {e}{RESET}")
        raise
    except Exception as e:
        logger.error(f"{RED}Neočekávaná chyba při výpočtu hashe: {type(e).__name__} - {e}{RESET}")
        raise Error(f"internal_error: {e}")

# --- Obecné operace (kopírování, přesun, mazání) ---

@mcp.tool()
def delete_path(path: str):
    """Smaže soubor nebo adresář (rekurzivně)."""
    logger.info(f"Pokouším se smazat cestu: {path}")
    try:
        p = safe_path(ROOT / path)
        if p == ROOT:
            raise Error("cannot_delete_root: Není povoleno mazat kořenový adresář.")

        if p.is_file():
            p.unlink()
            status = "deleted_file"
            logger.info(f"{GREEN}ÚSPĚCH: Soubor '{path}' smazán.{RESET}")
        elif p.is_dir():
            shutil.rmtree(p)
            status = "deleted_dir"
            logger.info(f"{GREEN}ÚSPĚCH: Adresář '{path}' rekurzivně smazán.{RESET}")
        else:
            raise Error("not_exist: Cesta neexistuje")

        return {"status": status}
    except Error as e:
        logger.error(f"{RED}Chyba při mazání '{path}': {e}{RESET}")
        raise
    except Exception as e:
        logger.error(f"{RED}Neočekávaná chyba při mazání '{path}': {type(e).__name__} - {e}{RESET}")
        raise Error(f"internal_error: {e}")

@mcp.tool()
def move_path(src: str, dst: str):
    """Přesune soubor nebo adresář ze zdroje do cíle."""
    logger.info(f"Pokouším se přesunout: z '{src}' do '{dst}'")
    try:
        s = safe_path(ROOT / src)
        d = safe_path(ROOT / dst)
        if not s.exists():
            raise Error("not_exist: Zdrojová cesta neexistuje.")
        
        shutil.move(str(s), str(d))
        logger.info(f"{GREEN}ÚSPĚCH: Přesun z '{src}' do '{dst}' dokončen.{RESET}")
        return {"status": "moved"}
    except Error as e:
        logger.error(f"{RED}Chyba při přesouvání '{src}' do '{dst}': {e}{RESET}")
        raise
    except Exception as e:
        logger.error(f"{RED}Neočekávaná chyba při přesouvání: {type(e).__name__} - {e}{RESET}")
        raise Error(f"internal_error: {e}")

@mcp.tool()
def copy_path(src: str, dst: str):
    """Zkopíruje soubor nebo adresář ze zdroje do cíle."""
    logger.info(f"Pokouším se kopírovat: z '{src}' do '{dst}'")
    try:
        s = safe_path(ROOT / src)
        d = safe_path(ROOT / dst)
        if not s.exists():
            raise Error("not_exist: Zdrojová cesta neexistuje.")

        if s.is_file():
            shutil.copy2(str(s), str(d))
            status = "copied_file"
        elif s.is_dir():
            shutil.copytree(str(s), str(d))
            status = "copied_dir"
        else:
             raise Error("not_file_or_dir: Zdroj není soubor ani adresář.")

        logger.info(f"{GREEN}ÚSPĚCH: Kopírování z '{src}' do '{dst}' dokončeno.{RESET}")
        return {"status": status}
    except Error as e:
        logger.error(f"{RED}Chyba při kopírování '{src}' do '{dst}': {e}{RESET}")
        raise
    except Exception as e:
        logger.error(f"{RED}Neočekávaná chyba při kopírování: {type(e).__name__} - {e}{RESET}")
        raise Error(f"internal_error: {e}")
        
# --- Archivace ---
        
@mcp.tool()
def zip_files(archive_path: str, files_to_add: list[str], base_dir: str = "."):
    """Vytvoří zip archiv ze seznamu souborů nebo adresářů."""
    logger.info(f"Vytvářím zip archiv '{archive_path}' z {len(files_to_add)} položek.")
    try:
        archive_p = safe_path(ROOT / archive_path)
        base_p = safe_path(ROOT / base_dir)

        with zipfile.ZipFile(archive_p, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in files_to_add:
                full_path = safe_path(base_p / file_path)
                if not full_path.exists():
                    logger.warning(f"Položka '{file_path}' neexistuje a bude přeskočena.")
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

        logger.info(f"{GREEN}ÚSPĚCH: Archiv '{archive_path}' vytvořen.{RESET}")
        return {"status": "created", "archive_path": str(archive_p.relative_to(ROOT))}
    except Error as e:
        logger.error(f"{RED}Chyba při vytváření zip archivu: {e}{RESET}")
        raise
    except Exception as e:
        logger.error(f"{RED}Neočekávaná chyba při zipování: {type(e).__name__} - {e}{RESET}")
        raise Error(f"internal_error: {e}")

@mcp.tool()
def unzip_file(archive_path: str, extract_to_dir: str):
    """Rozbalí zip archiv do zadaného adresáře."""
    logger.info(f"Rozbaluji archiv '{archive_path}' do '{extract_to_dir}'")
    try:
        archive_p = safe_path(ROOT / archive_path)
        extract_p = safe_path(ROOT / extract_to_dir)
        
        if not archive_p.is_file():
            raise Error("not_file: Archiv nenalezen")
        extract_p.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(archive_p, 'r') as zipf:
            zipf.extractall(extract_p)
            
        logger.info(f"{GREEN}ÚSPĚCH: Archiv rozbalen do '{extract_to_dir}'.{RESET}")
        return {"status": "extracted"}
    except zipfile.BadZipFile:
        raise Error("bad_zip_file: Soubor není platný zip archiv.")
    except Error as e:
        logger.error(f"{RED}Chyba při rozbalování archivu: {e}{RESET}")
        raise
    except Exception as e:
        logger.error(f"{RED}Neočekávaná chyba při rozbalování: {type(e).__name__} - {e}{RESET}")
        raise Error(f"internal_error: {e}")

# --- Spouštění externích příkazů ---

@mcp.tool()
def run_command(cmd: str, cwd: str = ".", timeout: int = 120):
    """Spustí shell příkaz v zadaném pracovním adresáři s časovým limitem."""
    logger.info(f"Pokouším se spustit příkaz: {cmd} v '{cwd}' s timeoutem {timeout}s")
    try:
        work_dir = safe_path(ROOT / cwd)
        if not work_dir.is_dir():
            raise Error("not_dir: Pracovní adresář neexistuje")

        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=False, cwd=str(work_dir), timeout=timeout, encoding='utf-8', errors='ignore')
        
        if result.returncode != 0:
            logger.warning(f"Příkaz skončil s chybou (RC: {result.returncode}). STDERR: {result.stderr.strip()[:200]}...")
            
        logger.info(f"{GREEN}ÚSPĚCH: Příkaz proveden (RC: {result.returncode}).{RESET}")
        
        return {"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode}
    except subprocess.TimeoutExpired as e:
        logger.error(f"{RED}Příkaz '{cmd}' vypršel po {timeout} sekundách.{RESET}")
        return {"stdout": e.stdout, "stderr": e.stderr, "returncode": -1, "error": "timeout"}
    except Exception as e:
        logger.error(f"{RED}Neočekávaná chyba při spouštění příkazu '{cmd}': {type(e).__name__} - {e}{RESET}")
        raise Error(f"internal_error: {e}")


# --- Spouštěcí blok ---
if __name__ == "__main__":
    logger.info(f"{GREEN}NyroMCP běží s vylepšenou sadou nástrojů pro práci se soubory...{RESET}")
    try:
        mcp.run(transport="stdio")
    except Exception as e:
        logger.critical(f"{RED}FATÁLNÍ CHYBA: FastMCP byl neočekávaně ukončen: {e}{RESET}")