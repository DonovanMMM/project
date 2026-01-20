TITLES_OF_CHRIST_FILEPATH = "titles_of_christ.txt"
BOOK_OF_MORMON_FILEPATH = "book_of_mormon.txt"

def normalize(s):
    return " ".join(s.lower().split())

def titles_of_christ_parser():
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
                names.append(normalize(current_title))
                if " - " in current_title:
                    raise ValueError("Title has not been saved correctly")
    return names 

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
    verses = []

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
                    verses.append(normalize(current_verse))
                current_verse = ""
                continue

            # -------- START CURRENT CHAPTER (handles chapter 1) --------
            if is_past_intro and line == f"{books[book_count-1]} {chapter_count}":
                verse_count = 1
                is_past_chapter = True

                if current_verse.strip():
                    verses.append(normalize(current_verse))
                current_verse = ""
                continue

            # -------- MOVE TO NEXT CHAPTER --------
            if is_past_intro and line == f"{books[book_count-1]} {chapter_count + 1}":
                chapter_count += 1
                verse_count = 1
                is_past_chapter = True

                if current_verse.strip():
                    verses.append(normalize(current_verse))
                current_verse = ""
                continue

            # -------- VERSE MARKER --------
            if is_past_chapter and line.startswith("Chapter "):
                continue
            if is_past_chapter and line == f"{books[book_count-1]} {chapter_count}:{verse_count}":
                if current_verse.strip():
                    verses.append(normalize(current_verse))
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
            verses.append(normalize(current_verse))

    return verses


def title_counter(verses, titles):
    name_counts = {}
    for i in verses:
        for j in titles:
            if j in i:
                if j in name_counts:
                    current_count = i.count(j)
                    name_counts[j] += current_count
                else:
                    current_count = i.count(j)
                    name_counts[j] = current_count
    return name_counts

def main():
    verses = book_of_mormon_parser()
    titles = titles_of_christ_parser()
    counts = title_counter(verses, titles)
    #longest = sorted(verses, key=len)[20:]
   # for v in longest:
       # print(len(v), repr(v))
    print(counts)

if __name__ == "__main__":
    main()