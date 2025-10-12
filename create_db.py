# create_db.py
# Import models so they are registered on Base.metadata before creating tables
import app.models  # noqa: F401
from app.core.database import Base, engine

print("🧱 Création des tables…")
Base.metadata.create_all(bind=engine)
print("✅ Base PostgreSQL prête !")
