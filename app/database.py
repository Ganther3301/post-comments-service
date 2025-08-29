from sqlmodel import SQLModel, create_engine, Session
from typing import Generator
from dotenv import load_dotenv
from os import getenv

load_dotenv()
# SQLite database URL
DATABASE_URL = getenv("DATABASE_URL")

# Create engine with SQLite-specific options
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Required for SQLite with FastAPI
    echo=True,  # Set to False in production to reduce logs
)


def create_tables():
    """Create all database tables"""
    SQLModel.metadata.create_all(engine)


def get_db() -> Generator[Session, None, None]:
    """Dependency to get database session"""
    with Session(engine) as session:
        yield session
