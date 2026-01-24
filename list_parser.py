from matplotlib import pyplot as plt # libraries allow me to create pie charts and display book of mormon information
import matplotlib as mpl
mpl.use("TkAgg")
import tkinter as tk
import ctypes as ct
import customtkinter as ctk

# "pip install matplotlib" command is neccessary for the import to work

TITLES_OF_CHRIST_FILEPATH = "titles_of_christ.txt" # List of titles of Christ that I personally gathered during my mission
BOOK_OF_MORMON_FILEPATH = "book_of_mormon.txt" # The Book of Mormon in .txt form
DWMWA_USE_IMMERSIVE_DARK_MODE = 20

def simplify_verse(s):
    return " ".join(s.lower().split())

def titles_of_christ_parser():
    try:
        names = []
        with open(TITLES_OF_CHRIST_FILEPATH, "r", encoding="utf-8") as titles:
            for text in titles:
                if text.startswith("#"):
                    i = 0
                    for char in range(3, len(text)):
                        if not text[char].isdigit():
                            i = char
                            break
                    current_title = text[i+2:text.find(" - ")]
                    names.append(simplify_verse(current_title))
                    if " - " in current_title:
                        raise ValueError(f"Title has not been saved correctly: {current_title}")
        return names 
    except ValueError as e:
        print(e)

def book_of_mormon_parser():
    books = [
        "1 Nephi", "2 Nephi", "Jacob", "Enos", "Jarom", "Omni",
        "Words of Mormon", "Mosiah", "Alma", "Helaman",
        "3 Nephi", "4 Nephi", "Mormon", "Ether", "Moroni", "end_of_book"
    ]

    is_past_intro = False
    is_past_chapter = False
    book_count = 0
    chapter_count = 1
    verse_count = 1
    current_verse = ""
    verse_names = {}

    with open(BOOK_OF_MORMON_FILEPATH, "r", encoding="utf-8") as book:
        for text in book:
            line = " ".join(text.split())

            # -------- BOOK HEADER --------
            if line == books[book_count] or line == f"{books[book_count]} 1":
                current_book_name = books[book_count]
                book_count += 1
                chapter_count = 1
                verse_count = 1
                is_past_intro = True
                is_past_chapter = (line == f"{current_book_name} 1")

                if current_verse.strip():
                    verse_names[simplify_verse(current_verse)] = f"{books[book_count-1]} {chapter_count}:{verse_count}"
                current_verse = ""
                continue

            # -------- START CURRENT CHAPTER (handles chapter 1) --------
            if is_past_intro and line == f"{books[book_count-1]} {chapter_count}":
                verse_count = 1
                is_past_chapter = True

                if current_verse.strip():
                    verse_names[simplify_verse(current_verse)] = f"{books[book_count-1]} {chapter_count}:{verse_count}"
                current_verse = ""
                continue

            # -------- MOVE TO NEXT CHAPTER --------
            if is_past_intro and line == f"{books[book_count-1]} {chapter_count + 1}":
                chapter_count += 1
                verse_count = 1
                is_past_chapter = True

                if current_verse.strip():
                    verse_names[simplify_verse(current_verse)] = f"{books[book_count-1]} {chapter_count}:{verse_count}"
                current_verse = ""
                continue

            # -------- VERSE MARKER --------
            if is_past_chapter and line.startswith("Chapter "):
                continue
            if is_past_chapter and line == f"{books[book_count-1]} {chapter_count}:{verse_count}":
                if current_verse.strip():
                    verse_names[simplify_verse(current_verse)] = f"{books[book_count-1]} {chapter_count}:{verse_count}"
                verse_count += 1
                current_verse = ""
                continue

            # -------- VERSE TEXT --------
            if is_past_chapter:
                upper = line.upper()
                if upper.startswith("THE BOOK OF "):
                    continue
                if upper == "THE WORDS OF MORMON":
                    continue
                # skip chapter headers like "Alma 5" or "Moroni 10"
                if line == f"{books[book_count-1]} {chapter_count}":
                    continue
                if line == f"{books[book_count-1]} {chapter_count + 1}":
                    continue

                parts = line.split()
                if len(parts) >= 2 and parts[-1].isdigit():
                    book_title = " ".join(parts[:-1])
                    if book_title in books:
                        continue

                current_verse += " " + " ".join(text.split())

        # append final verse
        if current_verse.strip():
            verse_names[simplify_verse(current_verse)] = f"{books[book_count-1]} {chapter_count}:{verse_count}"

    return verse_names

