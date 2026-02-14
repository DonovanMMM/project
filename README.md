# Book of Mormon Search and Analysis Tool

Desktop GUI app for searching and analyzing references to Jesus Christ in the Book of Mormon.

## Features
1. Pie chart of the most common selected titles of Christ.
2. Line chart showing where a selected title appears across books.
3. Text search for any word or phrase with verse references.
4. Missing dependency prompt in the executable, with optional automatic install.

## Tech Stack
- Python 3.14
- `customtkinter` for GUI
- `matplotlib` for charts
- `rich` for parser progress output
- `ctypes` + Tkinter window handling (Windows title bar/icon behavior)

## Requirements
- Windows 10/11
- Python 3.14 (tested with 3.14.2)
- `pip` available in PATH
- Python packages listed in `requirements.txt`:
  - `matplotlib>=3.10`
  - `customtkinter>=5.2`
  - `rich>=14.0`

## Project Files
- `my_gui.py`: GUI entry point
- `list_parser.py`: parsing and counting logic
- `book_of_mormon.txt`: Book of Mormon source text
- `titles_of_christ.txt`: master title/reference list
- `chosen.titles.txt`: selected title subset used for charts
- `book_of_mormon.ico`: app/window icon
- `my_gui.spec`: PyInstaller build config

## Setup
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run From Source
```powershell
python my_gui.py
```

## Build Executable (Windows)
```powershell
pyinstaller -y my_gui.spec --distpath dist --workpath build
```

Executable output:
- `dist\my_gui\my_gui.exe`

## Troubleshooting
- If the app closes immediately, run it from PowerShell to see the traceback:
  - `.\dist\my_gui\my_gui.exe`
- If PyInstaller says output folders are locked, close any running app instances and rebuild.
- If a dependency is missing at startup, click `Yes` in the popup to let the app run pip and install requirements automatically.

## Screenshots
<p>
  <img src="images/image1.png" alt="Project image 1" width="900" />
</p>
<p>
  <img src="images/image2.png" alt="Project image 2" width="900" />
</p>
<p>
  <img src="images/image3.png" alt="Project image 3" width="900" />
</p>
<p>
  <img src="images/image4.png" alt="Project image 4" width="900" />
</p>
