[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-24ddc0f5d75046c5622901739e7c5dd533143b0c8e959d652212380cedb1ea36.svg)](https://classroom.github.com/a/cVeImKGm)


# Hero and Story Generation App

Welcome to the Hero and Story Generation App - a place where epic tales and legendary heroes come to life!

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:
- Docker
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

This will set up all necessary services, including the backend server, database, and any other required components.

### Initialize Database

After the containers are up and running, initialize the database:

- Access the `/importCollection/<collection_name>` endpoint in your browser.
- Replace `<collection_name>` with the name of your collection to load initial data.

## Features

- **Hero Generation**: Create unique hero profiles with rich backstories and attributes.
- **Story Crafting**: Generate captivating stories involving the heroes.
- **Persistent Storage**: Save and manage your heroes and stories in a robust database.

## To-Do Roadmap

- [ ] Frontend Styling Enhancements
- [ ] Generation/Information Adding Feature
- [ ] Integration with Additional APIs for Richer Content

## Contributing

We welcome contributions! If you have ideas or suggestions, please open an issue or submit a pull request.
