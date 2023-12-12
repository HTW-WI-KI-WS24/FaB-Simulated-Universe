import chromadb
from chromadb.utils import embedding_functions
dbClient = chromadb.Client()

import chromadb

collection = dbClient.create_collection(name="heros")

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
abfrage_text = "Arkani"
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
