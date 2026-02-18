import sys
import subprocess
import importlib
from pathlib import Path
#taskkill /F /IM emulator.exe /IM qemu-system-x86_64.exe /IM adb.exe powershell -ExecutionPolicy Bypass -File "C:\dev\Book_of_Mormon_local\run_mobile_fixed.ps1"

REQUIRED_DEPENDENCIES = {
    "matplotlib": "matplotlib>=3.10",
    "customtkinter": "customtkinter>=5.2",
    "rich": "rich>=14.0",
}

def get_missing_dependencies() -> list[str]:
    missing = []
    for module_name in REQUIRED_DEPENDENCIES:
        try:
            importlib.import_module(module_name)
        except ImportError:
            missing.append(module_name)
    return missing

def prompt_and_install_requirements(missing_modules: list[str]):
    requirements_path = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent)) / "requirements.txt"
    package_specs = [REQUIRED_DEPENDENCIES[name] for name in missing_modules if name in REQUIRED_DEPENDENCIES]

    install_command = []
    if requirements_path.exists():
        install_command = [sys.executable, "-m", "pip", "install", "-r", str(requirements_path)]
    else:
        install_command = [sys.executable, "-m", "pip", "install", *package_specs]

    question = (
        f"Missing required dependencies: {', '.join(missing_modules)}\n\n"
        f"Python interpreter:\n{sys.executable}\n\n"
        "Would you like to install the required dependencies now?"
    )
    try:
        import tkinter as tk
        from tkinter import messagebox as tk_messagebox
        root = tk.Tk()
        root.withdraw()
        should_install = tk_messagebox.askyesno("Missing Dependencies", question)
        if should_install:
            result = subprocess.run(install_command, capture_output=True, text=True)
            if result.returncode == 0:
                tk_messagebox.showinfo("Install Complete", "Dependencies installed successfully. Please relaunch the app.")
            else:
                error_output = (result.stderr or result.stdout or "Unknown install error").strip()
                tk_messagebox.showerror("Install Failed", f"Could not install dependencies.\n\n{error_output}")
        root.destroy()
    except Exception:
        print(question)
        response = input("Install now? (y/n): ").strip().lower()
        if response == "y":
            result = subprocess.run(install_command)
            if result.returncode == 0:
                print("Dependencies installed successfully. Please relaunch the app.")
            else:
                print("Could not install dependencies. Please run one of these commands:")
                print(" ".join(install_command))

missing_dependencies = get_missing_dependencies()
if missing_dependencies:
    prompt_and_install_requirements(missing_dependencies)
    sys.exit(1)

try:
    import matplotlib as mpl # type: ignore
    mpl.use("TkAgg")
    from matplotlib import pyplot as plt # type: ignore # libraries allow me to create pie charts and display book of mormon information
    from list_parser import *
except ImportError as e:
    try:
        import tkinter as tk
        from tkinter import messagebox as tk_messagebox
        root = tk.Tk()
        root.withdraw()
        tk_messagebox.showerror("Startup Error", f"Import failed: {e}\n\nThis is not a standard missing-package error.")
        root.destroy()
    except Exception:
        print(f"Import failed: {e}")
    sys.exit(1)
import ctypes as ct
import customtkinter as ctk # type: ignore
from tkinter import messagebox
# "pip install matplotlib" command is neccessary for the import to work

def resource_path(filename: str) -> str:
    base_path = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return str(base_path / filename)

BOOK_OF_MORMON_ICON_FILEPATH = resource_path("book_of_mormon.ico")
DWMWA_USE_IMMERSIVE_DARK_MODE = 20

def safe_set_icon(window, icon_path: str):
    try:
        window.iconbitmap(icon_path)
    except Exception:
        pass

def dark_title_bar(window):
        window.update_idletasks()
        hwnd = window.winfo_id()
        # Tk returns an internal child hwnd; DWM titlebar attributes must be
        # applied to the real top-level window handle.
        GA_ROOT = 2
        hwnd = ct.windll.user32.GetAncestor(hwnd, GA_ROOT)
        value = ct.c_int(1)
        value_size = ct.sizeof(value)
        for attr in (20, 19):
            ct.windll.dwmapi.DwmSetWindowAttribute(hwnd, attr, ct.byref(value), value_size)

