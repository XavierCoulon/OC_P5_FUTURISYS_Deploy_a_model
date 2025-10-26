import pytest
from pydantic import ValidationError

import app.api.endpoints as endpoints
from app.schemas import PredictionInputCreate


# =========================
#        ROOT ENDPOINT
# =========================
class TestRootEndpoint:
    """Tests pour l'endpoint racine '/'."""

    @pytest.mark.asyncio
    async def test_root_success(self, async_client):
        resp = await async_client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["message"] == "Welcome to Futurisys ML API"
        assert data["api_version"] == "dev"


# =========================
#        HEALTH CHECK
# =========================
class TestHealthEndpoint:
    """Tests pour l'endpoint /health."""

    @pytest.mark.asyncio
    async def test_health_ok(self, async_client):
        resp = await async_client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data


# =========================
#         ERD
# =========================
class TestERDEndpoint:
    """Tests pour l'endpoint /erd."""

    @pytest.mark.asyncio
    async def test_erd_returns_mermaid(self, async_client, monkeypatch, fake_inspect):
        monkeypatch.setattr(endpoints, "inspect", fake_inspect)
        resp = await async_client.get("/erd")
        assert resp.status_code == 200
        content = resp.text
        assert content.startswith("```mermaid")
        assert "erDiagram" in content
        assert "table1" in content
        assert content.endswith("```")


# =========================
#       PREDICTIONS
# =========================
class TestPredictionsEndpoint:
    """Tests pour l'endpoint /predictions (POST)."""

    @pytest.mark.asyncio
    async def test_post_predictions_success(self, async_client, sample_input):
        """
        Vérifie que la requête POST /predictions renvoie les données d'entrée
        enrichies avec id et created_at, et un output valide.
        """
        resp = await async_client.post("/predictions", json=sample_input)
        assert resp.status_code == 201, f"HTTP {resp.status_code} inattendu"

        data = resp.json()

        # Bloc input
        assert "input" in data
        input_data = data["input"]
        assert "id" in input_data and isinstance(input_data["id"], int)
        assert "created_at" in input_data
        for key, value in sample_input.items():
            assert input_data[key] == value

        # Bloc output
        assert "output" in data
        assert 0 <= data["output"]["probability"] <= 1
        assert "prediction" in data["output"]

    @pytest.mark.asyncio
    async def test_get_all_predictions(self, async_client, sample_input):
        """
        Vérifie que l'endpoint GET /predictions renvoie une liste JSON.
        """
        # Crée une prédiction d'abord (POST)
        await async_client.post("/predictions", json=sample_input)

        # Puis liste toutes les prédictions
        resp = await async_client.get("/predictions")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert "id" in data[0]
        assert "created_at" in data[0]

    @pytest.mark.asyncio
    async def test_get_prediction_by_id(self, async_client, sample_input):
        """
        Vérifie que GET /predictions/{id} renvoie bien une prédiction existante.
        """
        # Crée une prédiction pour récupérer son id
        post_resp = await async_client.post("/predictions", json=sample_input)
        assert post_resp.status_code == 201
        prediction_id = post_resp.json()["input"]["id"]

        # Récupère cette prédiction
        get_resp = await async_client.get(f"/predictions/{prediction_id}")
        assert get_resp.status_code == 200
        data = get_resp.json()
        assert data["id"] == prediction_id
        assert "created_at" in data

    @pytest.mark.asyncio
    async def test_get_prediction_not_found(self, async_client):
        """
        Vérifie qu'une prédiction inexistante retourne 404.
        """
        resp = await async_client.get("/predictions/999999")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_prediction_success(self, async_client, sample_input):
        """
        Vérifie que DELETE /predictions/{id} supprime bien l'enregistrement.
        """
        # Crée une prédiction
        post_resp = await async_client.post("/predictions", json=sample_input)
        prediction_id = post_resp.json()["input"]["id"]

        # Supprime-la
        del_resp = await async_client.delete(f"/predictions/{prediction_id}")
        assert del_resp.status_code == 204

        # Vérifie qu'elle n'existe plus
        get_resp = await async_client.get(f"/predictions/{prediction_id}")
        assert get_resp.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_prediction_not_found(self, async_client):
        """
        Vérifie qu'une suppression d'ID inexistant retourne 404.
        """
        resp = await async_client.delete("/predictions/999999")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_post_predictions_invalid_data(self, async_client, sample_input):
        """
        Vérifie que l'API retourne une erreur 422 si les données sont invalides.
        """
        invalid_input = sample_input.copy()
        invalid_input["age"] = -5  # invalide
        resp = await async_client.post("/predictions", json=invalid_input)
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_post_predictions_missing_field(self, async_client, sample_input):
        """
        Vérifie qu'une clé manquante dans le JSON provoque une erreur 422.
        """
        data = sample_input.copy()
        data.pop("revenu_mensuel", None)
        resp = await async_client.post("/predictions", json=data)
        assert resp.status_code == 422

    # --- TESTS UNITAIRES DE VALIDATION Pydantic ---
    @pytest.fixture(autouse=True)
    def _base_data(self, sample_input):
        """Copie du sample_input pour tests Pydantic purs."""
        self.data = sample_input.copy()

    def test_valid_prediction_input(self):
        """Cas nominal : tout passe."""
        obj = PredictionInputCreate(**self.data)
        assert obj.age == self.data["age"]

    @pytest.mark.parametrize(
        "field,value,expected_msg",
        [
            (
                "annees_dans_le_poste_actuel",
                20,
                "Value error, Le nombre d’années dans le poste actuel ne peut pas dépasser l’expérience totale.",
            ),
            (
                "mobilite_interne_ratio",
                1.5,
                "Value error, Le ratio de mobilité interne doit être compris entre 0 et 1",
            ),
            (
                "ratio_anciennete",
                -0.2,
                "Value error, Le ratio d’ancienneté doit être compris entre 0 et 1",
            ),
            (
                "delta_evaluation",
                10,
                "Value error, L’écart d’évaluation doit être compris entre -5 et 5.",
            ),
        ],
    )
    def test_invalid_cases(self, field, value, expected_msg):
        """
        Paramétrisation des cas invalides — chaque règle de validation Pydantic
        doit lever une ValidationError avec le bon message.
        """
        self.data[field] = value
        with pytest.raises(ValidationError) as excinfo:
            PredictionInputCreate(**self.data)
        assert expected_msg in str(excinfo.value)
