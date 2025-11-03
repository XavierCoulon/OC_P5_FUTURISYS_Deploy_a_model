import os
from unittest.mock import MagicMock, patch

import gradio as gr

from app.ui import (
    CLEAN_LABELS,
    PERSONAL_INFO,
    PROFESSIONAL_INFO,
    SATISFACTION_METRICS,
    build_interface,
    get_version,
    predict_from_ui,
    predict_wrapper,
)

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


@patch("app.ui.get_version")
def test_build_interface_structure(mock_get_version):
    """Vérifie que la structure Gradio reste cohérente."""
    mock_get_version.return_value = "v1.0.0"

    interface = build_interface()
    assert isinstance(interface, gr.Blocks)
    # Vérifier que l'interface a un titre
    assert "Futurisys" in str(interface.title)
    # Vérifier que l'interface est bien configurée
    assert interface is not None


def test_clean_labels_completeness():
    """Vérifie que tous les champs ont des labels propres définis."""
    all_fields = PERSONAL_INFO + PROFESSIONAL_INFO + SATISFACTION_METRICS

    # Vérifier que tous les champs ont un label
    for field in all_fields:
        assert field in CLEAN_LABELS, f"Champ '{field}' manque dans CLEAN_LABELS"

    # Vérifier que les labels ne sont pas vides
    for field, label in CLEAN_LABELS.items():
        assert label.strip(), f"Label vide pour le champ '{field}'"


def test_feature_organization():
    """Vérifie l'organisation des features en catégories."""
    # Vérifier que les listes ne sont pas vides
    assert len(PERSONAL_INFO) > 0, "PERSONAL_INFO ne doit pas être vide"
    assert len(PROFESSIONAL_INFO) > 0, "PROFESSIONAL_INFO ne doit pas être vide"
    assert len(SATISFACTION_METRICS) > 0, "SATISFACTION_METRICS ne doit pas être vide"

    # Vérifier qu'il n'y a pas de doublons entre les catégories
    all_fields = PERSONAL_INFO + PROFESSIONAL_INFO + SATISFACTION_METRICS
    assert len(all_fields) == len(
        set(all_fields)
    ), "Doublons détectés entre les catégories"

    # Vérifier que certains champs essentiels sont présents
    assert "age" in PERSONAL_INFO
    assert "matricule" in PERSONAL_INFO
    assert "revenu_mensuel" in PROFESSIONAL_INFO
    assert "satisfaction_employee_environnement" in SATISFACTION_METRICS


@patch("app.ui.subprocess.run")
@patch("app.ui.os.getenv")
def test_get_version_from_env(mock_getenv, mock_subprocess):
    """Teste la récupération de version depuis les variables d'environnement."""
    mock_getenv.return_value = "1.2.3"

    version = get_version()

    assert version == "v1.2.3"
    mock_getenv.assert_called_with("API_VERSION")


@patch("app.ui.subprocess.run")
@patch("app.ui.os.getenv")
def test_get_version_fallback(mock_getenv, mock_subprocess):
    """Teste le fallback de version quand les autres méthodes échouent."""
    mock_getenv.return_value = None
    mock_subprocess.side_effect = Exception("Git command failed")

    version = get_version()

    assert version == "v1.0.0"


@patch("app.ui.predict_from_ui")
def test_predict_wrapper_success(mock_predict):
    """Teste le wrapper de prédiction avec succès."""
    mock_predict.return_value = (0.75, "🚪 Quittera l'entreprise")

    # Simuler des arguments d'entrée avec des valeurs appropriées
    all_fields = PERSONAL_INFO + PROFESSIONAL_INFO + SATISFACTION_METRICS
    # Utiliser des chaînes pour les champs qui peuvent être des chaînes, sinon des nombres
    args = []
    for field in all_fields:
        if field == "matricule":
            args.append("")  # Chaîne vide pour matricule
        elif field in [
            "genre",
            "heure_supplementaires",
            "departement",
            "domaine_etude",
            "frequence_deplacement",
            "poste",
            "statut_marital",
            "niveau_education",
        ]:
            args.append("test_value")  # Valeur string pour les enums
        else:
            args.append(1.0)  # Valeur numérique

    result_text, result_details = predict_wrapper(*args)

    assert "🎯 **Prédiction**: 🚪 Quittera l'entreprise" in result_text
    assert "📊 **Probabilité**: 75.0%" in result_text
    assert "⚠️ Cet employé présente un risque d'attrition" in result_text
    assert result_details["probability"] == 0.75
    assert result_details["prediction"] == "🚪 Quittera l'entreprise"


@patch("app.ui.predict_from_ui")
def test_predict_wrapper_error(mock_predict):
    """Teste le wrapper de prédiction avec erreur."""
    mock_predict.side_effect = Exception("Erreur de prédiction")

    all_fields = PERSONAL_INFO + PROFESSIONAL_INFO + SATISFACTION_METRICS
    args = []
    for field in all_fields:
        if field == "matricule":
            args.append("")
        elif field in [
            "genre",
            "heure_supplementaires",
            "departement",
            "domaine_etude",
            "frequence_deplacement",
            "poste",
            "statut_marital",
            "niveau_education",
        ]:
            args.append("test_value")
        else:
            args.append(1.0)

    result_text, result_details = predict_wrapper(*args)

    assert "❌ **Erreur lors de la prédiction**" in result_text
    assert result_details["error"] == "Erreur de prédiction"


def test_predict_from_ui_matricule_handling(sample_input):
    """Teste la gestion du matricule optionnel."""
    with patch("app.ui.create_prediction_full_service") as mock_service, patch(
        "app.ui.SessionLocal"
    ) as mock_session:
        db = MagicMock()
        mock_session.return_value = db
        mock_service.return_value.output.prediction = 1
        mock_service.return_value.output.probability = 0.8

        # Utiliser sample_input et modifier le matricule
        test_input = sample_input.copy()
        test_input["matricule"] = ""

        result = predict_from_ui(**test_input)

        # Vérifier que le service a été appelé avec matricule=None
        called_args = mock_service.call_args[0][1]
        assert called_args.matricule is None
        assert result == (0.8, "🚪 Quittera l'entreprise")
