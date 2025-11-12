import os

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.orm import sessionmaker

from app.api.endpoints import api_router
from app.core.database import Base, get_db
from app.core.security import verify_api_key


def is_running_in_docker() -> bool:
    """Detect if we are running inside a Docker container."""
    if os.path.exists("/.dockerenv"):
        return True
    try:
        with open("/proc/1/cgroup", "rt") as f:
            return any("docker" in line for line in f)
    except FileNotFoundError:
        return False


def get_test_database_url() -> str:
    """
    Adjust DATABASE_URL_TEST depending on environment.
    Use localhost when running pytest on the host.
    """
    url = os.getenv("DATABASE_URL_TEST")
    if not url:
        url = "postgresql+psycopg://admin:password@localhost:5432/futurisys_test_db"
        print("⚠️ DATABASE_URL_TEST non défini, fallback vers localhost par défaut.")
    if not is_running_in_docker():
        url = url.replace("@db:", "@localhost:")
    return url


TEST_DATABASE_URL = get_test_database_url()

# Admin connection (to create DB if not exists)
ADMIN_DATABASE_URL = TEST_DATABASE_URL.rsplit("/", 1)[0] + "/postgres"
admin_engine = create_engine(ADMIN_DATABASE_URL, isolation_level="AUTOCOMMIT")

# Regular SQLAlchemy engine for tests
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_test_database():
    """Create the test DB if it doesn’t already exist."""
    db_name = TEST_DATABASE_URL.split("/")[-1]
    try:
        with admin_engine.connect() as conn:
            conn.execute(text(f"CREATE DATABASE {db_name}"))
            print(f"✅ Created test database '{db_name}'")
    except ProgrammingError:
        # Already exists
        print(f"ℹ️ Test database '{db_name}' already exists")
    except OperationalError as e:
        print(f"❌ Could not connect to admin DB: {e}")


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """
    Initialise la base de test avant les tests et la détruit après.
    """
    create_test_database()
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    print("🧹 Test DB dropped after tests.")


@pytest.fixture(scope="function")
def db():
    """
    Fournit une session SQLAlchemy isolée pour chaque test.
    Rollback après chaque test.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    print("🚀 Nouvelle transaction pour un test")
    yield session
    session.close()
    transaction.rollback()
    connection.close()
    print("🧹 Rollback après test")


# --- CLIENT HTTP ASYNCHRONE -----------------------------------------------------------


@pytest_asyncio.fixture
async def async_client(db):
    """
    Client HTTP asynchrone avec DB de test isolée et authentification API key.
    """
    app = FastAPI()
    app.include_router(api_router)

    # Override la dépendance get_db de FastAPI pour utiliser la session de test
    def override_get_db():
        try:
            yield db
        finally:
            db.close()

    # Override la vérification d'API key pour les tests
    async def override_verify_api_key(api_key: str | None = None) -> str:
        return api_key or "test-key"

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[verify_api_key] = override_verify_api_key

    transport = ASGITransport(app=app)
    # Ajouter le header API key pour les tests
    headers = {"X-API-Key": os.getenv("API_KEY", "default-key-change-me")}
    async with AsyncClient(transport=transport, base_url="http://testserver", headers=headers) as client:  # type: ignore
        yield client


@pytest.fixture
def fake_inspect():
    """Mock de inspect(engine) pour les tests d'endpoint /erd (aucune connexion réelle DB)."""

    def _fake_inspect(engine):
        class FakeInspector:
            def get_table_names(self):
                return ["table1", "table2"]

            def get_columns(self, table):
                return [{"name": "col1", "type": "INTEGER"}]

            def get_foreign_keys(self, table):
                return (
                    [{"name": "fk_table2", "referred_table": "table2"}]
                    if table == "table1"
                    else []
                )

        return FakeInspector()

    return _fake_inspect


@pytest.fixture
def sample_input():
    """Exemple d'entrée de prédiction pour les tests."""
    return {
        "age": 41,
        "matricule": "M12345",
        "genre": "F",
        "revenu_mensuel": 5993,
        "statut_marital": "Célibataire",
        "departement": "Commercial",
        "poste": "Cadre Commercial",
        "nombre_experiences_precedentes": 8,
        "annee_experience_totale": 8,
        "annees_dans_l_entreprise": 6,
        "annees_dans_le_poste_actuel": 4,
        "satisfaction_employee_environnement": 2,
        "niveau_hierarchique_poste": 2,
        "satisfaction_employee_nature_travail": 4,
        "satisfaction_employee_equipe": 2,
        "satisfaction_employee_equilibre_pro_perso": 4,
        "note_evaluation_actuelle": 3,
        "heure_supplementaires": "Oui",
        "augmentation_salaire_precedente": 0.11,
        "nombre_participation_pee": 0,
        "nb_formations_suivies": 0,
        "distance_domicile_travail": 1,
        "niveau_education": 2,
        "domaine_etude": "Infra & Cloud",
        "frequence_deplacement": "Occasionnel",
        "annees_depuis_la_derniere_promotion": 0,
        "annes_sous_responsable_actuel": 5,
        "mobilite_interne_ratio": 0.666667,
        "ratio_anciennete": 0.428571,
        "delta_evaluation": 0,
    }


@pytest.fixture
def sample_output():
    """Exemple de sortie de prédiction pour les tests."""
    return {
        "id": 1,
        "prediction_input_id": 1,
        "prediction": 1,
        "probability": 0.55,
        "threshold": 0.5,
        "created_at": "2025-10-15T18:53:48.259Z",
    }
