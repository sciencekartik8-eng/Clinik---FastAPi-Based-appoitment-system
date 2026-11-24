from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings


def _resolve_database_url(database_url: str) -> str:
    """Resolve relative SQLite URLs against the backend directory."""
    sqlite_prefix = "sqlite:///"
    if not database_url.startswith(sqlite_prefix):
        return database_url

    database_path = Path(database_url[len(sqlite_prefix):])
    if not database_path.is_absolute():
        database_path = Path(__file__).resolve().parents[2] / database_path
    return f"{sqlite_prefix}{database_path.resolve().as_posix()}"


DATABASE_URL = _resolve_database_url(settings.database_url)

"""
The engine is SQLAlchemy's connection interface to the database.

It knows:

Which database?
How to connect?
How to communicate with it?

"""
connect_args = (
    {"check_same_thread": False}
    if DATABASE_URL.startswith("sqlite")
    else {}
)

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
)

'''
A session represents a conversation with the database.

We'll eventually do things like:

db.add(user)
db.commit()
db.query(User)

'''
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine)    

class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
