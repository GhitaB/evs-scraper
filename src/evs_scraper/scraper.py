from urllib.request import urlopen
from bs4 import BeautifulSoup
import json

SITE = "https://viatasisanatate.ro"
BASE = "/produse/carti/"
YEARS_FROM = "1990"
YEARS_TO = "2023"
LIMIT_MAX_PRICE = 60  # use None for no limit
EXCLUDE_DUPLICATE = True  # True: include only books you don't have
HARD_EXCLUDE = False  # True: use OR instead of AND in expression title-author
USE_BLACKLIST_AS_WHITELIST = False  # True: see only the books you have
SEARCH_PRINTRE_CARTI = False  # True: try to find the books on printrecarti.ro
USE_SAVED_LIST = False  # False: download the list of books each time
ONLY_DISCOUNTED = False  # True: show only discounted books
ONLY_IN_STOCK = True  # True: exclude books that are not in stock

# MAGIC_PARAMS = "?limitstart=0&limit=100000"
# MAGIC_PARAMS = "?limitstart=0&limit=100000&filter_Ordonare_6=price--lth"
# MAGIC_PARAMS = ("?limitstart=0&limit=100000&filter_Ordonare_6=price--lth" +
#                 "&filter_Limba_4=1")
MAGIC_PARAMS = ("?limitstart=0&limit=100000&filter_Ordonare_6=price--lth" +
                "&filter_Limba_4=1&filter_Anulapariiei_8=1" +
                "&filter_Anulapariiei_8_values=" + YEARS_FROM +
                ".00+-+" + YEARS_TO + ".00")

BOOKS_CATEGORIES = [
    "sanatate",
    "spiritualitate",
    "imnuri",
    # "copii",
    "familie",
    "dezvoltare-personala",
    # "pachete-de-carte",
    "cultura-generala",
    "poezie",
    "biografie",
    # "fictiune",
]


def human_readable_category(category):
    return category.capitalize().replace("-", " ")


def url_category(category):
    return SITE + BASE + category


def intro():
    print("------------------------------------------------------------------")
    print("Salut! Bun venit la", SITE)
    print("Esti omul care vrea toata lista de carti intr-o singura pagina?")
    print("(Rezolvam. Shh... Pe sub mana. Asa-s site-urile moderne...)")


def list_categories():
    print("------------------------------------------------------------------")
    print("Categorii de carti: ")
    for category in BOOKS_CATEGORIES:
        print("-->", human_readable_category(category),
              " -- ", url_category(category))


def get_page_html(url):
    try:
        with urlopen(url) as response:
            html_content = response.read().decode('utf-8')
    except Exception as e:
        e = e
        # print(f"Error: {e}")
        html_content = None
    return html_content


