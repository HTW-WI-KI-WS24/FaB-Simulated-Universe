from urllib.parse import urljoin

import requests
from flask import Flask, render_template, request, flash, current_app
from openai import OpenAI

import update_heroes
import update_stories
import update_world

client = OpenAI(api_key='insertAPIKeyHere')
base_url = "https://fabtcg.com/"
stories_path = "stories"
stories_url = urljoin(base_url, stories_path)
heroes_path = "heroes"
heroes_url = urljoin(base_url, heroes_path)
world_url = "https://fabtcg.com/world-of-rathe"

app = Flask(__name__)
app.secret_key = "password123"

persona_introduction = ""
persona_writing = ""
name = ""
messages = []
chromadb_service_url = 'http://heroes-persistence:8082'


@app.route("/")
def homepage():
    return render_template('home.html')


@app.route("/scrapeWorld", methods=['GET', 'POST'])
def scrapeWorld():
    if request.method == 'POST':
        scrapedWorld = update_world.scrape_world(world_url)
        world_data = []
        for region in scrapedWorld:
            for paragraph in region['text']:
                world_data.append({
                    'name': region['name'],
                    'text': paragraph
                })
        requests.post(chromadb_service_url + '/pullScrapedWorld', json=world_data,
                      headers={'Content-Type': 'application/json'})
        flash('World data scraped and updated successfully!')
        return render_template('world_scraper.html', regions=scrapedWorld)
    else:
        return render_template('world_scraper.html')

@app.route("/scrapeHeroes", methods=['GET', 'POST'])
def scrapeHeroes():
    if request.method == 'POST':
        scrapedHeroes = update_heroes.scrape_heroes(heroes_url)
        heroes_data = [
            {'name': hero['name'], 'designation': hero['designation'], 'text': hero['text']}
            for hero in scrapedHeroes
        ]
        requests.post(chromadb_service_url + '/pullScrapedHeroes', json=heroes_data,
                      headers={'Content-Type': 'application/json'})
        flash('Heroes scraped and updated successfully!')
        return render_template('hero_scraper.html', heroes=scrapedHeroes)
    else:
        return render_template('hero_scraper.html')


@app.route("/scrapeStories", methods=['GET', 'POST'])
def scrapeStories():
    if request.method == 'POST':
        scrapedStories = update_stories.scrape_stories(stories_url)
        stories_data = [
            {'title': story.title, 'description': story.description,
             'heroes': story.characters, 'text': story.text}
            for story in scrapedStories
        ]
        requests.post(chromadb_service_url + '/pullScrapedStories', json=stories_data,
                      headers={'Content-Type': 'application/json'})
        flash('Stories scraped and updated successfully!')
        return render_template('story_scraper.html', stories=scrapedStories)
    else:
        return render_template('story_scraper.html')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
