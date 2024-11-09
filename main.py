import os
from fastapi import FastAPI
from api.routers import chat
from db import database
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

app = FastAPI()

# Include the chat router
app.include_router(chat.router)


@app.on_event("startup")
async def startup():
    await database.init_db()


@app.on_event("shutdown")
async def shutdown():
    await database.close_db()

# Get host and port from environment variables (defaults to 'localhost' and 8000 if not set)
API_HOST = os.getenv('API_HOST', '0.0.0.0')
API_PORT = int(os.getenv('API_PORT', 8000))

# Uvicorn setup for the host and port
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=API_HOST, port=API_PORT)
