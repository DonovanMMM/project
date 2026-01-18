TITLES_OF_CHRIST_FILEPATH = "C:\\Users\\User\\OneDrive\\Desktop\\cs_111\\project\\titles_of_christ.txt"
BOOK_OF_MORMON_FILEPATH = "C:\\Users\\User\\OneDrive\\Desktop\\cs_111\\project\\book_of_mormon.txt"


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
                    raise ValueError
    return names 

def book_of_mormon_searcher(titles=list):
    counts = []
    books = ["1 Nephi", "2 Nephi", "Jacob", "Enos", "Jarom", "Omni", "Words of Mormon", "Mosiah", "Alma", "Helaman", "3 Nephi", "4 Nephi", "Mormon", "Ether", "Moroni"]
    is_past_intro = False
    book_count = 0
    chapter_count = 1
    with open(BOOK_OF_MORMON_FILEPATH, "r", encoding="utf-8") as book:
        for text in book:
            if text.startswith(books[book_count] + " 1\n"):
                print(text)
                book_count += 1 
                chapter_count = 1
                is_past_intro = True
                continue
            if is_past_intro:
                if text.startswith(f"Chapter {chapter_count}\n"):
                    chapter_count += 1
                    continue
    print(book_count, chapter_count)


def main():
    titles = titles_of_christ_parser()
    book_of_mormon_searcher()
    

if __name__ == "__main__":
    main()