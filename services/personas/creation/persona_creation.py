from urllib.parse import urljoin

import requests
from flask import Flask, render_template, request, flash
from openai import OpenAI

import update_heroes
import update_stories

client = OpenAI(api_key='insertAPIKeyHere')
base_url = "https://fabtcg.com/"
stories_path = "stories"
stories_url = urljoin(base_url, stories_path)
heroes_path = "heroes"
heroes_url = urljoin(base_url, heroes_path)

app = Flask(__name__)
app.secret_key = "password123"

persona_introduction = ""
persona_writing = ""
name = ""
messages = []
# db_service_url = 'http://persona-persistence:8082/createPersona'
chromadb_service_url = 'http://persona-persistence:8082'

scrapedStories = update_stories.scrape_stories(stories_url)
scrapedHeroes = update_heroes.scrape_heroes(heroes_url)


@app.route("/scrapeHeroes")
def scrapeHeroes():
    heroes_data = [
        {'name': hero['name'], 'designation': hero['designation'], 'text': hero['text']}
        for hero in scrapedHeroes
    ]
    requests.post(chromadb_service_url + '/pullscrapedHeroes', json=heroes_data, headers={'Content-Type': 'application/json'})
    return render_template('hero_scraper.html', heroes=scrapedHeroes)



@app.route("/scrapeStories")
def scrapeStories():
    stories_data = [
        {'title': story.title, 'description': story.description,
         'heroes': story.characters, 'text': story.text}
        for story in scrapedStories
    ]
    requests.post(chromadb_service_url + '/pullscrapedStories', json=stories_data, headers={'Content-Type': 'application/json'})
    return render_template('story_scraper.html', stories=scrapedStories)


@app.route("/")
def index():
    flash("What's the Heros name?")
    return render_template("0_enter_name.html")


@app.route("/getIntroduction", methods=["POST"])
def getIntroduction():
    global name
    name = request.form.get("user_input")
    flash("Okay, let's create a Persona for " + name + ". Please insert a paragraph about the hero (e.g. from "
                                                       "their hero page) to describe their character traits.")
    return render_template("1_hero_introduction.html")


@app.route("/addBiography", methods=["POST"])
def getWritingStyle():
    global heroIntroduction
    heroIntroduction = request.form.get("user_input")
    flash(
        "Hero: " + name + "\n Please insert Stories from the Heros Lore Page here.")
    return render_template("2_bio_stories.html")


@app.route("/addTraits", methods=["POST"])
def generateDepth():
    global heroBiography
    heroBiography = request.form.get("user_input")
    flash("Persona: " + name + "\n Please insert character traits for this Hero.")
    return render_template("3_character_traits.html")


# TODO: Change Creation Process based on Hero Data and Stories from http://fabtcg.com/heroes
#       and http://fabtcg.com/stories
@app.route("/generateQuestions", methods=["POST"])
def generateDescription():
    global characterTraits
    global heroIntroduction
    characterTraits = request.form.get("user_input")
    system_message = {"role": "system",
                      "content": "I want you to pretend to be a persona that is modeled after a fictional character "
                                 "from a Trading Card Game called Flesh and Blood"
                                 "so that you can interact as though the interaction is in their personal "
                                 "style of behaving and conversational mannerisms. To accomplish this, I will first "
                                 "give you a description of them so that you’ll have a "
                                 "semblance of them as a person. Next, I will provide you with samples of their "
                                 "biography so that you can discern the kind of person they are and what experiences"
                                 "they have made in the past. "
                                 f"Here is a description of the character so that you’ll have a semblance of them "
                                 f"as a person: {heroIntroduction}"
                                 f"Here are some of their character traits: {characterTraits}"
                                 "Here are some articles that are stories from their biography. "
                                 "Each article starts with the phrase “*START OF ARTICLE*” and ends with the phrase "
                                 "“*END OF ARTICLE*”: "
                                 f"{heroBiography}"
                                 "Now, write a thorough description of a persona that captures the personality and "
                                 "how the persona handles situations. Include both positive and controversial "
                                 "character traits."
                      }

    # List to store conversation messages
    global messages
    messages = [system_message]

    # Model response with Character description
    model_response = client.chat.completions.create(
        model="gpt-3.5-turbo", messages=messages
    )

    flash("Persona: " + name + "\n" + f"The model's response: {model_response.choices[0].message.content} "
                                      "Is this correct? (Type 'confirm' to confirm or describe what you "
                                      "think is missing about this hero description.): "
          )
    return render_template("4_generate_description.html")


@app.route("/checkPersonaDescription", methods=["POST"])
def checkPersonaExperience():
    confirmation = (request.form.get("user_input"))
    confirmed = False
    while not confirmed:
        if confirmation.lower() == "confirm":
            confirmed = True
        else:
            messages.append({"role": "user",
                             "content": "I think there is something missing about your perception of the heros"
                                        "character: " + confirmation + ". Please try to adapt your "
                                                                       "description accordingly."})
            # Model responds with new description
            model_response = client.chat.completions.create(
                model="gpt-3.5-turbo", messages=messages
            )
            flash("Persona: " + name + "\n" + f"The model's response: {model_response.choices[0].message.content}")
            return render_template("4_generate_description")

    messages.append(
        {"role": "user",
         "content": "Now, once again write a thorough description of a persona that captures the personality and "
                    "how the persona handles situations. Include both positive and controversial "
                    "character traits. An AI should be able to read this description and get a solid understanding"
                    "of what kind of person the hero is and how they act."})
    # Create a conversation with the assistant
    chat = client.chat.completions.create(
        model="gpt-3.5-turbo", messages=messages
    )

    # Safe the generated Data in the database
    prompt = chat.choices[0].message.content
    data = {'name': name, 'biography': prompt}
    requests.post(db_service_url, json=data)
    # Return the generated article content
    flash("Persona: " + name + "\n" + chat.choices[0].message.content)

    return render_template("5_generate_persona_prompt.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