def title_of_christ_checker(titles):
    for i in titles.copy():
        if titles[i] == 0:
            del titles[i]
            continue
        success = False
        while not success:
            print(i)
            current_user_response = input("Is this a title of Christ(y/n): ")
            if current_user_response.lower().strip() == "y":
                success = True
                continue
            elif current_user_response.lower().strip() == "n":
                success = True
                del titles[i]
            else:
                print('Response is invalid, please enter "y" or "n"')
    return titles

def save_chosen_titles_of_christ(chosen_titles):
    with open("chosen.titles.txt", "w", encoding="utf-8") as chosen_titles_file:
        for i in chosen_titles:
            chosen_titles_file.write(i + ",")

def get_chosen_titles_of_christ():
    with open("chosen.titles.txt", "r", encoding="utf-8") as chosen_titles_file:
        line = chosen_titles_file.readline()
        titles = line.split(",")
        return titles
    
def delete_chosen_title_of_christ(title_to_be_removed=str):
    chosen_titles = []
    title_to_be_removed = title_to_be_removed.lower().strip()
    with open("chosen.titles.txt", "r", encoding="utf-8") as chosen_titles_file:
        line = chosen_titles_file.readline()
        chosen_titles = line.split(",")
    if title_to_be_removed not in chosen_titles:
        print(ValueError("This title is not one of the chosen Christ titles."))
    else:
        chosen_titles.remove(title_to_be_removed)
        with open("chosen.titles.txt", "w", encoding="utf-8") as new_chosen_titles_file:
            for i in chosen_titles:
                new_chosen_titles_file.write(i + ",")

def title_counter(verses, titles):
    name_counts = {}
    verse_instances = {}
    for i in verses:
        for j in titles:
            if j in i:
                if j in name_counts:
                    current_count = i.count(j)
                    name_counts[j] += current_count
                    verse_instances[j].append(verses[i])
                else:
                    current_count = i.count(j)
                    name_counts[j] = current_count
                    verse_instances[j] = [verses[i]]
    return name_counts, verse_instances

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
    info = ["20", "TBD", "TBD"]
    different_prompts = ["Enter an amount of common titles you want to see:", "TBD", "TBD"]

    first_label = ctk.CTkLabel(window, width=500,fg_color='black',bg_color="gray30",text=different_prompts[0], anchor="w", font=('Arial',15))        
    first_entry = ctk.CTkEntry(window, width=45,fg_color='black',bg_color="gray30", font=('Arial',15,'bold'))

    first_label.grid(row=1, column=0)
    first_entry.grid(row=1, column=1)
    first_entry.insert(tk.END, info[0])

    def on_button_press():
        amount_of_titles = int(first_entry.get())
        window.destroy()
        counts, instances = title_counter(book_of_mormon_parser(), titles_of_christ_parser())
        titles_chosen = get_chosen_titles_of_christ()
        pie_chart_creator(get_counts_of_chosen_christ_titles(titles_chosen, counts), amount_of_titles)
        
    first_button = ctk.CTkButton(window, text="GO", command=on_button_press)
    first_button.grid(row=1, column=2)

    class Table:
        def __init__(self,window):
            # code for creating table
            for i in range(1, 3):
                for j in range(3):
                    if j == 0:
                        self.e = ctk.CTkLabel(window, width=500,fg_color='black',bg_color="gray30",text=different_prompts[i], anchor="w",
                                    font=('Arial',15))
                        
                        self.e.grid(row=i+1, column=j)
                    elif j == 1:
                        self.e = ctk.CTkEntry(window, width=45,fg_color='black',bg_color="gray30",
                                    font=('Arial',15,'bold'))
                        
                        self.e.grid(row=i+1, column=j)
                        self.e.insert(ctk.END, info[i])
                    else:
                        inner_button = ctk.CTkButton(window, text="GO", command=pie_chart_creator)
                        inner_button.grid(row=i+1, column=j)

    window.title("Book of Mormon and Titles of Jesus Christ")
    t = Table(window)
    window.geometry("950x750+360+0")
    window.iconbitmap("book_of_mormon.ico")
    window.configure(bg="gray25")
    window.mainloop()

def main():
    build_gui()

    #longest = sorted(verses, key=len)[20:]
    # for v in longest:
    # # print(len(v), repr(v))
    # 1) Are the strings identical (as sets)?

if __name__ == "__main__":
    main()