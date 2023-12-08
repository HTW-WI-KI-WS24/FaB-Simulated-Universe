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
    global personaIntroduction
    personaIntroduction = request.form.get("user_input")
    flash(
        "Hero: " + name + "\n Please insert Stories from the Heros Lore Page here.")
    return render_template("bio_stories.html")

@app.route("/addTraits", methods=["POST"])
def generateDepth():
    messages.append({"role": "user", "content": request.form.get("user_input")})
    print(messages)
    assistant_reply = generate_depth(client, messages)
    flash("Persona: " + name + "\n" + assistant_reply)
    return render_template("character_traits.html")

# TODO: Change Creation Process based on Hero Data and Stories from http://fabtcg.com/heroes
#       and http://fabtcg.com/stories
@app.route("/generateQuestions", methods=["POST"])
def generateQuestions():
    global personaStories
    global personaIntroduction
    personaStories = request.form.get("user_input")
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
                                 f"as a person: {personaIntroduction}"
                                 f"Here are some of their character traits: {characterTraits}"
                                 "Here are some articles that are stories from their biography. "
                                 "Each article starts with the phrase “*START OF ARTICLE*” and ends with the phrase "
                                 "“*END OF ARTICLE*”: "
                                 f"{personaStories}"
                      }

    # List to store conversation messages
    global messages
    messages = [system_message]

    # Generate 5 questions based on the system message prompt
    assistant_reply = generate_questions(client, system_message)

    flash("Persona: " + name + "\n" + assistant_reply)
    return render_template("generate_questions.html")

@app.route("/describeExperience", methods=["POST"])
def describeExperience():
    messages.append({"role": "user", "content": request.form.get("user_input")})
    flash(
        "Persona: " + name + "\n" + "Please describe a difficult situation the hero has experienced with another "
                                    "person. The model will try to imitate how you would've handled a conflict or "
                                    "situation. If the model handled the situation similar "
                                    "to the hero, please confirm it with 'confirm action'. Otherwise, please tell the "
                                    "model how they handled the situation you have described")
    return render_template("describe_experience.html")


@app.route("/simulatePersonaExperience", methods=["POST"])
def simulatePersonaExperience():
    persona_experience = (request.form.get("user_input"))
    messages.append({"role": "user",
                     "content": "I am going to describe you a situation that the hero has experienced. While "
                                "pretending to be them, describe how they would have handled the situation from a "
                                "first-person-perspective. Here is the situation: " +
                                persona_experience + "End of Situation" + ".\n Now please pretend to be them."})

    # Model responds as if it were the user in that situation
    model_response = client.chat.completions.create(
        model="gpt-3.5-turbo", messages=messages
    )

    flash("Persona: " + name + "\n" + f"The model's response: {model_response.choices[0].message.content} "
                                      "Is this correct? (Type 'confirm action' to confirm or describe what you "
                                      "have done if the model didn't handle your situation similarly): "
          )
    return render_template("simulate_persona_experience.html")


@app.route("/checkPersonaExperience", methods=["POST"])
def checkPersonaExperience():
    confirmation = (request.form.get("user_input"))
    confirmed = False
    while not confirmed:
        if confirmation.lower() == "confirm action":
            confirmed = True
        else:
            messages.append({"role": "user",
                             "content": "No I have reacted this way:" + confirmation + ". Please try to adapt your "
                                                                                       "description to how i have "
                                                                                       "handled it"})
            # Model responds as if it were the user in that situation
            model_response = client.chat.completions.create(
                model="gpt-3.5-turbo", messages=messages
            )
            flash("Persona: " + name + "\n" + f"The model's response: {model_response.choices[0].message.content}")
            return render_template("simulate_persona_experience.html")

    messages.append(
        {"role": "user",
         "content": "Now, write a thorough description of a persona that captures the personality and "
                    "how the persona handles situations. Include both positive and controversial "
                    "character traits."})
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


def generate_depth(client, messages):
    # Convert the system_message to a list of messages
    messages.append(
        {"role": "user", "content": "now that i have answered your questions. Please ask 5 question for that "
                                    "persona to add more depth by asking about his dislikes or controversial "
                                    "character traits. You can base these new questions on the answers or create new "
                                    "questions to add more depth to the persona by asking about his dislikes or "
                                    "controversial character traits"})

    # Generate questions based on the system message prompt
    chat = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
    )
    # Return the generated questions
    return chat.choices[0].message.content


def generate_questions(client, system_message):
    # Convert the system_message to a list of messages
    messages = [{"role": "system", "content": system_message["content"]}]

    # Generate questions based on the system message prompt
    chat = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
    )
    # Return the generated questions
    return chat.choices[0].message.content


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
