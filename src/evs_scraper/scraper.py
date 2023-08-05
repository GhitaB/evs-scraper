SITE = "https://viatasisanatate.ro"
BASE = "/produse/carti/"
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

def main():
    print("---------------------------------------------------------------------------")
    print("Salut! Bun venit la", SITE)
    print("Esti omul care vrea toata lista de carti intr-o singura pagina? Rezolvam...")
    print("(Shh... Pe sub mana... Dar n-am incotro ca asa-s site-urile moderne.)")
    print("---------------------------------------------------------------------------")

    print("Categorii de carti: ")
    for category in BOOKS_CATEGORIES:
        print("-->", human_readable_category(category), " -- ", url_category(category))
    print("---------------------------------------------------------------------------")
