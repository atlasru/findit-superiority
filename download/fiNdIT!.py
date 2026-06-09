#!/usr/bin/env python3

import os
import sys
import ctypes
import argparse
import subprocess
import winreg
from pathlib import Path
from typing import Set, List, Dict, Tuple
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

if sys.stdout.isatty():
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    GRAY = "\033[90m"
    WHITE = "\033[97m"
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"
    RESET = "\033[0m"
else:
    GREEN = RED = YELLOW = GRAY = WHITE = CYAN = MAGENTA = RESET = ""

def color_text(text: str, color: str) -> str:
    return f"{color}{text}{RESET}"

def print_border():
    print(color_text("+" + "-" * 51 + "+", CYAN))

def print_row(text: str, color: str = WHITE):
    padded = text.ljust(52)[:52]
    sys.stdout.write(color_text("| ", CYAN))
    sys.stdout.write(color_text(padded, color))
    print(color_text("|", CYAN))

def print_found(msg: str, critical: bool = False):
    if critical:
        print(f"      {color_text('[!!!]', RED)} {color_text(msg, RED)}")
    else:
        print(f"      {color_text('[+]', GREEN)} {msg}")

def print_not_found(msg: str):
    print(f"      {color_text('[-]', GRAY)} {msg}")

def print_warn(msg: str):
    print(f"      {color_text('[!]', YELLOW)} {msg}")

def print_cleaner_evidence(msg: str):
    print(f"      {color_text('[CLEANER]', MAGENTA)} {msg}")

def print_step(step: str, title: str):
    print()
    sys.stdout.write(f"  {color_text(f'[{step}]', CYAN)} ")
    print(color_text(title, WHITE))

def print_divider():
    print(color_text("+" + "-" * 51 + "+", CYAN))

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
    print_row("  fiNdIT! - Superiority Traces Finder v2.1", CYAN)
    print_row("  + cLeanIT! evidence detection", MAGENTA)
    print_row("  for moderation/research only", GRAY)
    print_row("  by d9vh + community patch", GRAY)
    print_divider()
    print_row("")
    print_row("  Searches for:", WHITE)
    for line in [
        "    * Superiority cheat traces",
        "    * cLeanIT! cleaner evidence (beta)",
    ]:
        print_row(line, GRAY)
    print_row("")
    print_row("  [NO DELETIONS -- info only]", RED)
    print_border()
    print()

def is_admin() -> bool:
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def scan_and_find(path: str, pattern: str = "superiority") -> Dict[str, List[str]]:
    found: Dict[str, List[str]] = {"files": [], "folders": []}
    p = Path(path)
    if not p.exists():
        return found
    try:
        for root, dirs, files in os.walk(p, topdown=False):
            root_path = Path(root)
            for f in files:
                if pattern.lower() in f.lower():
                    found["files"].append(str(root_path / f))
            for d in dirs:
                if pattern.lower() in d.lower():
                    found["folders"].append(str(root_path / d))
    except Exception as e:
        print_warn(f"Access error in {path}: {e}")
    return found

def scan_all_paths(scan_paths: Set[str]) -> Tuple[List[str], List[str]]:
    all_files: List[str] = []
    all_folders: List[str] = []
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {executor.submit(scan_and_find, path): path for path in scan_paths}
        for future in as_completed(futures):
            path = futures[future]
            try:
                res = future.result()
                if res["files"]:
                    for f in res["files"]:
                        print_found(f"File: {f}")
                        all_files.append(f)
                if res["folders"]:
                    for d in res["folders"]:
                        print_found(f"Folder: {d}")
                        all_folders.append(d)
            except Exception as e:
                print_warn(f"Scan error for {path}: {e}")
    return all_files, all_folders

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
        winreg.OpenKeyEx(hive_map[hive_str], subkey, 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
        return True
    except:
        return False

def check_autorun_entry() -> bool:
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_READ | winreg.KEY_WOW64_64KEY
        )
        winreg.QueryValueEx(key, "Superiority")
        winreg.CloseKey(key)
        return True
    except:
        return False

