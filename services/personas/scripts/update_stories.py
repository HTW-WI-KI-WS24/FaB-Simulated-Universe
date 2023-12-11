import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

base_url = "https://fabtcg.com/"
stories_path = "stories"


# TODO:
#  einige stories leiten einen auf eine Domain weiter mit /heroes/(charactername)/?stories=True und nicht auf
#  /stories. Dadurch wird bei den stories mit /heroes kein Text hinzugefügt, da man mit der normalen methode gar
#  nicht erst darauf zugreifen kann. Letztes TODO ist eine exception erfolgreich einzubauen, die auch das abdeckt

def scrape_stories(url):
    headers = {'User-Agent': 'Mozilla/5.0 ...'}

    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        stories = []

        # Suche nach allen relevanten Story-Elementen
        for story_div in soup.find_all("div", class_="listblock-item"):
            story_link = story_div.find("a", class_="item-link")
            if not story_link:
                continue

            title = story_link.find("h5").text.strip() if story_link.find("h5") else "Unbekannter Titel"
            description = story_link.find("p").text.strip() if story_link.find("p") else "Keine Beschreibung"
            detail_link = story_link["href"]

            # Vollständige URL für die Detailanfrage generieren
            detail_url = urljoin(base_url, detail_link)
            parsed_url = urlparse(detail_url)
            if parsed_url.netloc != urlparse(base_url).netloc:
                continue  # Sicherstellen, dass wir auf der gleichen Domain bleiben

            # Scraping der Detailseite der Story
            detail_response = requests.get(detail_url, headers=headers)
            detail_soup = BeautifulSoup(detail_response.content, 'html.parser')
            story_blocks = detail_soup.find_all("div", class_="block-paragraphs rich-text")

            story_text = ""
            for block in story_blocks:
                paragraphs = block.find_all("p")
                for p in paragraphs:
                    story_text += p.text.strip() + " "

            stories.append({
                "title": title,
                "description": description,
                "text": story_text.strip()
            })

        return stories

    except requests.RequestException as e:
        print(f"Error during requests to {url}: {str(e)}")
        return []


# URL der Hauptseite der Geschichten
stories_url = urljoin(base_url, stories_path)
stories_data = scrape_stories(stories_url)

# Drucken der gesammelten Daten
for story in stories_data:
    print(f"Titel: {story['title']}")
    print(f"Beschreibung: {story['description']}")
    print(f"Text: {story['text']}\n")
