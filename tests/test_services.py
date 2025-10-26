from unittest.mock import patch

import pytest

from app.models import PredictionInput, PredictionOutput
from app.schemas import PredictionInputCreate, PredictionOutputCreate
from app.services import (
    create_prediction_full_service,
    create_prediction_input,
    create_prediction_output,
    get_prediction_inputs,
    get_prediction_outputs,
)


@pytest.fixture
def payload_input(sample_input):
    """Prépare une instance Pydantic pour les tests d’insertions."""
    return PredictionInputCreate(**sample_input)


@pytest.fixture
def payload_output():
    """Sortie minimale pour créer un output."""
    return PredictionOutputCreate(
        prediction_input_id=1, prediction=1, probability=0.85, threshold=0.5
    )


@pytest.fixture
def mock_model():
    """Mock du modèle ML pour isoler le service."""
    with patch("app.services.model") as mock:
        mock.predict.return_value = [1]
        mock.predict_proba.return_value = [[0.3, 0.7]]
        yield mock


# ------------------------------
# TESTS UNITAIRES
# ------------------------------


def test_create_prediction_input(db, payload_input):
    """Vérifie que l’insertion d’un input fonctionne et retourne un objet persistant."""
    obj = create_prediction_input(db, payload_input)
    assert obj.id is not None
    assert obj.age == payload_input.age
    assert db.query(PredictionInput).count() == 1


def test_get_prediction_inputs(db, payload_input):
    """Vérifie que la récupération des inputs fonctionne."""
    create_prediction_input(db, payload_input)
    results = get_prediction_inputs(db)
    assert isinstance(results, list)
    assert len(results) == 1
    assert results[0].age == payload_input.age


def test_create_prediction_output(db, sample_input):
    """Vérifie la création d’un output isolé."""
    input_payload = PredictionInputCreate(**sample_input)
    db_input = create_prediction_input(db, input_payload)

    payload_output = PredictionOutputCreate(
        prediction_input_id=db_input.id,
        prediction=1,
        probability=0.85,
        threshold=0.5,
    )
    db_output = create_prediction_output(db, payload_output)

    # 3️⃣ Vérifie la cohérence
    assert db_output.prediction_input_id == db_input.id
    assert db_output.prediction == 1
    assert db.query(PredictionOutput).count() == 1


def test_get_prediction_outputs(db, sample_input):
    """Vérifie que la récupération des outputs fonctionne."""

    input_obj = create_prediction_input(db, PredictionInputCreate(**sample_input))

    # 2️⃣ Crée un output via le schéma Pydantic
    payload_output = PredictionOutputCreate(
        prediction_input_id=input_obj.id,
        prediction=1,
        probability=0.85,
        threshold=0.5,
    )
    create_prediction_output(db, payload_output)

    # 3️⃣ Teste la récupération
    results = get_prediction_outputs(db)
    assert len(results) == 1
    assert results[0].prediction_input_id == input_obj.id
    assert results[0].probability == 0.85


def test_create_prediction_full_service(db, payload_input, mock_model):
    """Teste le workflow complet du service principal avec le modèle mocké."""
    result = create_prediction_full_service(db, payload_input)

    # Vérifie que les sous-objets sont bien générés
    assert result.input.id is not None
    assert result.output.prediction in [0, 1]
    assert 0 <= result.output.probability <= 1

    # Vérifie que le modèle a été appelé
    mock_model.predict.assert_called_once()
    mock_model.predict_proba.assert_called_once()

    # --- Vérifie la persistance dans la DB ---
    assert db.query(PredictionInput).count() == 1
    assert db.query(PredictionOutput).count() == 1
