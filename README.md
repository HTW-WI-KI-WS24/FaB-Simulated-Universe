[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-24ddc0f5d75046c5622901739e7c5dd533143b0c8e959d652212380cedb1ea36.svg)](https://classroom.github.com/a/cVeImKGm)

### Team Members
Name              -  Student Number
```
Max Herget        -  0580332
Nicolas Marantos  -  0579813
Leon Schüßler     -  0579906
```

# Flesh and Blood Simulated Universe

Welcome to the Flesh and Blood Simulated Universe - a place where epic tales and legendary heroes come to life!

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:
- Docker/Docker Desktop
- Docker Compose

### Environment Setup

1. Clone the repository to your local machine.
2. Navigate to the project root directory.
3. Create a `.env` file with the necessary environment variables:

   ```shell
   OPENAI_API_KEY=<Your OpenAI API Key>
   APP_SECRET_KEY=<Your Application Secret Key>
   ```

### Build and Run

Run the following command to build and start the Docker containers:

```shell
docker-compose up --build -d
```

This will set up all necessary services, including the backend, ChromaDB, and any other required components.

### Initialize Database

After the containers are up and running, initialize the database:

- Access the `localhost:8082/heroes/importCollection/heroes` endpoint in your browser. This loads the data into the "heroes" collection in your ChromaDB (that's the one with Chromas default Embeddings).
- If you wish to load the data with OpenAIs Embeddings as well, access the `localhost:8082/openai/importCollection/heroes` endpoint.
- If you want to import a different name_collection.json, or load it into a different created Collection, just use this syntax:
- `localhost:8082/<chroma_collection_name>/importCollection/<filename_before_collection.json>`

### Using different Embeddings

If you want to use different Embeddings, please refer to [this Notebook by Chroma](https://github.com/chroma-core/chroma/blob/main/examples/basic_functionality/alternative_embeddings.ipynb).


## Features

- **Personality Generation**: Create unique hero profiles with rich backstories and attributes based on existing stories.
- **Story Generation**: Generate captivating stories involving the heroes and existing World Data.
- **Question Asking**: Ask Questions about the current State of the Universe.

## To-Do Roadmap

- [ ] Information Adding Feature
- [ ] Allow User Editing of Ratings
- [ ] Use [SelfQueryRetriever from LangChain](https://python.langchain.com/docs/integrations/retrievers/self_query/chroma_self_query) to query over the Ratings Metadatas Fields
- [ ] Get Universe Rating for Generated Stories generated automatically

## Contributing

We welcome contributions! If you have ideas or suggestions, please open an issue or submit a pull request.
