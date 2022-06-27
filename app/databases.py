from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


# Initilizing the database using sqlalchemy

SQLALCHEMY_DATABASE_URL = "sqlite:///./fast_api_sqlite.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker( autoflush=False,bind=engine, autocommit=False )

Base = declarative_base()