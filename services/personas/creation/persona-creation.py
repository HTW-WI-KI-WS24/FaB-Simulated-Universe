import requests
from flask import Flask, render_template, request, flash
from openai import OpenAI

client = OpenAI(api_key='insertAPIKeyHere')

app = Flask(__name__)
app.secret_key = "password123"

persona_introduction = ""
persona_writing = ""
name = ""
messages = []
url = 'http://persona-persistence:8082/createPersona'


@app.route("/")
def index():
    flash("What's the Heros name?")
    return render_template("enter_name.html")


@app.route("/getIntroduction", methods=["POST"])
def getIntroduction():
    global name
    name = request.form.get("user_input")
    flash("Okay, let's create a Persona for " + name + ". Please insert a paragraph about the hero (e.g. from "
                                                       "their hero page) to describe their character traits.")
    return render_template("hero_introduction.html")


@app.route("/addBiography", methods=["POST"])
def getWritingStyle():
    global heroIntroduction
    heroIntroduction = request.form.get("user_input")
    flash(
        "Hero: " + name + "\n Please insert Stories from the Heros Lore Page here.")
    return render_template("bio_stories.html")

@app.route("/addTraits", methods=["POST"])
def generateDepth():
    global heroBiography
    heroBiography = request.form.get("user_input")
    flash("Persona: " + name + "\n Please insert character traits for this Hero.")
    return render_template("character_traits.html")

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
    requests.post(url, json=data)
    # Return the generated article content
    flash("Persona: " + name + "\n" + chat.choices[0].message.content)

    return render_template("generate_persona_prompt.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
