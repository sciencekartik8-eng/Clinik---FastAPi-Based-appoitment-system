from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


DATABASE_URL = "sqlite:///./clinic.db"

"""
The engine is SQLAlchemy's connection interface to the database.

It knows:

Which database?
How to connect?
How to communicate with it?

"""
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
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
