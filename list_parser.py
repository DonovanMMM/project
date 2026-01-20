TITLES_OF_CHRIST_FILEPATH = "titles_of_christ.txt"
BOOK_OF_MORMON_FILEPATH = "book_of_mormon.txt"

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

def get_chosen_titles_of_christ(chosen_titles):
    with open("chosen.titles.txt", "r", encoding="utf-8") as chosen_titles_file:
        line = chosen_titles_file.readline()
        titles = line.split(",")
        return titles

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

def main():
    verse_names = book_of_mormon_parser()
    titles = titles_of_christ_parser()
    counts, instances = title_counter(verse_names, titles)
    titles_chosen = title_of_christ_checker(counts)
    save_chosen_titles_of_christ(titles_chosen)
    #longest = sorted(verses, key=len)[20:]
   # for v in longest:
       # print(len(v), repr(v))
    # 1) Are the strings identical (as sets)?
    print(titles_chosen)

if __name__ == "__main__":
    main()