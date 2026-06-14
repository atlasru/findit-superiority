# fiNdIT! — Superiority Traces Finder

Forensic detection tool for Rust game server moderation.
Scans Windows systems for **Superiority** cheat artifacts and **cLeanIT!** cleaner evidence.
Read-only — no files are modified or deleted.

---

## Download

| Version | Link | Requirements |
|---------|------|--------------|
| .exe (recommended) | [fiNdIT!.exe — Releases](https://github.com/atlasru/findit-superiority/releases/latest) | Windows 10/11, no Python needed |
| .py (source) | [fiNdIT!.py](download/fiNdIT!.py) | Python 3.8+ |

---

## Usage

**Run as Administrator** for full results (USN Journal + Event Log access).

```
python "fiNdIT!.py"
```

Save report automatically:
```
python "fiNdIT!.py" --log report.txt
```

Skip banner (for scripted use):
```
python "fiNdIT!.py" --quiet
```

At scan end, you will be prompted to save the report to Desktop as `.txt` for ban evidence submission.

---

## What it checks

| Category | Details |
|----------|---------|
| File system | AppData, LocalAppData, Temp, ProgramFiles, ProgramData, Documents, Downloads, Desktop |
| Registry | `HKCU\Software\Superiority`, `HKLM\Software\Superiority`, autorun entries, AppCompatFlags |
| Execution traces | Prefetch (`SUPERIORITY*.pf`), UserAssist (ROT13 decoded), Recent shortcuts, RecentDocs |
| USN Journal | Status check on C: D: E: F: G: — disabled journal = cleaner evidence |
| Event Logs | System, Security, Application, NTFS/Operational — checks for clear events (1102/104) |
| Cleaner detection | cLeanIT! script files, cleaner logs, Windows Defender support logs |
| System info | PC name, username, HWID, OS version, region, country code — included in report |

---

## Example output

```
+---------------------------------------------------+
|   FindIT! - Superiority Traces Finder v2.3        |
|   + cLeanIT! evidence detection                   |
+---------------------------------------------------+

  [3/7] Searching execution traces...
      [!!!] Prefetch: SUPERIORITY.EXE-AB1C2D3E.pf (last run: 2026-06-01 18:42:11)
         >> Windows creates Prefetch files every time a program runs.
         >> This proves the cheat executable was launched on this PC.
         >> Prefetch survives file deletion -- cannot be faked.
      [!!!] UserAssist: C:\Users\user\Desktop\Superiority.exe
         >> UserAssist tracks every program opened via Explorer.
         >> Stored in registry encoded ROT13. Survives file deletion.

  [CLEANER] USN Journal DISABLED on C: -- cLeanIT! was used here!
         >> USN Journal is always active by default on Windows.
         >> Only cLeanIT! or manual tampering disables it.

+---------------------------------------------------+
|   Superiority traces found: 4                     |
|   cLeanIT! evidence found: 5 points               |
|   VERDICT: Cheat + cleaner usage confirmed!       |
+---------------------------------------------------+
```

---

## Report file

The `.txt` report includes:
- Full scan output with all detections and `>>` explanations
- System info: PC name, HWID, region, OS version
- Final verdict

Attach the report as evidence when submitting a ban request.

---

## Requirements

- Windows 10 / 11
- Administrator rights (recommended)
- Python 3.8+ (`.py` version only)

---

## Build from source

```
pip install pyinstaller
pyinstaller --onefile --icon=icon.ico -n "fiNdIT!" "fiNdIT!.py"
```

---

## Notes

- **Antivirus may flag the `.exe`** — false positive due to PyInstaller packaging and system scan nature. Source code is available for verification.
- **No admin rights** — basic file and registry scan still works, USN Journal and Event Log checks will be skipped.
- **No traces found** — user may not have Superiority installed, or used cLeanIT! to remove evidence. Check the cleaner evidence section of the report.

---

## License

Free for moderation, research, and educational use.
Commercial use prohibited without written permission from d9vh.
Forks must credit the original author. See [LICENSE](LICENSE) for full terms.

---

*by d9vh & contributors — for moderation and research use only*
