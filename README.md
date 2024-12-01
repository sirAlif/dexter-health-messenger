# Messaging Backend Feature
This project provides a simple backend for a messaging feature similar to WhatsApp.

## Project Structure
- **api/**: Contains the FastAPI router definitions.
- **db/**: Contains database models and connection setup.
- **services/**: Contains business logic for specific tasks, such as authentication and messaging operations.
- **client/**: Contains a sample terminal client for interacting with the API (if applicable).


## Getting Started

### Prerequisites
- Docker and Docker Compose

### Running the Application
1. Create an `.env` file based on the `.env-example` file:
```sh
cp .env-example .env
```
Fill in the required environment variables in the .env file, such as database, FastAPI, and OpenAI settings.

You can use this link to generate OpenAI API key: https://platform.openai.com/api-keys

2. Build and run the application using Docker:
   ```bash
   make run
   ```

3. To stop the application:
   ```bash
   make stop
   ```
   
4. To test the application using a terminal client `client/terminal_client.py`:
   ```bash
   make run-client
   ```
You can open a terminal client for each user and make a live chat!

## Database Structure
- User: Stores user information such as username and password hash.
- Message: Stores messages, with relationships between sender and receiver.

## Future Improvements
- Message encryption
- Message status tracking (e.g., delivered, seen)
- Writing proper tests for the project
