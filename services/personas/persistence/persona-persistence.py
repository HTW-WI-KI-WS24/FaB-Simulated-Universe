import os

import chromadb
from flask import Flask, jsonify, request, current_app, send_from_directory
from chromadb.utils import embedding_functions
import json

chroma_client = chromadb.PersistentClient(path="/var/lib/chromadb")
default_ef = embedding_functions.DefaultEmbeddingFunction()
#chroma_client.delete_collection(name="heroes")
fabCollection = chroma_client.get_or_create_collection(name="heroes", embedding_function=default_ef)
# testCollection = chroma_client.get_or_create_collection(name="test", embedding_function=default_ef)

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
                    metadatas=[
                        {"kind": "hero", "name": hero['name'], "text": hero['text'], "designation": hero['designation'],
                         "personality": "Placeholder"}],
                    ids=[str(hero_id)]
                )
                current_app.logger.info(
                    f"Hero added to ChromaDB Collection with ID: {hero_id} and Name: {hero['name']}")

        return jsonify({'message': 'Hero data pulled successfully', 'heroesData': data})
    except Exception as e:
        current_app.logger.error(f"Error while processing heroes: {e}")
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
                current_app.logger.info(f"Story added with ID: {story_id} and Title: {story['title']}")

        return jsonify({'message': 'Story data pulled successfully', 'storiesData': data})
    except Exception as e:
        current_app.logger.error(f"Error while processing stories: {e}")
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
    return jsonify({'message': 'Hero created successfully', 'heroData': data})


@app.route('/getAllHeroes', methods=['GET'])
def getAllHeroes():
    # Abfragen aller Personas in der Collection
    heroes = fabCollection.get(
        where={"kind": "hero"}
    )
    print(heroes)
    return jsonify({'heroes': heroes})


@app.route('/getAllPlaceholders', methods=['GET'])
def getAllPlaceholders():
    heroes = fabCollection.get(
        where={"personality": "Placeholder"}
    )
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
        include=['embeddings', 'documents', 'metadatas']
    )
    if result:
        return jsonify({'hero': result})
    else:
        print("no result")
        return jsonify({'message': 'hero not found'}), 404

@app.route('/getInteractingHeroes', methods=['GET'])
def getInteractingHeroes():
    heroes = request.args.get('heroes')
    if heroes:
        heroes_list = heroes.split(',')
        promt = "What interactions did " + heroes_list[0]
        if len(heroes_list) > 1:
            promt += " and " + " and ".join(heroes_list[1:])
        promt += " have?"
        try:
            result = fabCollection.query(query_texts=[promt])
            current_app.logger.info(f"Query-promt sent to DB: {promt}")
            if result:
                return jsonify({'interaction between ' + heroes: result})
            else:
                print("no result")
                return jsonify({'error': 'The query call returned no result'}), 404
        except Exception as e:
            error_message = f"Query-request to GPT API failed: {e}"
            current_app.logger.error(error_message)
            return jsonify({'error': error_message}), 500
    else:
        print("No heroes provided")
        return jsonify({'error': 'No heroes provided'}), 400


@app.route('/getStory/<title>', methods=['GET'])
def getStory(title):
    result = fabCollection.get(
        where={'title': title},
    )
    if result:
        return jsonify({'story': result})
    else:
        return jsonify({'message': 'story not found'}), 404


@app.route('/getStoriesWithHero/<name>', methods=['GET'])
def getStoryWithHero(name):
    result = fabCollection.get(
        where={name.lower(): name},
        include=['embeddings', 'documents', 'metadatas']
    )
    if result:
        return jsonify({'stories': result})
    else:
        return jsonify({'message': 'story not found'}), 404


@app.route('/updateHero', methods=['POST'])
def updateHero():
    data = request.get_json()
    # Normalize line endings in the personality text
    personality_clean = data['personality'].replace('\r\n', ' ')

    fabCollection.update(
        ids=[data['id']],
        documents=[
            "The Hero's name is " + data['name'] + ". They have the following short description: " +
            data['text'] + ". Their Talent/Class is " + data['designation'] +
            ". " + personality_clean  # Use the cleaned personality text here
        ],
        metadatas=[
            {
                "kind": "hero",
                "name": data['name'],
                "text": data['text'],
                "designation": data['designation'],
                "personality": "added"
            }
        ]
    )
    return jsonify({'message': 'Hero updated successfully'}), 200


@app.route('/deleteAllHeroes', methods=['DELETE'])
def deleteAllHeroes():
    fabCollection.delete(where={"kind": "hero"})
    return jsonify({'message': 'heroes successfully deleted'})


@app.route('/deleteHeroByName/<name>', methods=['DELETE'])
def deleteHeroByName(name):
    fabCollection.delete(where={"name": name})
    return jsonify({'message': 'hero successfully deleted'})


@app.route('/deleteAllStories', methods=['DELETE'])
def deleteAllStories():
    fabCollection.delete(where={"kind": "story"})
    return jsonify({'message': 'stories successfully deleted'})


@app.route('/deleteCollection/<name>', methods=['DELETE'])
def deleteColletion(name):
    chroma_client.delete_collection(name=name)
    return jsonify({'message': 'collection ' + name + ' successfully deleted'})


@app.route('/getCollection/<name>', methods=['GET'])
def getCollection(name):
    return jsonify({'collection': chroma_client.get_collection(name=name, embedding_function=default_ef).get()})


@app.route('/exportCollection/<name>', methods=['GET'])
def saveCollection(name):
    try:
        # Fetch the collection data
        collection_response = chroma_client.get_collection(name=name).get()
        current_app.logger.info(f"Collection response: {collection_response}")

        # Assuming collection_response is the actual data you want to save:
        collection_data = collection_response

        # Set up the file path for saving
        file_name = f"{name}_collection.json"
        collections_folder = os.path.join(os.path.dirname(__file__), 'collections')
        if not os.path.exists(collections_folder):
            os.makedirs(collections_folder)
        file_path = os.path.join(collections_folder, file_name)

        # Save the data to a file
        with open(file_path, 'w') as file:
            json.dump(collection_data, file, indent=4)

        # Send the file for download
        jsonify({'message': 'Data downloaded. Check your Downloads Folder and manually put the file into the '
                            'collections folder located in the persistence directory of this project.'})
        return send_from_directory(directory=collections_folder, path=file_name, as_attachment=True)
    except Exception as e:
        current_app.logger.error(f"Error saving collection data: {str(e)}")
        return jsonify({'error': 'Failed to save collection data'}), 500


@app.route('/importCollection/<name>', methods=['POST'])
def loadCollection(name):
    try:
        # Set up the file path for loading
        file_name = f"{name}_collection.json"
        collections_folder = os.path.join(os.path.dirname(__file__), 'collections')
        file_path = os.path.join(collections_folder, file_name)

        # Load the data from the file
        with open(file_path, 'r') as file:
            collection_data = json.load(file)

        # Extract the documents, IDs, and metadatas
        documents = collection_data.get('documents', [])
        metadatas = collection_data.get('metadatas', [])
        ids = collection_data.get('ids', [])

        # Check if data is valid
        if not documents or not metadatas or not ids:
            raise ValueError("Missing documents, metadatas, or ids in the collection data")

        # Add the data to the collection
        fabCollection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        return jsonify({'message': f'Successfully imported collection data from {file_name}'}), 200

    except FileNotFoundError:
        return jsonify({'error': 'Collection file not found'}), 404
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error loading collection data: {str(e)}")
        return jsonify({'error': 'Failed to load collection data'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8082)
