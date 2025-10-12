# app/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

# Crée le moteur SQLAlchemy (connexion à ta base)
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # vérifie la connexion avant chaque requête
)

# Fabrique de sessions pour interagir avec la base
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour déclarer les modèles ORM
Base = declarative_base()


def get_db():
    """
    Fournit une session de base de données à utiliser dans les routes FastAPI.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
