import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

base_url = "https://fabtcg.com/heroes"


def scrape_heroes(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/58.0.3029.110 Safari/537.3'}

    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        heroes = []

        for hero in soup.find_all("div", class_="hero-row-name text-center py-2 mt-3 mb-5 mb-lg-3 line-before-g "
                                                "line-after-g-dbl "):
            name = hero.find("h2", class_="p-0 m-0 ").text
            designation = hero.find("h5", class_="p-0 m-0").text
            detail_link = hero.find("a")["href"]
            full_link = urljoin(base_url, detail_link)

            # Scraping der Detailseite des Helden
            detail_response = requests.get(full_link, headers=headers)
            detail_soup = BeautifulSoup(detail_response.content, 'html.parser')
            hero_text = detail_soup.find("div", class_="block-para pt-5 pb-4 container text-center").text

            heroes.append({
                "name": name,
                "designation": designation,
                "text": hero_text
            })
            print(heroes)

        return heroes

    except requests.RequestException as e:
        print(f"Error during requests to {url}: {str(e)}")
        return []


heroes_data = scrape_heroes(base_url)
