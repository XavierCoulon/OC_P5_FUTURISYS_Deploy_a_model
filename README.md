---
title: Futurisys
emoji: 🧠
colorFrom: blue
colorTo: indigo
sdk: docker
sdk_version: "1.0"
app_file: app.py
pinned: false
---

# OC P5 Futurisys - Déploiement d'un modèle ML

Application FastAPI pour le déploiement d'un modèle de Machine Learning avec interface utilisateur Gradio intégrée.

## 🚀 Fonctionnalités

-   **🤖 Prédictions ML** - Modèle de prédiction de départ d'employés
-   **🚀 FastAPI** - API REST moderne et performante
-   **🎨 Interface Gradio** - Interface web interactive intégrée
-   **🗄️ Base de données PostgreSQL** - Stockage des données avec SQLAlchemy 2.0
-   **📝 Validation Pydantic** - Validation robuste des données d'entrée
-   **🐳 Docker** - Déploiement containerisé avec docker-compose
-   **🧪 Tests automatisés** - Suite de tests avec pytest et coverage
-   **🔧 Outils de développement** - Black, isort, flake8, pre-commit hooks
-   **📊 Monitoring** - Endpoints de santé et métriques
-   **🔒 Configuration sécurisée** - Variables d'environnement et .env

## 📊 Structure de la base de données

```mermaid
erDiagram
    prediction_inputs {
        INTEGER id
        VARCHAR matricule
        INTEGER age
        VARCHAR(5) genre
        DOUBLE PRECISION revenu_mensuel
        INTEGER nombre_experiences_precedentes
        INTEGER annee_experience_totale
        INTEGER annees_dans_l_entreprise
        INTEGER annees_dans_le_poste_actuel
        INTEGER satisfaction_employee_environnement
        INTEGER niveau_hierarchique_poste
        INTEGER satisfaction_employee_nature_travail
        INTEGER satisfaction_employee_equipe
        INTEGER satisfaction_employee_equilibre_pro_perso
        INTEGER note_evaluation_actuelle
        VARCHAR(3) heure_supplementaires
        DOUBLE PRECISION augmentation_salaire_precedente
        INTEGER nombre_participation_pee
        INTEGER nb_formations_suivies
        DOUBLE PRECISION distance_domicile_travail
        INTEGER niveau_education
        VARCHAR(11) frequence_deplacement
        INTEGER annees_depuis_la_derniere_promotion
        INTEGER annes_sous_responsable_actuel
        VARCHAR(10) departement
        VARCHAR(11) statut_marital
        VARCHAR(23) poste
        VARCHAR(23) domaine_etude
        DOUBLE PRECISION mobilite_interne_ratio
        DOUBLE PRECISION ratio_anciennete
        DOUBLE PRECISION delta_evaluation
        TIMESTAMP created_at
    }
    prediction_outputs {
        INTEGER id
        INTEGER prediction_input_id
        INTEGER prediction
        DOUBLE PRECISION probability
        DOUBLE PRECISION threshold
        TIMESTAMP created_at
    }
    prediction_outputs}o--||prediction_inputs :prediction_outputs_prediction_input_id_fkey
```

## 📁 Structure du projet

```
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   └── endpoints.py             # Routes API (CRUD prédictions)
│   ├── core/
│   │   ├── config.py                # Configuration Pydantic Settings
│   │   └── database.py              # Configuration SQLAlchemy
│   ├── ml/
│   │   ├── model_loader.py          # Chargement du modèle ML
│   │   └── random_forest_optimized.pkl  # Modèle pré-entraîné
│   ├── __init__.py
│   ├── enums.py                     # Énumérations métier
│   ├── main.py                      # Point d'entrée FastAPI + Gradio
│   ├── models.py                    # Modèles SQLAlchemy (SQLAlchemy 2.0)
│   ├── schemas.py                   # Schémas Pydantic avec validation
│   ├── services.py                  # Logique métier et services
│   └── ui.py                        # Interface Gradio
├── tests/
│   ├── conftest.py                  # Configuration pytest
│   ├── test_endpoints.py            # Tests API
│   ├── test_services.py             # Tests services
│   └── test_*.py                    # Autres tests
├── .github/workflows/               # CI/CD GitHub Actions
├── create_db.py                     # Script création tables
├── docker-compose.yml               # Stack PostgreSQL + API
├── Dockerfile                       # Image de production
├── Makefile                         # Commandes de développement
├── requirements.txt                 # Dépendances Python
├── requirements-dev.txt             # Dépendances de développement
├── .env.example                     # Template variables d'environnement
├── .pre-commit-config.yaml         # Hooks pre-commit
└── setup.cfg                        # Configuration flake8/coverage
```