def get_category_details(category):
    url = url_category(category)
    magic_url = url + MAGIC_PARAMS
    html_doc = get_page_html(magic_url)

    soup = BeautifulSoup(html_doc, 'html.parser')

    books = soup.find(
        "section", {"id": "g-container-main"}).findAll(
        "div", {"class": "hikashop_product"})

    books_list = []

    BOOKS_I_HAVE = ""
    try:
        if EXCLUDE_DUPLICATE is True or USE_BLACKLIST_AS_WHITELIST:
            with open("blacklist.txt", "r") as file:
                BOOKS_I_HAVE = file.read()
    except FileNotFoundError:
        print("ATENTIE: Nu ai creat blacklist.txt cu lista cartilor tale.")

    for book in books:
        book_link = book.find(
            "span", {"class": "hikashop_product_name"}).find("a")
        book_url = book_link.attrs['href'].strip()
        h_url = SITE + book_url
        book_title = book_link.text.strip()
        try:
            class_a = "hikashop_product_custom_autor_carte_line"
            class_b = "hikashop_product_custom_value"
            author = book.find(
                "dl", {"class": class_a}).find(
                "dd", {"class": class_b}).text.strip()
        except Exception:
            author = "???"

        in_stock = True
        stock_flag = book.find(
            "span", {"class": "hikashop_product_stock_count"})
        if stock_flag is not None:
            if "Nu este" in stock_flag.text:
                in_stock = False

        price = book.find(
            "span", {"class": "hikashop_product_price_full"}).text
        price_info = price.replace(" lei ", "")
        if "lei" in price_info:
            # discount detected
            h_price = float(price_info.split("lei")[-1].replace(",", "."))
            old_price = float(price_info.split("lei")[0].replace(",", "."))
            is_discounted = True
        else:
            h_price = float(price_info.split("lei")[-1].replace(",", "."))
            old_price = h_price
            is_discounted = False

        this_book = {
            "url": h_url,
            "title": book_title,
            "author": author,
            "price": h_price,
            "old_price": old_price,
            "is_discounted": is_discounted,
            "in_stock": in_stock,
        }

        if EXCLUDE_DUPLICATE is True or USE_BLACKLIST_AS_WHITELIST is True:
            # Not perfect. TODO: improve this
            is_duplicate = False
            if HARD_EXCLUDE is True:
                if this_book['author'] in BOOKS_I_HAVE or \
                        this_book['title'] in BOOKS_I_HAVE:
                    print("DUPLICATE: ", this_book)
                    is_duplicate = True
            else:
                if this_book['author'] in BOOKS_I_HAVE and \
                        this_book['title'] in BOOKS_I_HAVE:
                    print("DUPLICATE: ", this_book)
                    is_duplicate = True

            if EXCLUDE_DUPLICATE is True and is_duplicate is True:
                continue

            if HARD_EXCLUDE is True and is_duplicate is True:
                continue

            if USE_BLACKLIST_AS_WHITELIST is True and is_duplicate is False:
                continue

        if ONLY_IN_STOCK is True and this_book['in_stock'] is False:
            continue

        if LIMIT_MAX_PRICE is not None and h_price > LIMIT_MAX_PRICE:
            continue

        if ONLY_DISCOUNTED is True and this_book['is_discounted'] is False:
            continue

        books_list.append(this_book)

    return {
        "books_list": books_list,
    }


def get_all_books():
    print("------------------------------------------------------------------")
    all_books = []
    all_authors = []
    total_price = 0
    book_id = 1
    for category in BOOKS_CATEGORIES:
        h_category = human_readable_category(category)
        books = get_category_details(category)['books_list']
        for book in books:

            already_in_list = False
            for a_book in all_books:
                if a_book['author'] == book['author'] and \
                        a_book['title'] == book['title']:
                    already_in_list = True

            if book['author'] not in all_authors:
                all_authors.append(book['author'])

            if not already_in_list:
                all_books.append(book)
                total_price += book['price']
                print(
                    book_id,
                    h_category,
                    book['author'],
                    book['title'],
                    book['old_price'],
                    book['price'],
                    book['url']
                )
                book_id += 1

    print("------------------------------------------------------------------")
    print("Iata si lista tuturor autorilor:")
    print(all_authors)
    print("------------------------------------------------------------------")
    print("PRET TOTAL, NUMAI ASTAZI, EVIDENT:", total_price, "lei")
    print("------------------------------------------------------------------")
    return all_books


def search_printre_carti(all_books):
    url = "https://www.printrecarti.ro/?cauta="

    found_id = 1

    for book in all_books:
        search_url = url + \
            book['author'].replace(" ", "+") + "+" + \
            book['title'].replace(" ", "+")
        html_doc = get_page_html(search_url)
        if html_doc is None:
            continue

        soup = BeautifulSoup(html_doc, 'html.parser')
        not_found_flag = soup.find("span", {"class": "nuexistaproduse"})

        if not_found_flag is None:
            product_details = soup.find("div", {"class": "produs"})
            if "IN STOC" in product_details.text:
                print(found_id, "PRINTRE CARTI: ",
                      book['author'], book['title'], book['price'])
                print(search_url)
                found_id += 1


def save_books_list(all_books):
    with open('books.json', "w") as file:
        json.dump(all_books, file, indent=4)


def try_get_books_from_file():
    with open('books.json', "r") as file:
        all_books = json.load(file)

    return all_books


def main():
    intro()
    list_categories()

    if USE_SAVED_LIST is True:
        try:
            print("Incerc sa folosesc lista de carti descarcata deja...")
            all_books = try_get_books_from_file()
        except Exception:
            print("Descarc lista proaspata de carti...")
            all_books = get_all_books()
    else:
        all_books = get_all_books()

    save_books_list(all_books)
    if SEARCH_PRINTRE_CARTI is True:
        search_printre_carti(all_books)
