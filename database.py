from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import os
from dotenv import load_dotenv

load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")
# getting ready for database connections
engine = create_engine(DATABASE_URL)

# session factory, used to create sessions for database interactions
SessionLocal = sessionmaker(bind=engine)

# base class for our models, using SQLAlchemy's declarative system
class Base(DeclarativeBase):
    pass

# dependency function to get a database session, used in API endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db      
    finally:
        db.close()    