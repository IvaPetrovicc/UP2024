import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Get database connection parameters from environment variables
db_username = os.getenv("DB_USER", "root")
db_password = os.getenv("DB_PASSWORD", "lozinka123.")
db_host = os.getenv("DB_HOST", "moj-mysql-server")
db_port = os.getenv("DB_PORT", "3306")
db_name = os.getenv("DB_NAME", "kolegij")

# Form the URL for database connection
SQLALCHEMY_DATABASE_URL = f"mysql+mysqlconnector://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}"

# Create engine for database connection
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create SessionLocal object for database operations
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base object for models
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
