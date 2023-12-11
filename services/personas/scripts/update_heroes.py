import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

base_url = "https://fabtcg.com/heroes"


def scrape_heroes(url):
    headers = {'User-Agent': 'Mozilla/5.0 ...'}

    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        heroes = []

        # Suche nach allen 'hero-row-name' divs
        for hero_div in soup.find_all("div", class_="hero-row-name"):
            hero_link = hero_div.find("a")
            if not hero_link:
                continue

            name = hero_link.find("h2").text.strip() if hero_link.find("h2") else "Unbekannter Name"
            designation = hero_link.find("h5").text.strip() if hero_link.find("h5") else "Unbekannte Bezeichnung"

            detail_link = hero_link["href"]
            full_link = urljoin(base_url, detail_link)

            # Scraping der Detailseite des Helden
            detail_response = requests.get(full_link, headers=headers)
            detail_soup = BeautifulSoup(detail_response.content, 'html.parser')
            hero_text = detail_soup.find("div",
                                         class_="block-para pt-5 pb-4 container text-center").text.strip() if detail_soup.find(
                "div", class_="block-para pt-5 pb-4 container text-center") else "Kein Text gefunden"

            heroes.append({
                "name": name,
                "designation": designation,
                "text": hero_text
            })

        return heroes

    except requests.RequestException as e:
        print(f"Error during requests to {url}: {str(e)}")
        return []


heroes_data = scrape_heroes(base_url)

# Drucken der gesammelten Daten
# for hero in heroes_data:
# print(f"Name: {hero['name']}")
# print(f"Designation: {hero['designation']}")
# print(f"Text: {hero['text']}\n")
