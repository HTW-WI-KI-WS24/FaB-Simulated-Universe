import os
import uuid

import chromadb
from flask import Flask, jsonify, request, current_app, send_from_directory
from chromadb.utils import embedding_functions
import json

chroma_client = chromadb.PersistentClient(path="/var/lib/chromadb")
default_ef = embedding_functions.DefaultEmbeddingFunction()
# chroma_client.delete_collection(name="heroes")
fabCollection = chroma_client.get_or_create_collection(name="heroes", embedding_function=default_ef)
# testCollection = chroma_client.get_or_create_collection(name="test", embedding_function=default_ef)
app = Flask(__name__)


@app.route('/createHero', methods=['POST'])
def createPersona():
    data = request.get_json()
    # Hinzufügen des Persona-Dokuments und seiner Embeddings zur ChromaDB-Collection
    fabCollection.add(
        documents=[data['text']],
        metadatas=[{"name": data['name']}],
        ids=[data['ids']]
    )
    return jsonify({'message': 'Hero created successfully', 'heroData': data})


@app.route('/saveStory', methods=['POST'])
def saveStory():
    data = request.get_json()  # Retrieve JSON payload from the request
    current_app.logger.info(f"Received story: {data} Saving...")
    try:
        # Assuming fabCollection.add is properly implemented to handle adding the story to the database
        fabCollection.add(
            documents=data['documents'],
            metadatas=data['metadatas'],
            ids=data['ids']
        )
        current_app.logger.info(f"Story saved successfully.")
        return jsonify({'message': 'Story saved successfully', 'storyData': data})
    except Exception as e:
        current_app.logger.error(f"Error saving story: {e}")
        return jsonify({'error': str(e)}), 500


# To get all heroes: GET /getHeroes
# To get a specific hero by name: GET /getHeroes?name=[hero_name]
# To get heroes without generated personality: GET /getHeroes?personality=Placeholder
@app.route('/getHeroes', methods=['GET'])
def getHeroes():
    name = request.args.get('name', default=None)
    personality = request.args.get('personality', default=None)

    # Choosing the query based on parameters
    if name:
        query = {'name': name}
    elif personality:
        query = {'personality': personality}
    else:
        query = {'kind': 'hero'}

    # Fetching heroes based on the constructed query
    heroes = fabCollection.get(where=query)
    return jsonify({'heroes': heroes})


# To get all stories: GET /getStories
# To get all official stories: GET /getStories?origin=official
# To get all generated stories: GET /getStories?origin=generated
# To get all stories with a specific hero: GET /getStories?hero=[hero_name]
# To get a story by title: GET /getStories?title=[title]
@app.route('/getStories', methods=['GET'])
def getStories():
    origin = request.args.get('origin', default=None)
    hero_name = request.args.get('hero', default=None)
    title = request.args.get('title', default=None)

    # Choose the query based on parameters
    if hero_name:
        query = {hero_name.lower(): hero_name}
    elif origin:
        query = {'origin': origin}
    elif title:
        query = {'title': title}
    else:
        query = {'kind': 'story'}

    # Fetching stories based on the constructed query
    stories = fabCollection.get(where=query)
    return jsonify({'stories': stories})


# To get all world data: GET /getWorldData
# To get world data for a specific region: GET /getWorldData?region=[region_name]
@app.route('/getWorldData', methods=['GET'])
def getWorldData():
    region = request.args.get('region', default=None)

    # Choose the query based on parameters
    if region:
        query = {'region': region}
    else:
        query = {'kind': 'regionData'}

    # Fetching world data based on the constructed query
    worldData = fabCollection.get(where=query)
    return jsonify({'worldData': worldData})


@app.route('/getInteractingHeroes', methods=['GET'])
def getInteractingHeroes():
    heroes = request.args.get('heroes')
    if not heroes:
        current_app.logger.info("No heroes provided")
        return jsonify({'error': 'No heroes provided'}), 400

    heroes_list = heroes.split(',')
    prompt = "Identify narratives where " + " and ".join(heroes_list) + " appear in the same context."

    try:
        # https://docs.trychroma.com/usage-guide#querying-a-collection
        result = fabCollection.query(
            query_texts=[prompt],
            n_results=3,
            # where={"metadata_field": "is_equal_to_this"},
            # where_document={"$contains":"search_string"}
        )
        current_app.logger.info(f"Query sent to DB: {prompt}")

        if result:
            return jsonify({'interactions between: ' + heroes: result})
        else:
            current_app.logger.info("Query call returned no result")
            return jsonify({'error': 'The query call returned no result'}), 404
    except Exception as e:
        error_message = f"Query-request to DB failed: {e}"
        current_app.logger.error(error_message)
        return jsonify({'error': error_message}), 500