def check_usn_journal(drive: str) -> Tuple[bool, bool]:
    if not Path(drive).exists():
        return (False, False)
    try:
        result = subprocess.run(
            ["fsutil", "usn", "queryjournal", drive],
            capture_output=True,
            text=True,
            timeout=8
        )
        out = result.stdout + result.stderr
        if "USN Journal" in out or "USN" in out:
            disabled = "not active" in out.lower() or "no journal" in out.lower() or result.returncode != 0
            return (True, not disabled)
        if result.returncode == 0 and out.strip():
            return (True, True)
        return (False, False)
    except Exception as e:
        print_warn(f"USN check error on {drive}: {e}")
        return (False, False)

def check_event_log(log_name: str) -> Tuple[bool, bool]:
    exists = False
    was_cleared = False
    try:
        result = subprocess.run(
            ["wevtutil", "get-log", log_name],
            capture_output=True,
            text=True,
            timeout=8
        )
        out = result.stdout + result.stderr
        if result.returncode == 0 and ("enabled" in out.lower() or log_name.lower() in out.lower()):
            exists = True

        if exists:
            if log_name == "Security":
                qr = subprocess.run(
                    ["wevtutil", "qe", "Security",
                     "/q:*[System[(EventID=1102)]]",
                     "/c:1", "/rd:true", "/f:text"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                out2 = qr.stdout + qr.stderr
                if "1102" in out2 or "audit log was cleared" in out2.lower():
                    was_cleared = True
            elif log_name == "System":
                qr = subprocess.run(
                    ["wevtutil", "qe", "System",
                     "/q:*[System[(EventID=104)]]",
                     "/c:1", "/rd:true", "/f:text"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if "log was cleared" in (qr.stdout + qr.stderr).lower():
                    was_cleared = True
        return (exists, was_cleared)
    except Exception as e:
        print_warn(f"Event log check error ({log_name}): {e}")
        return (False, False)

def check_recent_python_admin() -> bool:
    try:
        prefetch_dir = Path("C:\\Windows\\Prefetch")
        if not prefetch_dir.exists():
            return False
        cutoff = datetime.now() - timedelta(hours=1)
        for pf_file in prefetch_dir.glob("PYTHON*.pf"):
            if datetime.fromtimestamp(pf_file.stat().st_mtime) > cutoff:
                return True
        return False
    except:
        return False

def check_cleaner_script_files() -> List[str]:
    found: List[str] = []
    possible_names = [
        "cLeanIT!.py", "cLeanIT!.exe",
        "cleanit.py", "CleanIT.py",
        "cleanit.exe", "CleanIT.exe",
    ]
    user_profile = os.environ.get("USERPROFILE", "")
    search_dirs = [
        user_profile + "\\Desktop",
        user_profile + "\\Downloads",
        user_profile + "\\Documents",
        os.environ.get("TEMP", ""),
        os.environ.get("APPDATA", ""),
        os.environ.get("LOCALAPPDATA", ""),
    ]
    for search_dir in search_dirs:
        if not search_dir or not Path(search_dir).exists():
            continue
        for name in possible_names:
            target = Path(search_dir) / name
            if target.exists() and str(target) not in found:
                found.append(str(target))
            try:
                for found_file in Path(search_dir).rglob(name):
                    if str(found_file) not in found:
                        found.append(str(found_file))
            except:
                pass
    return found

def check_mft_timestamp_anomalies() -> bool:
    suspicious = 0
    for drive_letter in "CDEFG":
        drive = f"{drive_letter}:"
        if Path(drive).exists():
            exists, enabled = check_usn_journal(drive)
            if exists and not enabled:
                suspicious += 1
    return suspicious > 0

def check_registry_run_leftover() -> List[str]:
    found_values: List[str] = []
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_READ | winreg.KEY_WOW64_64KEY
        )
        i = 0
        while True:
            try:
                name, data, _ = winreg.EnumValue(key, i)
                if "superior" in name.lower() or "superior" in str(data).lower():
                    found_values.append(f"{name} -> {data}")
                i += 1
            except OSError:
                break
        winreg.CloseKey(key)
    except:
        pass
    return found_values

def check_scheduled_tasks() -> List[str]:
    found: List[str] = []
    try:
        result = subprocess.run(
            ["schtasks", "/query", "/fo", "LIST"],
            capture_output=True,
            text=True,
            timeout=15
        )
        lines = result.stdout.splitlines()
        task_name = ""
        for line in lines:
            if line.startswith("TaskName:"):
                task_name = line.split(":", 1)[1].strip()
            if "superior" in task_name.lower():
                found.append(task_name)
    except:
        pass
    return found

def check_temp_anomaly() -> Tuple[bool, int]:
    temp_dir = os.environ.get("TEMP", "")
    if not temp_dir or not Path(temp_dir).exists():
        return (False, -1)
    try:
        count = len(list(Path(temp_dir).glob("*")))
        return (count < 5, count)
    except:
        return (False, -1)

def check_cleaner_logs() -> List[Tuple[str, List[str]]]:
    results: List[Tuple[str, List[str]]] = []
    user_profile = os.environ.get("USERPROFILE", "")
    temp_dir = os.environ.get("TEMP", "")
    possible_logs = [
        "cleanit_log.txt",
        "cLeanIT_log.txt",
        "superiority_clean.log",
        "cleanit.log",
    ]
    search_roots = [
        user_profile + "\\Desktop",
        user_profile + "\\Downloads",
        temp_dir,
    ]
    for logname in possible_logs:
        for search_root in search_roots:
            if not search_root or not Path(search_root).exists():
                continue
            log_path = Path(search_root) / logname
            if log_path.exists():
                lines: List[str] = []
                try:
                    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
                        lines = [l.strip() for l in f.readlines()[:3] if l.strip()]
                except:
                    pass
                results.append((str(log_path), lines))
    return results

def main():
    parser = argparse.ArgumentParser(description="FindIT! - Superiority Traces Finder")
    parser.add_argument("--quiet", action="store_true", help="Skip banner and prompts")
    args = parser.parse_args()

    admin_mode = is_admin()

    if not args.quiet:
        if not admin_mode:
            print(color_text("  [!] Admin rights recommended for full search (USN/logs).", YELLOW))
            print(color_text("  Press ENTER to continue anyway, Ctrl+C to exit.", GRAY))
            try:
                input()
            except KeyboardInterrupt:
                sys.exit(0)
        print_banner()
        try:
            input(color_text("  Press ENTER to start search...", GRAY))
        except KeyboardInterrupt:
            sys.exit(0)
        print()

    total_found = 0
    cleaner_evidence_count = 0
    critical_evidence: List[str] = []

    print_step("1/6", "Searching Superiority files (parallel)...")
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

    for path in sorted(scan_paths):
        print(f"    -> {path}")

    all_files, all_folders = scan_all_paths(scan_paths)
    total_found += len(all_files) + len(all_folders)

    print_step("2/6", "Searching registry (Superiority)...")
    registry_keys = [
        "HKCU\\Software\\Superiority",
        "HKLM\\Software\\Superiority",
        "HKCU\\Software\\Classes\\superiority",
    ]
    for key in registry_keys:
        if find_registry_key(key):
            print_found(f"Registry key: {key}")
            total_found += 1
        else:
            print_not_found(f"Registry key: {key}")

    if check_autorun_entry():
        print_found("Autorun entry: HKCU\\...\\Run\\Superiority")
        total_found += 1
    else:
        print_not_found("Autorun entry: Superiority")

    run_leftovers = check_registry_run_leftover()
    for rv in run_leftovers:
        print_found(f"Run value: {rv}")
        total_found += 1

    print_step("3/6", "Checking scheduled tasks...")
    tasks = check_scheduled_tasks()
    if tasks:
        for t in tasks:
            print_found(f"Scheduled task: {t}")
            total_found += 1
    else:
        print_not_found("No suspicious scheduled tasks found")

    print_step("4/6", "Checking USN Journal status...")
    for drive_letter in "CDEFG":
        drive = f"{drive_letter}:"
        exists, enabled = check_usn_journal(drive)
        if exists:
            if enabled:
                print_found(f"USN Journal active on {drive}")
                total_found += 1
            else:
                print_cleaner_evidence(f"USN Journal DISABLED on {drive} -- cLeanIT! was used here!")
                cleaner_evidence_count += 2
                critical_evidence.append(f"USN Journal disabled on {drive} (only cLeanIT! does this)")
        else:
            print_not_found(f"USN Journal on {drive}")

    print_step("5/6", "Checking event logs...")
    logs = [
        "Microsoft-Windows-NTFS/Operational",
        "System",
        "Security",
        "Application",
    ]
    for log in logs:
        exists, was_cleared = check_event_log(log)
        if exists:
            print_found(f"Log exists: {log}")
            total_found += 1
            if was_cleared:
                print_cleaner_evidence(f"[WARNING] {log} log was CLEARED! (cLeanIT! behavior)")
                cleaner_evidence_count += 2
                critical_evidence.append(f"Event log {log} was cleared")
        else:
            print_not_found(f"Log {log}: not found")

    print_step("6/6", "Searching for cLeanIT! cleaner evidence...")

    cleaner_files = check_cleaner_script_files()
    if cleaner_files:
        for cf in cleaner_files:
            print_cleaner_evidence(f"cLeanIT! script found: {cf}")
            cleaner_evidence_count += 3
            critical_evidence.append(f"Cleaner file present: {cf}")
    else:
        print_not_found("No cLeanIT! script files found")

    if admin_mode and check_recent_python_admin():
        print_cleaner_evidence("Recent Python execution detected (possible cLeanIT! run)")
        cleaner_evidence_count += 2
        critical_evidence.append("Python executed recently as admin")
    else:
        print_not_found("No recent suspicious Python execution found")

    if check_mft_timestamp_anomalies():
        print_cleaner_evidence("USN Journal missing/disabled -- DEFINITE cleaner usage")
        cleaner_evidence_count += 3

    temp_anomaly, temp_count = check_temp_anomaly()
    if temp_anomaly:
        print_cleaner_evidence(f"Temp directory nearly empty ({temp_count} files) -- unusual for normal system")
        cleaner_evidence_count += 1

    cleaner_logs = check_cleaner_logs()
    for log_path, lines in cleaner_logs:
        print_cleaner_evidence(f"Cleaner log file found: {log_path}")
        cleaner_evidence_count += 2
        critical_evidence.append(f"Cleaner log exists: {log_path}")
        for line in lines:
            print(f"           -> {line[:60]}")

    print()
    print_border()

    if total_found > 0:
        print_row(f"  Superiority traces found: {total_found}", GREEN)
    else:
        print_row("  No direct Superiority traces found.", GRAY)

    if cleaner_evidence_count > 0:
        print_row(f"  cLeanIT! evidence found: {cleaner_evidence_count} points", MAGENTA)
        if cleaner_evidence_count >= 3:
            print_row("  [WARNING] SUSPICIOUS: Cleaner was likely used!", RED)
        print_row("", GRAY)
        for evidence in critical_evidence[:3]:
            print_row(f"  * {evidence[:45]}", YELLOW)
        if len(critical_evidence) > 3:
            print_row(f"  * ... and {len(critical_evidence) - 3} more items", YELLOW)
    else:
        print_row("  No cLeanIT! evidence found.", GRAY)

    print_divider()
    if cleaner_evidence_count >= 3:
        print_row("  VERDICT: Cleaner usage confirmed!", RED)
        print_row("  This behavior is evidence of cheat removal attempt.", RED)
    elif total_found == 0 and cleaner_evidence_count > 0:
        print_row("  VERDICT: Suspicious -- traces removed but cleaner detected.", YELLOW)
    elif total_found > 0:
        print_row("  VERDICT: Cheat detected directly.", RED)
    else:
        print_row("  VERDICT: No evidence found.", GREEN)

    print_row("  No files were deleted -- report only.", CYAN)
    print_border()
    print()

    if cleaner_evidence_count >= 3:
        print(color_text("  ACTION REQUIRED:", RED))
        print(color_text("    This user likely used cLeanIT! to hide Superiority.", WHITE))
        print(color_text("    Share this report with moderators for ban decision.", WHITE))
    elif total_found > 0:
        print(color_text("  ACTION: Cheat detected directly.", RED))
    else:
        print(color_text("  System appears clean.", GREEN))

    print()
    if not args.quiet:
        try:
            input(color_text("  Press ENTER to exit...", GRAY))
        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(color_text("\n  Interrupted by user.", YELLOW))
        sys.exit(0)

