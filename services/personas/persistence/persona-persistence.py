import chromadb
import requests
import logging
from flask import Flask, jsonify, request
from chromadb.utils import embedding_functions

chroma_client = chromadb.PersistentClient(path="/var/lib/chromadb")
default_ef = embedding_functions.DefaultEmbeddingFunction()
chroma_client.delete_collection(name="heroes")
fabCollection = chroma_client.get_or_create_collection(name="heroes", embedding_function=default_ef)


app = Flask(__name__)

last_id = 0


def get_next_id():
    global last_id
    last_id += 1
    return last_id


@app.route('/pullscrapedHeroes', methods=['POST'])
def pullScrapedHeroes():
    try:
        data = request.get_json()
        if not data:
            return "No data received", 400

        for hero in data:
            ### check if already exists
            results = fabCollection.get(
                where={"text": hero['text']},
                include=["metadatas"]
            )
            if len(results["ids"]) > 0:
                print("Hero already exists. Skipping...")
            else:
                hero_id = get_next_id()
                fabCollection.add(
                    documents=["The Heros name is " + hero['name'] + ". They have the following short description: " +
                               hero['text'] + ". Their Talent/Class is " + hero['designation'] + "."],
                    metadatas=[{"kind": "hero", "name": hero['name'], "text": hero['text'], "designation": hero['designation'],
                                "personality": "Placeholder"}],
                    ids=[str(hero_id)]
                )
                logging.info(f"Hero added to ChromaDB Collection with ID: {hero_id}")

        return jsonify({'message': 'Hero data pulled successfully', 'heroesData': data})
    except Exception as e:
        logging.error(f"Error while processing heroes: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/pullscrapedStories', methods=['POST'])
def pullScrapedStories():
    try:
        data = request.get_json()
        if not data:
            return "No data received", 400

        for story in data:
            ### check if already exists
            results = fabCollection.get(
                where={"title": story['title']},
                include=["metadatas"]
            )
            if len(results["ids"]) > 0:
                print("Story already exists. Skipping...")
            else:
                story_id = get_next_id()
                # Prepare metadata with title and description
                metadata = {"kind": "story", "title": story['title'], "description": story['description']}
                # Add each hero as a key-value pair in metadata
                if 'heroes' in story:
                    for hero in story['heroes']:
                        metadata[hero.lower()] = hero

                # Add the story with updated metadata to fabCollection
                fabCollection.add(
                    documents=[story['text']],
                    metadatas=[metadata],
                    ids=[str(story_id)]
                )
                logging.info(f"Story added with ID: {story_id}")

        return jsonify({'message': 'Story data pulled successfully', 'storiesData': data})
    except Exception as e:
        logging.error(f"Error while processing stories: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/createHero', methods=['POST'])
def createPersona():
    data = request.get_json()
    # Hinzufügen des Persona-Dokuments und seiner Embeddings zur ChromaDB-Collection
    fabCollection.add(
        documents=[data['text']],
        metadatas=[{"name": data['name']}],
        ids=[]
    )
    return jsonify({'message': 'Persona created successfully', 'personaData': data})


@app.route('/getAllHeroes', methods=['GET'])
def getAllHeroes():
    # Abfragen aller Personas in der Collection
    heroes = fabCollection.get(
        where={"kind": "hero"}
    )
    print(heroes)
    return jsonify({'heroes': heroes})


@app.route('/getAllStories', methods=['GET'])
def getAllStories():
    # Abfragen aller Personas in der Collection
    stories = fabCollection.get(
        where={"kind": "story"}
    )
    return jsonify({'stories': stories})


@app.route('/getHero/<name>', methods=['GET'])
def getHero(name):
    # Durchführen einer Abfrage basierend auf dem Namen der Persona
    result = fabCollection.get(
        where={'name': name},
    )
    if result:
        return jsonify({'hero': result})
    else:
        print("no result")
        return jsonify({'message': 'hero not found'}), 404


@app.route('/getStory/<title>', methods=['GET'])
def getStory(title):
    result = fabCollection.get(
        where={'title': title},
    )
    if result:
        return jsonify({'story': result})
    else:
        return jsonify({'message': 'story not found'}), 404


@app.route('/getStoryWithHero/<name>', methods=['GET'])
def getStoryWithHero(name):
    result = fabCollection.query(
        query_texts=["*"],
        where={'heroes': {'$eq': name}},
        n_results=99
    )
    if result:
        return jsonify({'story': result})
    else:
        return jsonify({'message': 'story not found'}), 404


# deletemethoden noch implementieren
@app.route('/deleteAllHeroes', methods=['GET'])
def deleteAllHeroes():
    return jsonify({'message': 'heroes successfully deleted'})


@app.route('/deleteAllStories', methods=['GET'])
def deleteAllStories():
    return jsonify({'message': 'stories successfully deleted'})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8082)

"""


# embeddings?? -> noch nicht angeschaut
hero_embeddings = [
    [1.2, 2.3, 4.5],  # Vektorrepräsentation für Hero 1??
    [6.7, 8.2, 9.2]   # Vektorrepräsentation für Hero 2??
]

hero_documents = [
    "Arakni ,No-one escapes Southmaw. No-one except Patient 1413.The feral orphan, taken and tormented to the point of no return. The silent prodigy transformed into an expression of graceful violence.."    # Beschreibung für Charakter 1
    "Data Doll, Buried deep beneath Iron Assembly headquarters there lies a vast, secret chamber. Inside rests Data Doll, a steam-powered automaton delicately suspended by a web of wires and hoses..."  # Beschreibung für Charakter 2
]

hero_metadata = [
    {"name": "Arakni", "titel": "Solitary Confinement", "typ": "Assassin"},  # Metadaten für Charakter 1
    {"name": "Data Doll", "titel": "MKII", "typ": "Mechanologist"}  # Metadaten für Charakter 2
]

hero_ids = ["hero1", "hero2"]  # Eindeutige IDs für die Charaktere


collection.add(
    embeddings=hero_embeddings,
    documents=hero_documents,
    metadatas=hero_metadata,
    ids=hero_ids
)

collection = dbClient.create_collection(name="stories")







# Beispielabfrage
abfrage_text = "Arakni"
abfrage_ergebnisse = collection.query(
    query_texts=[abfrage_text],
    n_results=2
)

# Ergebnisse der Abfrage
for result in abfrage_ergebnisse:
    print(f"ID: {result['id']}, Dokument: {result['document']}, Score: {result['score']}")


#class Hero:
#   def __init__(self, id, name, beschreibung, vektor):
#        self.id = id
#        self.name = name
#        self.beschreibung = beschreibung
#        self.vektor = vektor

#def addHero(hero):
#    dbClient.insert(hero.id, hero.vektor, hero.__dict__)

#def retrieveHero(name):
#    ergebnis = dbClient.search("name:{}".format(name))
#    return ergebnis

#def updateHero(id, newData):
#    dbClient.update(id, newData)

#def deleteHero(id):
#    dbClient.delete(id)
"""
