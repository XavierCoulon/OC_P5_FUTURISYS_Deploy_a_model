# create_db.py
from app.core.database import Base, engine

print("🧱 Création des tables…")
Base.metadata.create_all(bind=engine)
print("✅ Base PostgreSQL prête !")
