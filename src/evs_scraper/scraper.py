from urllib.request import urlopen
from bs4 import BeautifulSoup

SITE = "https://viatasisanatate.ro"
BASE = "/produse/carti/"
MAGIC_PARAMS = "?limitstart=0&limit=100000"
BOOKS_CATEGORIES = [
    "sanatate",
    "spiritualitate",
    "imnuri",
    "copii",
    "familie",
    "dezvoltare-personala",
    "pachete-de-carte",
    "cultura-generala",
    "poezie",
    "biografie",
    "fictiune",
]

def human_readable_category(category):
    return category.capitalize().replace("-", " ")

def url_category(category):
    return SITE + BASE + category

def intro():
    print("---------------------------------------------------------------------------")
    print("Salut! Bun venit la", SITE)
    print("Esti omul care vrea toata lista de carti intr-o singura pagina? Rezolvam...")
    print("(Shh... Pe sub mana... Dar n-am incotro ca asa-s site-urile moderne.)")

def list_categories():
    print("---------------------------------------------------------------------------")
    print("Categorii de carti: ")
    for category in BOOKS_CATEGORIES:
        print("-->", human_readable_category(category), " -- ", url_category(category))

def get_category_details(category):
    url = url_category(category)
    magic_url = url + MAGIC_PARAMS
    html_doc = get_page_html(magic_url)

    soup = BeautifulSoup(html_doc, 'html.parser')

    books = soup.findAll("div", {"class": "hikashop_product"})
    books_list = []
    for book in books:
        book_link = book.find("span", {"class": "hikashop_product_name"}).find("a")
        book_url = book_link.attrs['href']
        book_title = book_link.text
        try:
            author = book.find(
                    "dl", {"class": "hikashop_product_custom_autor_carte_line"}).find(
                            "dd", {"class": "hikashop_product_custom_value"}).text
        except Exception:
            author = "???"

        price = book.find("span", {"class": "hikashop_product_price_full"}).text

        print(book_url)
        print(book_title)
        print(author)
        print(price)
        books_list.append({
            "url": book_url,
            "title": book_title,
            "author": author,
            "price": price,
        })

    return {
        "books_list": books_list,
    }

def get_page_html(url):
    try:
        with urlopen(url) as response:
            html_content = response.read().decode('utf-8')
    except Exception as e:
        print(f"Error: {e}")
        html_content = None

    return html_content

def main():
    intro()
    list_categories()

    print("---------------------------------------------------------------------------")
    for category in BOOKS_CATEGORIES:
        details = get_category_details(category)
        print(details)

    # TODO
    # get number of pages for each category
    # get list of books
    # get details for each book
    # save final list (csv?):
    #   category, year, author, title, number of pages, price, description
