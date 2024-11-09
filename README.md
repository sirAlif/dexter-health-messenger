# Messaging Backend Feature
This project provides a simple backend for a messaging feature similar to WhatsApp.

## Project Structure
- **api/**: Contains the FastAPI router definitions.
- **db/**: Contains database models and connection setup.
- **services/**: Logic for specific tasks, like message-related operations.
- **tests/**: Unit tests for the chat functionality.

## Getting Started

### Prerequisites
- Docker and Docker Compose

### Running the Application
1. Create an `.env` file based on the `.env.example` file:
```sh
cp .env.example .env
```
Fill in the required environment variables in the .env file, such as database and FastAPI settings.

2. Build and run the application using Docker:
   ```bash
   make run
   ```

3. To stop the application:
   ```bash
   make stop
   ```
   
## Testing
To test your FastAPI application, you can use curl commands as examples to make requests to the different routes. Below are examples of how to test the endpoints using curl:
1. Create Users:
   ```bash
   curl --location 'http://localhost:8000/users' \
     --header 'Content-Type: application/json' \
     --data '{
      "username": "setashiz"
     }'
   ```
   
   ```bash
   curl --location 'http://localhost:8000/users' \
     --header 'Content-Type: application/json' \
     --data '{
      "username": "sirAlif"
     }'
   ```

2. Send a Message:
   ```bash
   curl --location 'http://localhost:8000/messages' \
     --header 'Content-Type: application/json' \
     --data '{
       "sender_id": 1,
       "receiver_id": 2,
       "content": "Hello",
       "timestamp": "2024-12-11"
     }'
   ```

3. Get Messages for a User:
   ```bash
   curl --location --request GET 'http://localhost:8000/messages/2' --header 'Content-Type: application/json'
   ```

## Database Structure
- User: Stores user information.
- Message: Stores messages, with sender and receiver relationships.

## Future Improvements
- Add authentication
- Message encryption
- Message status tracking (e.g., delivered, seen)
- Writing proper tests for the project
