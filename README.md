# Book of Mormon Search and Analysis Tool

This project contains:
- A Windows desktop GUI app (`my_gui.py`)
- An Android mobile app (`mobile_app`) built with BeeWare/Briefcase

## Features
1. Search words or phrases with verse references.
2. Title statistics by book.
3. Pie and line chart views for title usage.

## Tech Stack
- Python 3.14
- Desktop: `customtkinter`, `matplotlib`, `rich`
- Android: BeeWare `toga`, Briefcase, Chaquopy

## Core Files
- `my_gui.py`: desktop GUI entry point
- `list_parser.py`: shared parsing/counting logic
- `mobile_app/app.py`: Android app UI/logic
- `pyproject.toml`: Briefcase app configuration
- `ANDROID_RUNBOOK.md`: stable Android/emulator workflow
- `PLAY_STORE_CHECKLIST.md`: Play Store submission preflight checklist

## Desktop Setup and Run
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python my_gui.py
```

## Desktop EXE Build
```powershell
pyinstaller -y my_gui.spec --distpath dist --workpath build
```

Output:
- `dist\my_gui\my_gui.exe`

## Android Stable Workflow

Use the non-OneDrive workspace for Android builds:
- `C:\dev\Book_of_Mormon_local`

Start emulator (safe mode):
```powershell
powershell -ExecutionPolicy Bypass -File .\run_android_stable.ps1
```

Live patch app (no emulator restart):
```powershell
powershell -ExecutionPolicy Bypass -File .\patch_android_live.ps1
```

Notes:
- Keep the emulator flow in `ANDROID_RUNBOOK.md` as source of truth.
- Current chart rendering uses image output with offline fallback and non-blocking background rendering.

## Play Store Release Packaging

From `C:\dev\Book_of_Mormon_local`:
```powershell
powershell -ExecutionPolicy Bypass -File .\release_playstore_aab.ps1
```

This packages an Android App Bundle (`.aab`) and prints the artifact path + SHA256.

## Play Store Docs in Repo
- `PLAY_STORE_CHECKLIST.md`
- `PLAY_STORE_LISTING_TEMPLATE.md`
- `PRIVACY_POLICY.md`

## Screenshots
<p><img src="images/image1.png" alt="Project image 1" width="900" /></p>
<p><img src="images/image2.png" alt="Project image 2" width="900" /></p>
<p><img src="images/image3.png" alt="Project image 3" width="900" /></p>
<p><img src="images/image4.png" alt="Project image 4" width="900" /></p>
