from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config.conf import Config

# Load environment variables
conf = Config()

# Fetch database credentials from environment variables
DATABASE_URL = (
    f"postgresql+asyncpg://{conf.POSTGRES_USER}:{conf.POSTGRES_PASSWORD}"
    f"@{conf.POSTGRES_HOST}:5432/{conf.POSTGRES_DB}"
)

engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()


async def init_db():
    """Initialize the database, creating tables if necessary."""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("Database initialized successfully.")
        return True
    except Exception as e:
        print(f"Error initializing the database: {str(e)}")
        return False


async def close_db():
    """Close the database connection pool."""
    await engine.dispose()


async def get_db():
    """Return a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        # Ensure the session is closed
        await db.close()
