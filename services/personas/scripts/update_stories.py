import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

base_url = "https://fabtcg.com/"
stories_path = "stories"


# TODO:
#  Zu den Stories zugehörige Helden mitscrapen bzw. schauen inwieweit das möglich ist
def scrape_story_text(detail_soup):
    story_text = ""

    # Überprüfen Sie zuerst die ursprüngliche Struktur
    story_blocks = detail_soup.find_all("div", class_="block-paragraphs rich-text")
    if story_blocks:
        for block in story_blocks:
            paragraphs = block.find_all("p")
            for p in paragraphs:
                story_text += p.text.strip() + " "
    else:
        # Überprüfen Sie die Struktur aus dem neuesten Screenshot
        story_blocks = detail_soup.find_all("div", class_="block-paragraphs")
        for block in story_blocks:
            paragraphs = block.find_all("p")
            for p in paragraphs:
                story_text += p.text.strip() + " "

    # Wenn die vorherigen Strukturen nicht gefunden wurden, suchen Sie nach der Struktur aus dem ersten Screenshot
    if not story_text:
        paragraphs = detail_soup.find_all("p", attrs={"data-block-key": True})
        for p in paragraphs:
            story_text += p.text.strip() + " "

    return story_text.strip()

def scrape_stories(url):
    headers = {'User-Agent': 'Mozilla/5.0 ...'}
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        stories = []

        for story_div in soup.find_all("div", class_="listblock-item"):
            story_link = story_div.find("a", class_="item-link")
            if not story_link:
                continue

            title = story_link.find("h5").text.strip() if story_link.find("h5") else "Unbekannter Titel"
            description = story_link.find("p").text.strip() if story_link.find("p") else "Keine Beschreibung"
            detail_link = story_link["href"]

            detail_url = urljoin(base_url, detail_link)
            parsed_url = urlparse(detail_url)
            if parsed_url.netloc != urlparse(base_url).netloc:
                continue  # Sicherstellen, dass wir auf der gleichen Domain bleiben

            detail_response = requests.get(detail_url, headers=headers)
            detail_soup = BeautifulSoup(detail_response.content, 'html.parser')

            # Rufen Sie die Funktion auf, um den Text zu scrapen
            story_text = scrape_story_text(detail_soup)

            stories.append({
                "title": title,
                "description": description,
                "text": story_text
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
