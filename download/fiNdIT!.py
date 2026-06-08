#!/usr/bin/env python3

import os
import sys
import ctypes
from pathlib import Path
from typing import Set, List, Dict
import winreg

if sys.stdout.isatty():
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    GRAY = "\033[90m"
    WHITE = "\033[97m"
    CYAN = "\033[96m"
    RESET = "\033[0m"
else:
    GREEN = RED = YELLOW = GRAY = WHITE = CYAN = RESET = ""

def color_text(text: str, color: str) -> str:
    return f"{color}{text}{RESET}"

def print_border():
    print(color_text("+" + "-" * 51 + "+", CYAN))

def print_row(text: str, color: str = WHITE):
    padded = text.ljust(52)[:52]
    sys.stdout.write(color_text("| ", CYAN))
    sys.stdout.write(color_text(padded, color))
    print(color_text("|", CYAN))

def print_found(msg: str):
    print(f"      {color_text('[+]', GREEN)} {msg}")

def print_not_found(msg: str):
    print(f"      {color_text('[-]', GRAY)} {msg}")

def print_warn(msg: str):
    print(f"      {color_text('[!]', YELLOW)} {msg}")

def print_step(step: str, title: str):
    print()
    sys.stdout.write(f"  {color_text(f'[{step}]', CYAN)} ")
    print(color_text(title, WHITE))

def print_banner():
    os.system("cls" if os.name == "nt" else "clear")
    ascii_art = r"""
         __ _     __    _    _____  _____  _        
__/\__  / _(_) /\ \ \__| |   \_   \/__   \/ \ __/\__
\    / | |_| |/  \/ / _` |    / /\/  / /\/  / \    /
/_  _\ |  _| / /\  / (_| | /\/ /_   / / /\_/  /_  _\
  \/   |_| |_\_\ \/ \__,_| \____/   \/  \/      \/
"""
    for line in ascii_art.splitlines():
        if line.strip():
            print(color_text(line, YELLOW))
    print_border()
    print_row("  FindIT! - Superiority Traces Finder v1.0", CYAN)
    print_row("  for moderation/research only", GRAY)
    print_row("  by d9vh  ", GRAY)
    print_divider()
    print_row("")
    print_row("  Searches for Superiority-related traces:", WHITE)
    for line in [
        "    * AppData (Roaming / Local)",
        "    * Temp, Program Files, ProgramData",
        "    * Documents, Downloads, Desktop",
        "    * Windows Registry",
        "    * Autorun entries",
        "    * USN Journal (NTFS traces)",
        "    * Windows Event Logs",
    ]:
        print_row(line, GRAY)
    print_row("")
    print_row("  [NO DELETIONS — info only]", RED)
    print_border()
    print()

def print_divider():
    print(color_text("+" + "-" * 51 + "+", CYAN))

def is_admin() -> bool:
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def scan_and_find(path: str, pattern: str = "superiority") -> Dict[str, List[str]]:
    found = {"files": [], "folders": []}
    path = Path(path)
    if not path.exists():
        return found
    try:
        for root, dirs, files in os.walk(path, topdown=False):
            root_path = Path(root)
            for f in files:
                if pattern.lower() in f.lower():
                    file_path = root_path / f
                    found["files"].append(str(file_path))
            for d in dirs:
                if pattern.lower() in d.lower():
                    dir_path = root_path / d
                    found["folders"].append(str(dir_path))
    except Exception as e:
        print_warn(f"Access error in {path}: {e}")
    return found

def find_registry_key(key_path: str) -> bool:
    try:
        parts = key_path.split('\\', 1)
        hive_str = parts[0]
        subkey = parts[1] if len(parts) > 1 else ""
        hive_map = {
            "HKCU": winreg.HKEY_CURRENT_USER,
            "HKLM": winreg.HKEY_LOCAL_MACHINE,
        }
        if hive_str not in hive_map:
            return False
        hive = hive_map[hive_str]
        winreg.OpenKeyEx(hive, subkey, 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
        return True
    except:
        return False

def check_autorun_entry() -> bool:
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Software\Microsoft\Windows\CurrentVersion\Run",
                             0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
        winreg.QueryValueEx(key, "Superiority")
        winreg.CloseKey(key)
        return True
    except:
        return False

def check_usn_journal(drive: str) -> bool:
    if not Path(drive).exists():
        return False
    try:
        result = os.popen(f'fsutil usn queryjournal {drive} 2>nul').read()
        return "USN Journal" in result
    except:
        return False

def check_event_log(log_name: str) -> bool:
    try:
        result = os.popen(f'wevtutil get-log "{log_name}" 2>nul').read()
        return "enabled" in result.lower() or log_name in result
    except:
        return False

def main():
    if not is_admin():
        print(color_text("  [!] Admin rights recommended for full search (USN/logs).", YELLOW))
        print(color_text("  Press ENTER to continue anyway, Ctrl+C to exit.", GRAY))
        input()

    print_banner()

    input(color_text("  Press ENTER to start search...", GRAY))
    print()

    total_found = 0

    print_step("1/4", "Searching file system...")

    scan_paths: Set[str] = set()
    for env in ["APPDATA", "LOCALAPPDATA", "TEMP", "ProgramFiles", "ProgramFiles(x86)", "ProgramData"]:
        p = os.environ.get(env)
        if p and Path(p).exists():
            scan_paths.add(p)

    user = os.environ.get("USERPROFILE", "")
    for sub in ["Documents", "Downloads", "Desktop"]:
        p = Path(user) / sub
        if p.exists():
            scan_paths.add(str(p))

    all_files = []
    all_folders = []

    for path in sorted(scan_paths):
        print(f"    -> {path}")
        res = scan_and_find(path)
        if res["files"]:
            for f in res["files"]:
                print_found(f"File: {f}")
                total_found += 1
                all_files.append(f)
        if res["folders"]:
            for d in res["folders"]:
                print_found(f"Folder: {d}")
                total_found += 1
                all_folders.append(d)

    print_step("2/4", "Searching registry...")
    registry_keys = [
        "HKCU\\Software\\Superiority",
        "HKLM\\Software\\Superiority",
        "HKCU\\Software\\Classes\\superiority"
    ]
    for key in registry_keys:
        if find_registry_key(key):
            print_found(f"Registry key: {key}")
            total_found += 1
        else:
            print_not_found(f"Registry key: {key}")

    if check_autorun_entry():
        print_found("Autorun entry: HKCU\...\Run\Superiority")
        total_found += 1
    else:
        print_not_found("Autorun entry: Superiority")

    print_step("3/4", "Checking USN Journal...")
    for drive in "CDEFG":
        if check_usn_journal(f"{drive}:"):
            print_found(f"USN Journal active on {drive}:")
            total_found += 1
        else:
            print_not_found(f"USN Journal on {drive}:")

    print_step("4/4", "Checking event logs...")
    logs = ["Microsoft-Windows-NTFS/Operational", "System", "Security", "Application"]
    for log in logs:
        if check_event_log(log):
            print_found(f"Log exists: {log}")
            total_found += 1
        else:
            print_not_found(f"Log {log}: not found or empty")

    print()
    print_border()
    print_row(f"  Search completed. Traces found: {total_found}", GREEN if total_found > 0 else GRAY)
    print_row("  No files were deleted — report only.", CYAN)
    print_border()
    print()
    input(color_text("  Press ENTER to exit...", GRAY))

if __name__ == "__main__":
    main()