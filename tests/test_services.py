from unittest.mock import patch

import pytest
from fastapi import HTTPException

from app.models import PredictionInput, PredictionOutput
from app.schemas import PredictionInputCreate, PredictionOutputCreate
from app.services import (
    create_prediction_full_service,
    create_prediction_input,
    create_prediction_output,
    delete_prediction_input,
    get_prediction_input_by_id,
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
    """Vérifie que l'insertion d'un input fonctionne et retourne un objet persistant."""
    obj = create_prediction_input(db, payload_input)
    assert obj.id is not None
    assert obj.age == payload_input.age
    assert obj.matricule == payload_input.matricule
    assert db.query(PredictionInput).count() == 1


def test_create_prediction_input_duplicate_matricule(db, payload_input):
    """Vérifie qu'on ne peut pas créer deux inputs avec le même matricule."""
    # Première création réussit
    create_prediction_input(db, payload_input)

    # Deuxième création avec le même matricule échoue
    with pytest.raises(HTTPException) as exc_info:
        create_prediction_input(db, payload_input)

    assert exc_info.value.status_code == 409
    assert payload_input.matricule in str(exc_info.value.detail)


def test_create_prediction_input_no_matricule(db, sample_input):
    """Vérifie qu'on peut créer plusieurs inputs sans matricule."""
    sample_input["matricule"] = None
    payload = PredictionInputCreate(**sample_input)

    # Deux créations sans matricule devraient réussir
    obj1 = create_prediction_input(db, payload)
    obj2 = create_prediction_input(db, payload)

    assert obj1.id != obj2.id
    assert obj1.matricule is None
    assert obj2.matricule is None
    assert db.query(PredictionInput).count() == 2


def test_get_prediction_inputs(db, payload_input):
    """Vérifie que la récupération des inputs fonctionne."""
    create_prediction_input(db, payload_input)
    results = get_prediction_inputs(db)
    assert isinstance(results, list)
    assert len(results) == 1
    assert results[0].age == payload_input.age
    assert results[0].matricule == payload_input.matricule


def test_get_prediction_inputs_with_filter(db, sample_input):
    """Vérifie le filtrage par matricule."""
    # Crée deux inputs avec des matricules différents
    sample1 = sample_input.copy()
    sample1["matricule"] = "M11111"
    sample2 = sample_input.copy()
    sample2["matricule"] = "M22222"

    create_prediction_input(db, PredictionInputCreate(**sample1))
    create_prediction_input(db, PredictionInputCreate(**sample2))

    # Teste le filtrage
    results_all = get_prediction_inputs(db)
    results_filtered = get_prediction_inputs(db, matricule="M11111")

    assert len(results_all) == 2
    assert len(results_filtered) == 1
    assert results_filtered[0].matricule == "M11111"


def test_get_prediction_input_by_id(db, payload_input):
    """Vérifie la récupération d'un input par ID."""
    created_obj = create_prediction_input(db, payload_input)

    # Test avec ID existant
    found_obj = get_prediction_input_by_id(db, created_obj.id)
    assert found_obj is not None
    assert found_obj.id == created_obj.id
    assert found_obj.matricule == payload_input.matricule

    # Test avec ID inexistant
    not_found = get_prediction_input_by_id(db, 999999)
    assert not_found is None


def test_delete_prediction_input(db, payload_input):
    """Vérifie la suppression d'un input."""
    created_obj = create_prediction_input(db, payload_input)

    # Test suppression réussie
    success = delete_prediction_input(db, created_obj.id)
    assert success is True
    assert db.query(PredictionInput).count() == 0

    # Test suppression d'un ID inexistant
    success_not_found = delete_prediction_input(db, 999999)
    assert success_not_found is False


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
    assert result.input.matricule == payload_input.matricule
    assert result.output.prediction in [0, 1]
    assert 0 <= result.output.probability <= 1

    # Vérifie que le modèle a été appelé
    mock_model.predict.assert_called_once()
    mock_model.predict_proba.assert_called_once()

    # --- Vérifie la persistance dans la DB ---
    assert db.query(PredictionInput).count() == 1
    assert db.query(PredictionOutput).count() == 1


def test_create_prediction_full_service_duplicate_matricule(
    db, payload_input, mock_model
):
    """Vérifie que le service complet refuse les matricules en double."""
    # Première création réussit
    create_prediction_full_service(db, payload_input)

    # Deuxième création avec le même matricule échoue
    with pytest.raises(HTTPException) as exc_info:
        create_prediction_full_service(db, payload_input)

    assert exc_info.value.status_code == 409
    assert payload_input.matricule in str(exc_info.value.detail)
