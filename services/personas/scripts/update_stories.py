import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import namedtuple

base_url = "https://fabtcg.com/"
stories_path = "stories"
characters = [
    "Arakni", "Azalea", "Benji", "Boltyn", "Bravo", "Brevant", "Briar",
    "Chane", "Dash", "Data Doll", "Dorinthea", "Dromai", "Emperor", "Fai",
    "Genis", "Ira", "Iyslander", "Kano", "Kassai", "Katsu", "Kavdaen", "Kayo",
    "Levia", "Lexi", "Maxx", "Melody", "Oldhim", "Prism", "Rhinar", "Riptide",
    "Shiyana", "Teklovossen", "Uzuri", "Valda", "Viserai", "Vynnset", "Yoji"
]

Story = namedtuple('Story', 'title description text characters')

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

def find_characters_in_text(text):
    found_characters = [character for character in characters if character in text]
    return found_characters


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

            title = story_link.find("h5").text.strip() if story_link.find("h5") else "Unknown Title"
            description = story_link.find("p").text.strip() if story_link.find("p") else "No Description"
            detail_link = story_link["href"]

            # Handle the specific case for "Stories of Illumination"
            if title == "Stories of Illumination":
                detail_link = "/heroes/prism/stories-of-illumination/"

            # Search characters in title and description
            title_characters = find_characters_in_text(title)
            description_characters = find_characters_in_text(description)

            detail_url = urljoin(base_url, detail_link)
            parsed_url = urlparse(detail_url)
            if parsed_url.netloc != urlparse(base_url).netloc:
                continue  # Ensure we stay on the same domain

            # Search characters in URL
            link_characters = find_characters_in_text(detail_url)

            detail_response = requests.get(detail_url, headers=headers)
            detail_soup = BeautifulSoup(detail_response.content, 'html.parser')

            # Scrape the text and search for characters
            story_text = scrape_story_text(detail_soup)
            text_characters = find_characters_in_text(story_text)

            # Combine all found characters without duplicates
            all_characters = list(set(title_characters + description_characters + link_characters + text_characters))

            stories.append(Story(
                title=title,
                description=description,
                text=story_text,
                characters=all_characters  # Add found characters
            ))

            return stories

        return stories

    except requests.RequestException as e:
        print(f"Error during requests to {url}: {str(e)}")
        return []

# URL of the main stories page
stories_url = urljoin(base_url, stories_path)
stories_data = scrape_stories(stories_url)

# Print the collected data
if __name__ == "__main__":
    # This block will only execute when the script is run directly,
    # not when it's imported as a module in another script
    stories_data = scrape_stories(stories_url)

    # Print the collected data
    for story in stories_data:
        print(f"Title: {story.title}")
        print(f"Description: {story.description}")
        print(f"Text: {story.text}")
        print(f"Characters: {', '.join(story.characters)}\n")