## 🛠️ Installation et configuration

### Prérequis

-   Python 3.12+
-   Docker et Docker Compose
-   Git

### Option 1: Développement local avec Docker (recommandé)

```bash
# Cloner le repository
git clone <repository-url>
cd OC_P5_Futurisys

# Copier et configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos paramètres

# Lancer la stack complète (PostgreSQL + API)
make up
# ou: docker compose up -d

# L'application sera accessible sur:
# - API: http://localhost:8000/v1/
# - Interface Gradio: http://localhost:8000/
# - Documentation: http://localhost:8000/docs
```

### Option 2: Développement local Python

```bash
# Installer les dépendances
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Configurer l'environnement
cp .env.example .env

# Créer la base de données (après avoir configuré DATABASE_URL)
python create_db.py

# Lancer le serveur de développement
fastapi dev app/main.py
# ou: uvicorn app.main:app --reload
```

## 🚀 Utilisation

### Interface utilisateur (Gradio)

L'interface web principale est accessible à la racine en local : http://localhost:8000/
Aussi accessible en production via Hugging Face Spaces : https://huggingface.co/spaces/XavierCoulon/futurisys

### API REST

Les endpoints principaux sont préfixés par `/v1/` :

#### Endpoints généraux

-   **GET** `/v1/` - Message d'accueil de l'API
-   **GET** `/v1/health` - Vérification de l'état de santé
-   **GET** `/v1/erd` - Schéma de base de données (format Mermaid)

#### Endpoints de prédiction

-   **POST** `/v1/predictions` - Créer une nouvelle prédiction
-   **GET** `/v1/predictions` - Lister les prédictions (avec pagination)
-   **GET** `/v1/predictions/{id}` - Récupérer une prédiction par ID
-   **DELETE** `/v1/predictions/{id}` - Supprimer une prédiction

#### Documentation automatique

-   **Swagger UI** : http://localhost:8000/docs
-   **ReDoc** : http://localhost:8000/redoc

### Exemple d'utilisation API

```bash
# Créer une prédiction
curl -X POST "http://localhost:8000/v1/predictions" \
  -H "Content-Type: application/json" \
  -d '{
    "age": 35,
    "genre": "M",
    "matricule": "M12345",
    "revenu_mensuel": 3200.5,
    "nombre_experiences_precedentes": 3,
    "annee_experience_totale": 10,
    "annees_dans_l_entreprise": 5,
    "annees_dans_le_poste_actuel": 3,
    "satisfaction_employee_environnement": 4,
    "niveau_hierarchique_poste": 3,
    "satisfaction_employee_nature_travail": 5,
    "satisfaction_employee_equipe": 4,
    "satisfaction_employee_equilibre_pro_perso": 3,
    "note_evaluation_actuelle": 4,
    "heure_supplementaires": "Oui",
    "augmentation_salaire_precedente": 3.5,
    "nombre_participation_pee": 2,
    "nb_formations_suivies": 5,
    "distance_domicile_travail": 12.3,
    "niveau_education": 4,
    "frequence_deplacement": "Occasionnel",
    "annees_depuis_la_derniere_promotion": 2,
    "annes_sous_responsable_actuel": 3,
    "departement": "Consulting",
    "statut_marital": "Marié(e)",
    "poste": "Consultant",
    "domaine_etude": "Infra & Cloud",
    "mobilite_interne_ratio": 0.2,
    "ratio_anciennete": 0.5,
    "delta_evaluation": -0.3
  }'

# Lister les prédictions
curl "http://localhost:8000/v1/predictions?skip=0&limit=10"
```

## ⚙️ Variables d'environnement

Copiez `.env.example` vers `.env` et personnalisez :

```env
# Configuration générale
DEBUG=True
ENVIRONMENT=development
API_VERSION=dev

# Base de données PostgreSQL
DATABASE_URL=postgresql://admin:password@localhost:5432/futurisys_db

# Configuration API
API_TITLE=Futurisys ML API
API_DESCRIPTION=API de prédiction de départ d'employés
HOST=0.0.0.0
PORT=8000

# Sécurité (changez en production)
SECRET_KEY=your-secret-key-change-this-in-production

# Logging
LOG_LEVEL=INFO
```

