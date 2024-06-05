from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Definiranje parametara za povezivanje s bazom podataka
db_username = "root"
db_password = "lozinka123."
db_host = "127.0.0.1"
db_port = "6306"
db_name = "kolegij"

# Formiranje URL-a za povezivanje s bazom podataka
SQLALCHEMY_DATABASE_URL = f"mysql+mysqlconnector://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}"

# Stvaranje engine objekta za povezivanje s bazom podataka
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Stvaranje SessionLocal objekta za rad s bazom podataka
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Stvaranje baze objekata
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
