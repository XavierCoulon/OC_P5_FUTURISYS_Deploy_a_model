# Dockerfile
FROM python:3.12-slim

# Dossier de travail dans le conteneur
WORKDIR /app

# Copie du code source dans le conteneur
COPY . .

# Installation des dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Commande par défaut (redéfinie dans docker-compose)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
