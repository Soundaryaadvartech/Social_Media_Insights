import os
import urllib.parse
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DB_PASSWORD = urllib.parse.quote_plus(os.getenv("DB_PASSWORD"))
DB_USER = urllib.parse.quote_plus(os.getenv("DB_USER"))
DB_HOST = os.getenv("DB_HOST")

# Mapping business to database names
DB_MAPPING = {
    "zing": os.getenv("ZING_DB_NAME"),
    "pkm": os.getenv("PKM_DB_NAME"),
    "beelittle": os.getenv("BLT_DB_NAME"),
    "adoreaboo": os.getenv("ADB_DB_NAME"),
}

def get_database_url(business: str):
    """Return the correct database URL based on the provided business."""
    db_name = DB_MAPPING.get(business)
    if not db_name:
        raise ValueError("Invalid business code provided")
    
    return f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{db_name}"

def get_engine(business: str):
    """Create a new engine for the given business."""
    db_url = get_database_url(business)
    return create_engine(db_url, pool_recycle=3600, pool_timeout=60)

Base = declarative_base()

# Dependency to get a DB session dynamically
def get_db(business: str):
    """Dependency to get a database session for the requested business."""
    engine = get_engine(business)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()