def line_chart_creator(line_info=dict, title="christ"):
    if title not in line_info:
        messagebox.showerror("Title Not Found", f'"{title}" was not found in the parsed titles.')
        return
    plt.subplots(figsize=(13, 6))
    mngr = plt.get_current_fig_manager()
    mngr.window.title("Line Chart")
    mngr.window.wm_geometry("1080x750+360+0")
    safe_set_icon(mngr.window, BOOK_OF_MORMON_ICON_FILEPATH)
    mngr.window.after(10, lambda: dark_title_bar(mngr.window))
    shortened_dictionary = {}
    shortened_dictionary[title] = line_info[title]
    upper_case_dictionary = {}
    for key, value in shortened_dictionary.items():
        new_key = str(key).title()
        upper_case_dictionary[new_key] = value

    y = upper_case_dictionary[title.title()]
    # Keep axis labels aligned with parsed counts (exclude sentinel labels like "end_of_book").
    x = BOOKS[: len(y)]
    plt.plot(x, y, label=f"{title.title()}", marker="o")
    for xi in range(len((x))):
        plt.annotate(f'{y[xi]}',
                 (xi, y[xi]),
                 textcoords="offset points",
                 xytext=(0, 10),
                 ha='center')
    plt.xlabel("Books of The Book of Mormon")
    plt.ylabel("Instances of title")
    plt.title("Instances of Jesus Christ's titles in each book of The Book of Mormon")
    plt.legend()
    plt.grid(True)
    plt.show()

def pie_chart_creator(counts=dict, amount_of_titles=20):
    sorted_titles = sorted(counts.items(), key=lambda item: item[1])
    shortened_dictionary = dict(sorted_titles[-amount_of_titles:])
    upper_case_dictionary = {}
    for key, value in shortened_dictionary.items():
        new_key = str(key).title()
        upper_case_dictionary[new_key] = value
    titles = upper_case_dictionary.keys()
    title_counts = upper_case_dictionary.values()
    explode  = [0] * amount_of_titles
    explode[amount_of_titles - 1], explode[amount_of_titles - 2], explode[amount_of_titles - 3], explode[amount_of_titles - 4], explode[amount_of_titles - 5] = .1, .08, .06, .04, .02
    mngr = plt.get_current_fig_manager()
    mngr.window.title("Pie Chart")
    mngr.window.wm_geometry("1080x750+360+0")
    safe_set_icon(mngr.window, BOOK_OF_MORMON_ICON_FILEPATH)
    mngr.window.after(10, lambda: dark_title_bar(mngr.window))
    plt.title(f"{amount_of_titles} of The Most Common Titles of Jesus Christ in The Book of Mormon")
    tot=sum(title_counts)/100.0
    autopct=lambda x: "%d" % round(x*tot)
    plt.pie(title_counts, labels=titles, colors=plt.cm.Accent.colors, autopct=autopct, explode=explode)
    plt.legend(titles, loc="upper left")
    plt.axis('equal')
    plt.show()

def searcher_creator(parent, verses, search_term):
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("dark-blue") 
    existing = getattr(parent, "search_window", None)
    if existing is not None and existing.winfo_exists():
        existing.destroy()

    top = ctk.CTkToplevel(parent)
    parent.search_window = top
    summary_label = ctk.CTkLabel(top, text=f'Found {len(verses)} matches for "{search_term}"', anchor="w", font=('Arial',15))
    summary_label.grid(column=0, row=0, sticky="ew", padx=8, pady=(8, 4))
    textbox = ctk.CTkTextbox(top, width=950, height=750, wrap="word")
    textbox.grid(column=0, row=1, sticky="nsew")
    top.grid_rowconfigure(1, weight=1)
    top.grid_columnconfigure(0, weight=1)
    text = ""
    for verse_text, verse_ref in verses:
        text += f"{verse_ref}\n{verse_text}\n\n"
    textbox.insert("1.0", text)

    textbox.tag_config("match", foreground="black")
    term = (search_term or "").strip()
    if term:
        start = "1.0"
        while True:
            i = textbox.search(term, start, stopindex="end", nocase=True)
            if not i:
                break
            end = f"{i}+{len(term)}c"
            textbox.tag_add("match", i, end)
            start = end
    top.title("Book of Mormon Searcher")
    top.geometry("950x750+360+0")
    safe_set_icon(top, BOOK_OF_MORMON_ICON_FILEPATH)
    top.after(50, lambda: safe_set_icon(top, BOOK_OF_MORMON_ICON_FILEPATH))
    top.configure(bg="gray25")
    top.after(10, lambda: dark_title_bar(top))
    top.transient(parent)
    top.lift()
    top.attributes("-topmost", True)
    top.after(100, lambda: top.attributes("-topmost", False))
    top.focus_force()

