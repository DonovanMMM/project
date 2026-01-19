TITLES_OF_CHRIST_FILEPATH = "titles_of_christ.txt"
BOOK_OF_MORMON_FILEPATH = "book_of_mormon.txt"


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
                names.append(current_title.lower().strip())
                if " - " in current_title:
                    raise ValueError("Title has not been saved correctly")
    return names 

def book_of_mormon_searcher():
    books = ["1 Nephi", "2 Nephi", "Jacob", "Enos", "Jarom", "Omni", "Words of Mormon", "Mosiah", "Alma", "Helaman", "3 Nephi", "4 Nephi", "Mormon", "Ether", "Moroni", "end_of_book"]
    is_past_intro = False
    is_past_chapter = False
    book_count = 0
    chapter_count = 1
    verse_count = 1
    current_verse = ""
    with open(BOOK_OF_MORMON_FILEPATH, "r", encoding="utf-8") as book, open("test_file.txt", "w") as test:
        for text in book:
            if text.startswith(books[book_count] + " 1\n"):
                book_count += 1 
                chapter_count = 1
                verse_count = 1
                test.write(current_verse)
                current_verse = ""
                is_past_intro = True
                continue
            if is_past_intro:
                if text.startswith(f"Chapter {chapter_count}\n"):
                    chapter_count += 1
                    verse_count = 1
                    is_past_chapter = True
                    test.write(current_verse)
                    current_verse = ""
                    continue
            if is_past_chapter:
                if text.startswith(f" {verse_count}"):
                    test.write(current_verse)
                    verse_count += 1
                    current_verse = text
                    continue
                else:
                    current_verse += text
        test.write(current_verse)



def main():
    book_of_mormon_searcher()
    

if __name__ == "__main__":
    main()