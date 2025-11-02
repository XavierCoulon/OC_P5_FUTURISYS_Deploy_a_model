import os
from unittest.mock import MagicMock, patch

import gradio as gr

from app.ui import build_interface, predict_from_ui

# Désactiver les analytics Gradio pendant les tests
os.environ["GRADIO_ANALYTICS_ENABLED"] = "False"


@patch("app.ui.create_prediction_full_service")
@patch("app.ui.SessionLocal")
def test_predict_from_ui_reuses_sample_input(mock_session, mock_service, sample_input):
    """Vérifie que l'UI utilise correctement le service et le ferme, avec les fixtures existantes."""
    db = MagicMock()
    mock_session.return_value = db
    mock_service.return_value.output.prediction = 0
    mock_service.return_value.output.probability = 0.23456

    # Appel avec les données de la fixture existante
    result = predict_from_ui(**sample_input)

    assert result == (0.235, "🧑‍💼 Restera")
    mock_service.assert_called_once()
    db.close.assert_called_once()


def test_build_interface_structure():
    """Vérifie que la structure Gradio reste cohérente."""
    interface = build_interface()
    assert isinstance(interface, gr.Interface)
    assert len(interface.input_components) > 10
    assert isinstance(interface.output_components[0], gr.Number)
    assert isinstance(interface.output_components[1], gr.Text)
    assert "Futurisys" in str(interface.title)
