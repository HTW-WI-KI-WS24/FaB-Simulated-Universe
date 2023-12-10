import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

base_url = "https://fabtcg.com/heroes"

# TODO Testing

def scrape_heroes(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    heroes = []
    for hero in soup.find_all("div", class_="hero-row-name"):
        name = hero.find("h2").text
        designation = hero.find("h5", class_="p-0 m-0").text
        detail_link = hero.find("a")["href"]
        full_link = urljoin(base_url, detail_link)

        # Scraping der Detailseite des Helden
        detail_response = requests.get(full_link)
        detail_soup = BeautifulSoup(detail_response.content, 'html.parser')
        hero_text = detail_soup.find("div", class_="block-para pt-5 pb-4 container text-center").text

        heroes.append({
            "name": name,
            "designation": designation,
            "text": hero_text
        })

    return heroes


heroes_data = scrape_heroes(base_url)