## 🔄 CI/CD et GitHub Actions

Le projet utilise GitHub Actions pour l'automatisation du cycle de développement :

### 🚦 Workflows configurés

-   **🧪 Tests automatiques** (`test.yml`) - Validation du code sur chaque PR
-   **🐳 Build & Push Docker** (`docker-publish.yml`) - Construction et publication d'images
-   **🚀 Déploiement** - Vers Hugging Face Spaces automatiquement
-   **✅ Quality checks** - Vérification du formatage et linting

### 🔧 Déclenchement automatique

-   **Pull Requests** : Tests complets, vérifications qualité (Black, flake8, pytest)
-   **Tags v\*** : Build et publication d'images Docker vers DockerHub
-   **Push sur `main`** : Déploiement automatique vers Hugging Face Spaces
-   **Commits** : Hooks pre-commit locaux + validation CI

### 📋 Pipeline type

```mermaid
graph LR
    A[Code Push] --> B[Tests unitaires]
    B --> C[Quality checks]
    C --> D[Build Docker]
    D --> E[Deploy HF Spaces]

    F[Tag v*] --> G[Build & Push DockerHub]
```

Le système garantit que seul du code testé et validé atteint la production.

## 🧪 Développement et tests

### Commandes Make disponibles

```bash
# Docker
make up              # Démarrer la stack
make down            # Arrêter la stack
make rebuild         # Rebuild et redémarrer

# Tests et qualité code
make test            # Lancer pytest
make coverage        # Tests avec rapport de couverture
make precommit       # Lancer pre-commit sur tous les fichiers

# Voir Makefile pour plus de commandes
```

### Tests

```bash
# Tests unitaires
pytest

# Tests avec couverture
pytest --cov=app --cov-report=html

# Tests spécifiques
pytest tests/test_endpoints.py -v
```

### Outils de qualité code

Le projet utilise plusieurs outils pour maintenir la qualité du code :

-   **Black** : Formatage automatique du code
-   **isort** : Tri des imports
-   **flake8** : Linting et vérification PEP8
-   **pre-commit** : Hooks Git automatiques

```bash
# Formater le code
black .
isort .

# Vérifier le linting
flake8

# Installer les hooks pre-commit
pre-commit install
```

## 🚀 Déploiement

### Déploiement Docker

```bash
# Build de l'image
docker build -t futurisys-api .

# Lancer avec docker-compose (recommandé)
docker compose up -d --build
```

### Déploiement Hugging Face Spaces

Ce projet est configuré pour être déployé sur Hugging Face Spaces :

1. Le fichier de configuration Hugging Face est dans l'en-tête du README
2. L'interface Gradio est montée à la racine (`/`)
3. L'API est accessible sous `/v1/`

### Production

Pour un déploiement en production, considérez :

1. **Variables d'environnement** : Utilisez un gestionnaire de secrets
2. **Base de données** : PostgreSQL avec sauvegarde automatique
3. **Serveur WSGI** : Gunicorn avec workers Uvicorn
4. **Reverse Proxy** : Nginx ou traefik
5. **Monitoring** : Logs structurés et métriques
6. **Sécurité** : HTTPS, authentification, rate limiting

## 🤝 Contribution

1. Fork le projet
2. Créez une branche feature (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commitez vos changements (`git commit -m 'Ajout nouvelle fonctionnalité'`)
4. Pushez vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Ouvrez une Pull Request

### Workflow de développement

1. Les hooks pre-commit vérifient automatiquement le code
2. Les tests doivent passer avant merge
3. La couverture de code doit être maintenue > 80%
4. Suivez les conventions de nommage Python (PEP8)

## 📝 Technologies utilisées

-   **FastAPI** - Framework web moderne et performant
-   **Gradio** - Interface utilisateur web interactive
-   **SQLAlchemy 2.0** - ORM avec support des types mappés
-   **Pydantic** - Validation de données avec annotations de types
-   **PostgreSQL** - Base de données relationnelle
-   **Docker & Docker Compose** - Containerisation et orchestration
-   **pytest** - Framework de tests
-   **Black, isort, flake8** - Outils de qualité code
-   **pre-commit** - Hooks Git automatiques
-   **scikit-learn** - Modèle de Machine Learning

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.