@app.route('/queryChromaDB', methods=['POST'])
def query_chroma_db():
    try:
        data = request.get_json()
        query_texts = data.get('query_texts', [])
        n_results = data.get('n_results', 10)

        current_app.logger.info(f"Received query parameters: {data}")

        # The where and where_document conditions are optional
        where_conditions = data.get('where', None)  # Default to None if not provided
        where_document_conditions = data.get('where_document', None)  # Default to None if not provided
        include_conditions = data.get('include', None)  # Default to None if not provided

        # Construct the query arguments, excluding None values
        query_args = {
            'query_texts': query_texts,
            'n_results': n_results
        }
        if where_conditions is not None:
            query_args['where'] = where_conditions
        if where_document_conditions is not None:
            query_args['where_document'] = where_document_conditions
        if include_conditions is not None:
            query_args['include'] = include_conditions

        current_app.logger.info(f"Sending query to chroma with arguments: {query_args}")

        result = fabCollection.query(**query_args)

        current_app.logger.info(f"Query result: {result}")

        if result and result.get('documents'):
            # Return the successful query result
            return jsonify(result), 200
        else:
            current_app.logger.info("No results found for the given query")
            return jsonify({'message': 'No results found for the given query'}), 200

    except Exception as e:
        # Log the error and return an error message
        current_app.logger.error(f"An error occurred while querying the database: {e}")
        return jsonify({'error': str(e)}), 500


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


@app.route('/deleteAllWorldData', methods=['DELETE'])
def deleteAllWorldData():
    fabCollection.delete(where={"kind": "regionData"})
    return jsonify({'message': 'World Data deleted successfully.'})


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


@app.route('/pullScrapedWorld', methods=['POST'])
def pullScrapedWorld():
    try:
        data = request.get_json()
        if not data:
            return "No data received", 400

        for region in data:
            ### check if already exists
            results = fabCollection.get(
                where={"text": region['text']},
                include=["metadatas"]
            )
            if len(results["ids"]) > 0:
                print("Region Data already exists. Skipping...")
            else:
                regionData_id = generate_uuid(region['text'])
                fabCollection.add(
                    documents=[region['text']],
                    metadatas=[{"kind": "regionData", "region": region['name']}],
                    ids=[regionData_id]
                )
                current_app.logger.info(
                    f"Region Data added to ChromaDB Collection with UUID: {regionData_id} from Region: {region['name']} "
                    f"and Text: {region['text']}")
        return jsonify({'message': 'World data received successfully', 'worldData': data})
    except Exception as e:
        current_app.logger.error(f"Error while processing World Data: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/pullScrapedHeroes', methods=['POST'])
def pullScrapedHeroes():
    try:
        data = request.get_json()
        if not data:
            return "No data received", 400

        for hero in data:
            # check if already exists
            results = fabCollection.get(
                where={"text": hero['text']},
                include=["metadatas"]
            )
            if len(results["ids"]) > 0:
                print("Hero already exists. Skipping...")
            else:
                hero_id = generate_uuid(hero['text'])
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

        return jsonify({'message': 'Hero data received successfully', 'heroesData': data})
    except Exception as e:
        current_app.logger.error(f"Error while processing heroes: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/pullScrapedStories', methods=['POST'])
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
                story_id = generate_uuid(story['title'])
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

        return jsonify({'message': 'Story data received successfully', 'storiesData': data})
    except Exception as e:
        current_app.logger.error(f"Error while processing stories: {e}")
        return jsonify({'error': str(e)}), 500


def generate_uuid(name):
    # Generate a UUID based on the SHA-1 hash of a namespace identifier and a name
    name_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, name)
    return str(name_uuid)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8082)