def get_counts_of_chosen_christ_titles(titles_chosen, counts):
    new_counts = {}
    for i in titles_chosen:
        try:
            new_counts[i] = counts[i]
        except KeyError:
            continue
    return new_counts

def build_gui():
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("dark-blue") 
    window = ctk.CTk()
    window.after(10, lambda: dark_title_bar(window))
    verses = book_of_mormon_parser()
    all_titles = titles_of_christ_parser(TITLES_OF_CHRIST_FILEPATH)
    counts, instances = title_counter(verses, all_titles)

    info = ["20", "Jesus Christ", "Jesus Christ"]
    different_prompts = ["Enter an amount of common titles you want to see:", "Pick a Title", "Search for word or phrase in The Book of Mormon"]

    first_label = ctk.CTkLabel(window, width=500,fg_color='gray15',bg_color="gray30",text=different_prompts[0], anchor="w", font=('Arial',15))        
    first_entry = ctk.CTkEntry(window, width=125,fg_color='gray15',bg_color="gray30", font=('Arial',15,'bold'))

    first_label.grid(row=1, column=0)
    first_entry.grid(row=1, column=1)
    first_entry.insert(ctk.END, info[0])

    def on_button_press():
        amount_of_titles = int(first_entry.get())
        titles_chosen = get_chosen_titles_of_christ() # type: ignore
        pie_chart_creator(get_counts_of_chosen_christ_titles(titles_chosen, counts), amount_of_titles)
        
    first_button = ctk.CTkButton(window, text="Show Pie", command=on_button_press, fg_color="black")
    first_button.grid(row=1, column=2)

    second_label = ctk.CTkLabel(window, width=500,fg_color='gray15',bg_color="gray30",text=different_prompts[1], anchor="w", font=('Arial',15))        
    second_entry = ctk.CTkEntry(window, width=125,fg_color='gray15',bg_color="gray30", font=('Arial',15,'bold'))
    second_label.grid(row=2, column=0)
    second_entry.grid(row=2, column=1)
    second_entry.insert(ctk.END, info[1])

    def on_second_button_press():
        which_title = str(second_entry.get()).strip().lower()
        line_chart_creator(counts_per_book(instances), which_title)

    second_button = ctk.CTkButton(window, text="Show Line", command=on_second_button_press, fg_color="black")
    second_button.grid(row=2, column=2)

    third_label = ctk.CTkLabel(window, width=500,fg_color='gray15',bg_color="gray30",text=different_prompts[2], anchor="w", font=('Arial',15))        
    third_entry = ctk.CTkEntry(window, width=125,fg_color='gray15',bg_color="gray30", font=('Arial',15,'bold'))
    third_label.grid(row=3, column=0)
    third_entry.grid(row=3, column=1)
    third_entry.insert(ctk.END, info[2])

    def on_third_button_press():
        search_term = str(third_entry.get()).strip().lower()
        verses_with_search_term = []
        _, search_instances = title_counter(verses, [search_term])
        if search_term in search_instances:
            for i in search_instances[search_term]:
                for j, k in verses.items():
                    if i == k:
                        verses_with_search_term.append((j, k))
        window.after(50, lambda: searcher_creator(window, verses_with_search_term, search_term))

    third_button = ctk.CTkButton(window, text="Search", command=on_third_button_press, fg_color="black")
    third_button.grid(row=3, column=2)

    window.title("Book of Mormon and Titles of Jesus Christ")
    window.geometry("950x750+360+0")
    safe_set_icon(window, BOOK_OF_MORMON_ICON_FILEPATH)
    window.configure(bg="gray25")

    def close_app():
        window.quit()
        window.destroy()

    window.protocol("WM_DELETE_WINDOW", close_app)
    window.mainloop()

def main():
    build_gui()  # type: ignore

if __name__ == "__main__":
    main()
