# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Create an SQLite database file
DATABASE_URL = "sqlite:///network_assets_test.db"

engine = create_engine(DATABASE_URL, echo=False)

# Base class for ORM models
class Base(DeclarativeBase):
    pass

# Create a session factory
SessionLocal = sessionmaker(bind=engine)

Base.metadata.create_all(bind=engine)