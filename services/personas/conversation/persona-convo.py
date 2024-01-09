from flask import Flask, request, flash, render_template, redirect, url_for
import requests
from openai import OpenAI

client = OpenAI(
    api_key='insertAPIKeyHere'
)

app = Flask(__name__)
app.secret_key = "password123"

chromadb_service_url = 'http://persona-persistence:8082'
getPersonaUrl = 'http://persona-persistence:8082/getHero/'
personaList = []


@app.route('/')
def showPlaceholderPersonalities():
    response = requests.get(chromadb_service_url + "/getAllPlaceholders")
    if response.status_code == 200:
        data = response.json()
        heroes = data.get('heroes', {}).get('metadatas', [])
    else:
        heroes = []
        flash("Failed to retrieve heroes")

    return render_template('unfinishedHeroes.html', heroes=heroes)

# TODO
@app.route('/generatePersonality', methods=['POST'])
def generatePersonality():
    hero_data = {
        'id': request.form['heroId'],
        'name': request.form['heroName'],
        'text': request.form['heroText'],
        'designation': request.form['heroDesignation']
    }
    # Code to call GPT-API and generate personality
    # Assume personality is stored in 'generated_personality'

    return render_template('approvePersonality.html', hero=hero_data, personality=generated_personality)



@app.route('/updateHero', methods=['POST'])
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
    response = requests.post("http://localhost:8082/updateHero", json=hero_data, headers={'Content-Type': 'application/json'})
    if response.status_code == 200:
        flash('Hero updated successfully!')
    else:
        flash('Failed to update hero.')

    return redirect(url_for('showPlaceholderPersonalities'))


@app.route('/createConversation', methods=['POST'])
def createConversation():
    response1 = requests.get(getPersonaUrl + request.form.get("persona1"))
    personaData = response1.json()["persona"]
    savedData = {
        "username": personaData["name"],
        "biography": personaData["biography"]
    }
    savedName2 = savedData["name"]
    savedBiography = savedData["biography"]

    response2 = requests.get(getPersonaUrl + request.form.get("persona2"))
    persona_data2 = response2.json()["persona"]
    saved_data2 = {
        "name": persona_data2["name"],
        "biography": persona_data2["biography"]
    }
    savedName = saved_data2["name"]
    savedBiography2 = saved_data2["biography"]

    prompt = (
        f"I will describe two fictional people for you with a Name and a Biography. Please emulate a conversation "
        f"between both auf these people, based on their biography. The conversation should include around 5 "
        f"messages from each person and the person has to think of a question that suits to keep the "
        f"conversation going. The question should include something personal, view on future plans, "
        f"how they would handle a situation, morality to make the conversation deeper. Let them ask question and "
        f"engage in a conversation that could result in a conflict of interest. Person 1 is: {savedName} "
        f"and the biography is: {savedBiography}.Person 2 is: {savedName2} and the biography is:"
        f"{savedBiography2}. After the conversation, give a quick statement on whether the two persons "
        f"would understand each-other well or not, and if so, why not. Also explain where they have common "
        f"interest or if there "
        f"is a deeper connection. Or which topics or views on life could be potential conflicts for the "
        f"relationships. For the conversation, dont say yes to everything but stay critical in the conversation "
        f"to let the personas stay in character. If you are missing information about that persona do not make "
        f"up things to keep the conversation going.")

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user",
                   "content": prompt}],
        temperature=0.2
    )

    answer = response.choices[0].message.content
    flash(answer)
    return render_template("result.html")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8081)
