from unittest.mock import MagicMock, patch

import pytest

import app.ml.model_loader as model_loader


# === 1️⃣ CAS LOCAL : le fichier existe et se charge correctement ===
@patch("app.ml.model_loader.joblib.load", return_value="dummy_model")
@patch("app.ml.model_loader.Path.exists", return_value=True)
def test_load_model_local_success(mock_exists, mock_joblib):
    model = model_loader.load_model()
    assert model == "dummy_model"
    mock_joblib.assert_called_once()
    mock_exists.assert_called_once()


# === 2️⃣ CAS LOCAL : le fichier existe mais joblib.load échoue → fallback Hugging Face ===
@patch("app.ml.model_loader.Path.exists", return_value=True)
@patch("app.ml.model_loader.requests.get")
@patch("app.ml.model_loader.hf_hub_url", return_value="http://fake-url.com/model.pkl")
def test_load_model_local_fail_fallback_remote(mock_hf, mock_req, mock_exists):
    # prépare la réponse "distante"
    fake_response = MagicMock()
    fake_response.content = b"FAKEBYTES"
    fake_response.raise_for_status = lambda: None
    mock_req.return_value = fake_response

    # premier appel joblib.load -> Exception, deuxième -> succès
    with patch(
        "app.ml.model_loader.joblib.load",
        side_effect=[Exception("corrupted"), "remote_model"],
    ):
        model = model_loader.load_model()

    assert model == "remote_model"
    mock_hf.assert_called_once()
    mock_req.assert_called_once()


# === 3️⃣ CAS DISTANT : le fichier local n'existe pas ===
@patch("app.ml.model_loader.Path.exists", return_value=False)
@patch("app.ml.model_loader.requests.get")
@patch("app.ml.model_loader.hf_hub_url", return_value="http://fake-url.com/model.pkl")
def test_load_model_remote_success(mock_hf, mock_req, mock_exists):
    fake_response = MagicMock()
    fake_response.content = b"BYTES"
    fake_response.raise_for_status = lambda: None
    mock_req.return_value = fake_response

    with patch("app.ml.model_loader.joblib.load", return_value="model_from_hf"):
        model = model_loader.load_model()

    assert model == "model_from_hf"
    mock_exists.assert_called_once()
    mock_hf.assert_called_once()


# === 4️⃣ CAS DISTANT : échec du téléchargement => RuntimeError ===
@patch("app.ml.model_loader.Path.exists", return_value=False)
@patch("app.ml.model_loader.requests.get", side_effect=Exception("network error"))
@patch("app.ml.model_loader.hf_hub_url", return_value="http://fake-url.com/model.pkl")
def test_load_model_remote_fail(mock_hf, mock_req, mock_exists):
    with pytest.raises(RuntimeError, match="Impossible de charger le modèle ML"):
        model_loader.load_model()

    mock_hf.assert_called_once()
    mock_req.assert_called_once()
