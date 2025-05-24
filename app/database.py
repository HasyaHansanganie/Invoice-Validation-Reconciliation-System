from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Fetch database credentials from environment
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DB = os.getenv("MYSQL_DB")
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")

# Construct the MySQL database connection URL
DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}"

# Create the SQLAlchemy engine (echo=True enables SQL statement logging)
engine = create_engine(DATABASE_URL, echo=True)

# Create a session factory for generating DB sessions
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Base class that models will inherit from
Base = declarative_base()

# Dependency function to provide a database session
# Used in FastAPI endpoints via Depends(get_db)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        # Close DB session after use
        db.close()
