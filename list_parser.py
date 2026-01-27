from my_gui import *

TITLES_OF_CHRIST_FILEPATH = "C:\\Users\\Donov\\OneDrive\\Desktop\\book_of_mormon\\project\\titles_of_christ.txt" # List of titles of Christ that I personally gathered during my mission
BOOK_OF_MORMON_FILEPATH = "C:\\Users\\Donov\\OneDrive\\Desktop\\book_of_mormon\\project\\book_of_mormon.txt" # The Book of Mormon in .txt form
BOOKS = [
        "1 Nephi", "2 Nephi", "Jacob", "Enos", "Jarom", "Omni",
        "Words of Mormon", "Mosiah", "Alma", "Helaman",
        "3 Nephi", "4 Nephi", "Mormon", "Ether", "Moroni", "end_of_book"
    ]

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
            if line == BOOKS[book_count] or line == f"{BOOKS[book_count]} 1":
                current_book_name = BOOKS[book_count]
                book_count += 1
                chapter_count = 1
                verse_count = 1
                is_past_intro = True
                is_past_chapter = (line == f"{current_book_name} 1")

                if current_verse.strip():
                    verse_names[simplify_verse(current_verse)] = f"{BOOKS[book_count-1]} {chapter_count}:{verse_count}"
                current_verse = ""
                continue

            # -------- START CURRENT CHAPTER (handles chapter 1) --------
            if is_past_intro and line == f"{BOOKS[book_count-1]} {chapter_count}":
                verse_count = 1
                is_past_chapter = True

                if current_verse.strip():
                    verse_names[simplify_verse(current_verse)] = f"{BOOKS[book_count-1]} {chapter_count}:{verse_count}"
                current_verse = ""
                continue

            # -------- MOVE TO NEXT CHAPTER --------
            if is_past_intro and line == f"{BOOKS[book_count-1]} {chapter_count + 1}":
                chapter_count += 1
                verse_count = 1
                is_past_chapter = True

                if current_verse.strip():
                    verse_names[simplify_verse(current_verse)] = f"{BOOKS[book_count-1]} {chapter_count}:{verse_count}"
                current_verse = ""
                continue

            # -------- VERSE MARKER --------
            if is_past_chapter and line.startswith("Chapter "):
                continue
            if is_past_chapter and line == f"{BOOKS[book_count-1]} {chapter_count}:{verse_count}":
                if current_verse.strip():
                    verse_names[simplify_verse(current_verse)] = f"{BOOKS[book_count-1]} {chapter_count}:{verse_count}"
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
                if line == f"{BOOKS[book_count-1]} {chapter_count}":
                    continue
                if line == f"{BOOKS[book_count-1]} {chapter_count + 1}":
                    continue

                parts = line.split()
                if len(parts) >= 2 and parts[-1].isdigit():
                    book_title = " ".join(parts[:-1])
                    if book_title in BOOKS:
                        continue

                current_verse += " " + " ".join(text.split())

        # append final verse
        if current_verse.strip():
            verse_names[simplify_verse(current_verse)] = f"{BOOKS[book_count-1]} {chapter_count}:{verse_count}"

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

def counts_per_book(verse_instances=dict):
    current_list = []
    new_dict = {}
    for i in verse_instances.keys():
        counts_per_book = [0] * 15
        current_list = verse_instances[i]
        for j in current_list:
            for k in range(len(BOOKS)):
                if BOOKS[k] in j:
                    counts_per_book[k] += 1
        new_dict[i] = counts_per_book
    return new_dict


def main():
    build_gui()

if __name__ == "__main__":
    main()