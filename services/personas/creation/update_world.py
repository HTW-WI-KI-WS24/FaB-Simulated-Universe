import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# base_url = "https://fabtcg.com/world-of-rathe"


def scrape_world(url):
    headers = {'User-Agent': 'Mozilla/5.0 ...'}

    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        regions = []

        # Find all 'item-link' anchors within the 'listblock-item' divs
        for item_div in soup.find_all("div", class_="listblock-item"):
            region_link = item_div.find("a", class_="item-link")
            if not region_link:
                continue

            region_name = region_link.text.strip()
            region_url = urljoin(url, region_link['href'])
            region_text = scrape_region_details(region_url, headers)

            regions.append({
                "name": region_name,
                "url": region_url,
                "text": region_text  # list of paragraphs
            })

        return regions

    except requests.RequestException as e:
        print(f"Error during requests to {url}: {str(e)}")
        return []


def scrape_region_details(region_url, headers):
    response = requests.get(region_url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    rich_text_divs = soup.find_all("div", class_="rich-text")
    content_list = []  # Use a list to store unique content in order

    for div in rich_text_divs:
        # Include h3 in the list of elements to find
        elements = div.find_all(["h3", "h4", "p"])
        current_header = ""

        for element in elements:
            if element.name in ["h3", "h4"]:
                current_header = element.get_text(strip=True) + ":"
            elif element.name == "p":
                paragraph_text = element.get_text(strip=True)
                combined_text = f"{current_header} {paragraph_text}" if current_header else paragraph_text
                if combined_text not in content_list:
                    content_list.append(combined_text)
                    current_header = ""  # Reset the header after using it

    return content_list


# world_data = scrape_world(base_url)
#
# for region in world_data:
#     print(region['url'])
#     print(region['name'])
#     for paragraph in region['text']:  # Iterate over paragraphs
#         print(paragraph)
