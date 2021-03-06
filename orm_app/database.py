from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# Create a database URL for SQLAlchemy
SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:interface!!@localhost/social_media'

# Create the SQLALchemy engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a Base class
Base = declarative_base()

# Dependency, For getting a session from the database each time we execute


def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()
