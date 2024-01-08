import chromadb
import requests
import logging
from flask import Flask, jsonify, request

# from chromadb.utils import embedding_functions

#chroma_client = chromadb.Client()
chroma_client = chromadb.PersistentClient(path="/var/lib/chromadb")

heroesCollection = chroma_client.get_collection(name="heroes")
if heroesCollection is None:
    heroesCollection = chroma_client.create_collection(name="heroes")

storiesCollection = chroma_client.get_collection(name="stories")
if storiesCollection is None:
    storiesCollection = chroma_client.create_collection(name="stories")

app = Flask(__name__)

last_id = 0


def get_next_id():
    global last_id
    last_id += 1
    return last_id


@app.route('/pullscrapedHeroes', methods=['POST'])
def pullingScrapedHeroes():
    try:
        data = request.get_json()
        if not data:
            return "No data received", 400

        for hero in data:
            hero_id = get_next_id()
            heroesCollection.add(
                documents=[hero['text']],
                metadatas=[{"name": hero['name'], "designation": hero['designation']}],
                ids=[str(hero_id)]
            )
            logging.info(f"Hero added with ID: {hero_id}")

        return jsonify({'message': 'heroesdata pulled successfully', 'heroesData': data})
    except Exception as e:
        logging.error(f"Error while processing heroes: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/pullscrapedStories', methods=['POST'])
def pullingScrapedStories():
    try:
        data = request.get_json()
        if not data:
            return "No data received", 400

        for story in data:
            story_id = get_next_id()
            storiesCollection.add(
                documents=[story['text']],
                metadatas=[{"title": story['title'], "description": story['description'],
                            'heroes': ', '.join(story['heroes']) if story['heroes'] else ""}],
                ids=[str(story_id)]
            )
            logging.info(f"Story added with ID: {story_id}")

        return jsonify({'message': 'storiesdata pulled successfully', 'storiesData': data})
    except Exception as e:
        logging.error(f"Error while processing stories: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/createPersona', methods=['POST'])
def createPersona():
    data = request.get_json()
    # Hinzufügen des Persona-Dokuments und seiner Embeddings zur ChromaDB-Collection
    heroesCollection.add(
        documents=[data['text']],
        metadatas=[{"name": data['name']}],
        ids=[]
    )
    return jsonify({'message': 'Persona created successfully', 'personaData': data})


@app.route('/getAllHeroes', methods=['GET'])
def getAllHeroes():
    # Abfragen aller Personas in der Collection
    heroes = heroesCollection.query(
        query_texts=["*"],
        n_results=50
    )
    return jsonify({'heroes': heroes})


@app.route('/getAllStories', methods=['GET'])
def getAllStories():
    # Abfragen aller Personas in der Collection
    stories = storiesCollection.query(
        query_texts=["*"],
        n_results=50
    )
    return jsonify({'stories': stories})


@app.route('/getHero/<name>', methods=['GET'])
def getHero(name):
    # Durchführen einer Abfrage basierend auf dem Namen der Persona
    result = heroesCollection.query(
        query_texts=["*"],
        where={'name': name},
        n_results=1
    )
    result.values()
    if result:
        print(result)
        return jsonify({'hero': result.values()})
    else:
        print("no result")
        return jsonify({'message': 'hero not found'}), 404


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8082)


@app.route('/getStory/<title>', methods=['GET'])
def getStory(title):
    # Durchführen einer Abfrage basierend auf dem Namen der Persona
    result = storiesCollection.query(
        query_texts=[title],
        n_results=1
    )
    if result:
        return jsonify({'story': result[0]})
    else:
        return jsonify({'message': 'story not found'}), 404


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8082)

"""
@app.route('/pullscrapedHeroes', methods=['POST'])
def pullingScrapedHeroes():
    data = request.get_json()
    if data:
        for hero in data:
            personaCollection.add(
                documents=[hero['text']],
                metadatas=[{"name": hero['name'], "designation": hero['designation']}],
                ids=[last_id + 1]
            )
            print(f"Name: {hero['name']}")
            print(f"Designation: {hero['designation']}")
            print(f"Text: {hero['text']}\n")
        return jsonify({'message': 'heroesdata pulled successfully', 'heroesData': data})
    else:
        return "No data received", 400




@app.route('/pullscrapedHeroes')
def pullingScrapedData():
    url = 'http://localhost:8080/scrapeHeroes'
    try:
        response = requests.get(url)

        if response.status_code == 200:
          result = response.json()
          heroes = result.get("heroes", [])
        else:
            print(f"error: {response.status_code}")
    except requests.RequestException as e:
        print(f"Error during request: {str(e)}")
    if heroes:
        for hero in heroes:
            personaCollection.add(
                documents=[hero['text']],
                metadatas=[{"name": hero['name'], "designation": hero['designation']}],
                ids=[last_id + 1]
            )
            print(f"Name: {hero['name']}")
            print(f"Designation: {hero['designation']}")
            print(f"Text: {hero['text']}\n")
    return jsonify({'message': 'heroesdata pulled successfully', 'heroesData': heroes})












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
