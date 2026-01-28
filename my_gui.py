import sys
from matplotlib import pyplot as plt # libraries allow me to create pie charts and display book of mormon information
import matplotlib as mpl
mpl.use("TkAgg")
import ctypes as ct
import customtkinter as ctk
from list_parser import *
# "pip install matplotlib" command is neccessary for the import to work

BOOK_OF_MORMON_ICON_FILEPATH = "C:\\Users\\Donov\\OneDrive\\Desktop\\book_of_mormon\\project\\book_of_mormon.ico"
DWMWA_USE_IMMERSIVE_DARK_MODE = 20

def line_chart_creator(line_info=dict, title="christ"):
    plt.subplots(figsize=(13, 6))
    shortened_dictionary = {}
    shortened_dictionary[title] = line_info[title]
    upper_case_dictionary = {}
    for key, value in shortened_dictionary.items():
        new_key = str(key).title()
        upper_case_dictionary[new_key] = value

    y = upper_case_dictionary[title.title()]
    x = [
        "1 Nephi", "2 Nephi", "Jacob", "Enos", "Jarom", "Omni",
        "W of M", "Mosiah", "Alma", "Helaman",
        "3 Nephi", "4 Nephi", "Mormon", "Ether", "Moroni"
    ]
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
    def get_pie_chart_slice_amount():
        try:
            amount_of_titles = int(input("How many of the most common titles of Christ in the Book of Mormon would you like to be displayed? "))
            if amount_of_titles < 5:
                print("Please enter 5 or more.")
                get_pie_chart_slice_amount()
            if amount_of_titles > 30:
                print("Please enter 30 or less.")
                get_pie_chart_slice_amount()
            return amount_of_titles
        except ValueError:
            print("Please enter an integer.")
            get_pie_chart_slice_amount()
    
    #amount_of_titles = get_pie_chart_slice_amount()
    pie_chart_size_multiplier = float(amount_of_titles / 10)
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
    mngr.window.wm_geometry("1080x750+360+0")
    plt.title(f"{amount_of_titles} of The Most Common Titles of Jesus Christ in The Book of Mormon")
    tot=sum(title_counts)/100.0
    autopct=lambda x: "%d" % round(x*tot)
    plt.pie(title_counts, labels=titles, colors=plt.cm.Accent.colors, autopct=autopct, explode=explode)
    plt.legend(titles, loc="upper left")
    plt.axis('equal')
    plt.show()

def get_counts_of_chosen_christ_titles(titles_chosen, counts):
    new_counts = {}
    for i in titles_chosen:
        try:
            new_counts[i] = counts[i]
        except KeyError:
            continue
    return new_counts

def build_gui():
    def dark_title_bar(window):
        window.update()
        set_window_attribute = ct.windll.dwmapi.DwmSetWindowAttribute
        get_parent = ct.windll.user32.GetParent
        hwnd = get_parent(window.winfo_id())
        rendering_policy = DWMWA_USE_IMMERSIVE_DARK_MODE
        value = 2
        value = ct.c_int(value)
        set_window_attribute(hwnd, rendering_policy, ct.byref(value), ct.sizeof(value))

    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("dark-blue") 
    window = ctk.CTk()
    dark_title_bar(window)
    info = ["20", "Jesus Christ", "Jesus Christ"]
    different_prompts = ["Enter an amount of common titles you want to see:", "Pick a Title", "Search for word or phrase in The Book of Mormon"]

    first_label = ctk.CTkLabel(window, width=500,fg_color='black',bg_color="gray30",text=different_prompts[0], anchor="w", font=('Arial',15))        
    first_entry = ctk.CTkEntry(window, width=45,fg_color='black',bg_color="gray30", font=('Arial',15,'bold'))

    first_label.grid(row=1, column=0)
    first_entry.grid(row=1, column=1)
    first_entry.insert(ctk.END, info[0])

    def on_button_press():
        amount_of_titles = int(first_entry.get())
        window.destroy()
        counts, instances = title_counter(book_of_mormon_parser(), titles_of_christ_parser())
        titles_chosen = get_chosen_titles_of_christ()
        pie_chart_creator(get_counts_of_chosen_christ_titles(titles_chosen, counts), amount_of_titles)
        sys.exit()
        
    first_button = ctk.CTkButton(window, text="GO", command=on_button_press)
    first_button.grid(row=1, column=2)

    second_label = ctk.CTkLabel(window, width=500,fg_color='black',bg_color="gray30",text=different_prompts[1], anchor="w", font=('Arial',15))        
    second_entry = ctk.CTkEntry(window, width=45,fg_color='black',bg_color="gray30", font=('Arial',15,'bold'))
    second_label.grid(row=2, column=0)
    second_entry.grid(row=2, column=1)
    second_entry.insert(ctk.END, info[1])

    def on_second_button_press():
        which_title = str(second_entry.get()).strip().lower()
        window.destroy()
        counts, instances = title_counter(book_of_mormon_parser(), titles_of_christ_parser())
        line_chart_creator(counts_per_book(instances), which_title)
        sys.exit()

    second_button = ctk.CTkButton(window, text="GO", command=on_second_button_press)
    second_button.grid(row=2, column=2)

    third_label = ctk.CTkLabel(window, width=500,fg_color='black',bg_color="gray30",text=different_prompts[2], anchor="w", font=('Arial',15))        
    third_entry = ctk.CTkEntry(window, width=45,fg_color='black',bg_color="gray30", font=('Arial',15,'bold'))
    third_label.grid(row=3, column=0)
    third_entry.grid(row=3, column=1)
    third_entry.insert(ctk.END, info[2])

    def on_third_button_press():
        pass

    third_button = ctk.CTkButton(window, text="GO", command=on_third_button_press)
    third_button.grid(row=3, column=2)

    window.title("Book of Mormon and Titles of Jesus Christ")
    window.geometry("950x750+360+0")
    window.iconbitmap(BOOK_OF_MORMON_ICON_FILEPATH)
    window.configure(bg="gray25")
    window.mainloop()
