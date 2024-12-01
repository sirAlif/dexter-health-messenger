import asyncio
import sys
from fastapi import FastAPI
from api.routes import chat, auth, ai
from db import database
from config.conf import Config
import uvicorn

# Load environment variables
conf = Config()

app = FastAPI()

# Include routes
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])
app.include_router(ai.router, prefix="/ai", tags=["AI"])


@app.on_event("startup")
async def startup():
    # Retry database initialization if failed
    max_retries = 3
    retry_delay = 5  # Seconds
    retries = 0

    while retries < max_retries:
        if retries != 0:
            print("Retrying database initialization...")
        db_created = await database.init_db()
        if db_created:
            return
        retries += 1
        await asyncio.sleep(retry_delay)

    # If the database wasn't created after retries, exit the app
    sys.exit(1)


@app.on_event("shutdown")
async def shutdown():
    await database.close_db()


if __name__ == "__main__":
    uvicorn.run(app, host=conf.API_HOST, port=conf.API_PORT)
