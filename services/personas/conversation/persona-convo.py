import os
import openai
from flask import Flask, request, flash, render_template, redirect, url_for, current_app
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
app_secret_key = os.getenv('APP_SECRET_KEY')
openai.api_key = api_key

app = Flask(__name__)
app.secret_key = app_secret_key

chromadb_service_url = 'http://persona-persistence:8082'
getPersonaUrl = 'http://persona-persistence:8082/getHero/'
personaList = []


@app.route('/showPlaceholders')
def showPlaceholderPersonalities():
    response = requests.get(chromadb_service_url + "/getAllPlaceholders")
    if response.status_code == 200:
        data = response.json()
        ids = data.get('heroes', {}).get('ids', [])
        metadatas = data.get('heroes', {}).get('metadatas', [])
        heroes = [{"id": id, **metadata} for id, metadata in zip(ids, metadatas)]
    else:
        heroes = []
        flash("Failed to retrieve heroes")

    return render_template('unfinishedHeroes.html', heroes=heroes)



@app.route('/generatePersonality', methods=['POST'])
def generatePersonality():
    hero_data = {
        'id': request.form['heroId'],
        'name': request.form['heroName'],
        'text': request.form['heroText'],
        'designation': request.form['heroDesignation']
    }
    current_app.logger.info(f"Received hero data: {hero_data}")

    response = requests.get(chromadb_service_url + "/getStoriesWithHero/" + hero_data['name'])
    if response.status_code == 200:
        stories_response = response.json().get('stories', {})
        stories_documents = stories_response.get('documents', [])
        stories_metadata = stories_response.get('metadatas', [])
        current_app.logger.info(f"Fetched stories documents: {stories_documents}")
        current_app.logger.info(f"Fetched stories metadata: {stories_metadata}")
    else:
        stories_documents = []
        stories_metadata = []
        current_app.logger.error("Failed to fetch stories or none found")

    prompt = f"Generate a detailed description of personality for a fictional hero based on the following data:\n\n"
    prompt += f"Hero Name: {hero_data['name']}\n"
    prompt += f"Hero Description: {hero_data['text']}\n"
    prompt += f"Hero Class/Talent: {hero_data['designation']}\n\n"
    prompt += "Associated Stories:\n"

    # If you want to include the story content in the prompt, iterate through stories_documents
    for story_content in stories_documents:
        prompt += f"{story_content}\n\n"

    # And if you want to include metadata like title and description, iterate through stories_metadata
    for story_info in stories_metadata:
        prompt += f"- Title: {story_info.get('title', 'No title')}\n"
        prompt += f"  Description: {story_info.get('description', 'No description')}\n\n"

    prompt += "\nThe personality description should include a collection of about 5-7 dominant " \
              "personality traits (you may include negative traits) and how the hero goes about their live." \
              "This is very important." \
              "Start your response with 'Personality:' and end it after you have finished describing the personality." \
              "Here is an example how I want the response to look: " \
              "Personality: (list of 5-7 character traits here). \n(description of personality with about 5 " \
              "Sentences here)"

    current_app.logger.info(f"Generated prompt: {prompt}")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai.api_key}"
    }
    current_app.logger.info(f"Sending Data to gpt-4")
    payload = {
        "model": "gpt-4-1106-preview",
        "temperature": 0.8,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 2000
    }

    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        if response.status_code == 200:
            response_json = response.json()
            generated_personality = response_json['choices'][0]['message']['content'] if response_json.get('choices') else 'No content'
            current_app.logger.info(f"Generated personality: {generated_personality}")
        else:
            error_message = f"Error from GPT API: Status Code {response.status_code}, Response: {response.text}"
            current_app.logger.error(error_message)
            generated_personality = f"Error generating personality. API response status: {response.status_code}"
    except requests.exceptions.RequestException as e:
        error_message = f"Request to GPT API failed: {e}"
        current_app.logger.error(error_message)
        generated_personality = f"Error generating personality. Exception: {e}"

    flash(generated_personality)
    return render_template('approvePersonality.html', hero=hero_data, personality=generated_personality)


@app.route('/updateHero', methods=['POST'])
def updateHero():
    hero_data = {
        'id': request.form['heroId'],
        'name': request.form['heroName'],
        'text': request.form['heroText'],
        'designation': request.form['heroDesignation'],
        'personality': request.form['personality']
    }
    # Make POST request to update hero in the database
    response = requests.post(chromadb_service_url + "/updateHero", json=hero_data,
                             headers={'Content-Type': 'application/json'})
    if response.status_code == 200:
        flash('Hero updated successfully!')
    else:
        flash('Failed to update hero.')

    return redirect(url_for('showPlaceholderPersonalities'))

@app.route('/createConversation', methods=['GET'])
def createConversation():
    # Fetch hero names
    response = requests.get(chromadb_service_url + '/getAllHeroes')
    if response.status_code == 200:
        heroes_data = response.json().get('heroes', {}).get('metadatas', [])
        hero_names = [hero['name'] for hero in heroes_data]
    else:
        hero_names = []
        flash("Failed to retrieve heroes")

    return render_template('createConversation.html', hero_names=hero_names)

# TODO query the database for hero interactions
@app.route('/sendConversation', methods=['POST'])
def sendConversation():
    worldbuilding = get_story_documents("The Land of Rathe")
    participatingCharacters = request.form.getlist('selectedHeroes')
    setting = request.form['setting']
    styles = request.form.getlist('selectedStyles')
    style = ', '.join(styles)
    queriedCharacterData = "/getInteractingHeroes?heroes=hero1,hero2,..."

    prompt = ("I want you to write a story set in this world:\n".join(worldbuilding) +
              "\nThe Characters for this story are:\n" + ', '.join(participatingCharacters) +
              "\n\nThe Setting should be " + setting +
              "\nAnd the story should be written to be very " + style + "."
              "\nHere is additional information about the characters: " + queriedCharacterData +
              "\nWrite about 500-1000 words.")

    current_app.logger.info(f"Generated prompt: {prompt}")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai.api_key}"
    }
    current_app.logger.info(f"Sending Data to gpt-4")
    payload = {
        "model": "gpt-4-1106-preview",
        "temperature": 0.8,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 2000
    }

    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        if response.status_code == 200:
            response_json = response.json()
            generated_story = response_json['choices'][0]['message']['content'] if response_json.get('choices') else 'No content'
            current_app.logger.info(f"Generated story: {generated_story}")
        else:
            error_message = f"Error from GPT API: Status Code {response.status_code}, Response: {response.text}"
            current_app.logger.error(error_message)
            generated_story = f"Error generating story. API response status: {response.status_code}"
    except Exception as e:
        current_app.logger.error(f"Error generating story: {e}")
        generated_story = f"Error generating story: {e}"

    return render_template("generatedStory.html", generated_story=generated_story)

def get_story_documents(title):
    url = chromadb_service_url + "/getStory/" + title
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        documents = data.get('story', {}).get('documents', [])
        return documents
    else:
        print("Failed to retrieve story or story not found")
        return []


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8081)
