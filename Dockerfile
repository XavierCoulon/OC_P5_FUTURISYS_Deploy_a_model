# Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Installer git (pour pip install depuis un dépôt Git)
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*

# Copier le code
COPY . .

# Installer les dépendances
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && if [ -f requirements-dev.txt ]; then pip install --no-cache-dir -r requirements-dev.txt; fi

EXPOSE 7860
ENV PORT=7860
ENV ENVIRONMENT=production

# Lancer Uvicorn avec auto-reload (utile en dev)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860", "--reload"]
