# flake8: noqa=E225
# app/ui.py
import os
import subprocess

import gradio as gr

from app.core.database import SessionLocal
from app.enums import (
    Departement,
    DomaineEtude,
    FrequenceDeplacement,
    Genre,
    NiveauEducation,
    NiveauHierarchiquePoste,
    NoteEvaluation,
    OuiNon,
    Poste,
    SatisfactionEmployee,
    StatutMarital,
)
from app.schemas import PredictionInputCreate
from app.services import create_prediction_full_service

# === Clean labels mapping ===
CLEAN_LABELS = {
    "age": "Âge",
    "matricule": "Matricule (optionnel)",
    "genre": "Genre",
    "revenu_mensuel": "Revenu mensuel (€)",
    "nombre_experiences_precedentes": "Expériences précédentes",
    "annee_experience_totale": "Années d'expérience totale",
    "annees_dans_l_entreprise": "Ancienneté dans l'entreprise",
    "annees_dans_le_poste_actuel": "Années dans le poste actuel",
    "satisfaction_employee_environnement": "Satisfaction - Environnement de travail",
    "niveau_hierarchique_poste": "Niveau hiérarchique",
    "satisfaction_employee_nature_travail": "Satisfaction - Nature du travail",
    "satisfaction_employee_equipe": "Satisfaction - Équipe",
    "satisfaction_employee_equilibre_pro_perso": "Satisfaction - Équilibre vie pro/perso",
    "note_evaluation_actuelle": "Note d'évaluation actuelle",
    "heure_supplementaires": "Heures supplémentaires",
    "augmentation_salaire_precedente": "Dernière augmentation (%)",
    "nombre_participation_pee": "Participations PEE",
    "nb_formations_suivies": "Formations suivies",
    "distance_domicile_travail": "Distance domicile-travail (km)",
    "niveau_education": "Niveau d'éducation",
    "frequence_deplacement": "Fréquence des déplacements",
    "annees_depuis_la_derniere_promotion": "Années depuis dernière promotion",
    "annes_sous_responsable_actuel": "Années sous responsable actuel",
    "departement": "Département",
    "statut_marital": "Statut marital",
    "poste": "Poste",
    "domaine_etude": "Domaine d'étude",
    "mobilite_interne_ratio": "Ratio de mobilité interne",
    "ratio_anciennete": "Ratio d'ancienneté",
    "delta_evaluation": "Écart d'évaluation",
}

# === Feature organization for 2-column layout ===
PERSONAL_INFO = [
    "age",
    "matricule",
    "genre",
    "statut_marital",
    "niveau_education",
    "domaine_etude",
    "distance_domicile_travail",
]

PROFESSIONAL_INFO = [
    "revenu_mensuel",
    "nombre_experiences_precedentes",
    "annee_experience_totale",
    "annees_dans_l_entreprise",
    "annees_dans_le_poste_actuel",
    "departement",
    "poste",
    "niveau_hierarchique_poste",
    "heure_supplementaires",
    "augmentation_salaire_precedente",
    "nombre_participation_pee",
    "nb_formations_suivies",
    "frequence_deplacement",
    "annees_depuis_la_derniere_promotion",
    "annes_sous_responsable_actuel",
]

SATISFACTION_METRICS = [
    "satisfaction_employee_environnement",
    "satisfaction_employee_nature_travail",
    "satisfaction_employee_equipe",
    "satisfaction_employee_equilibre_pro_perso",
    "note_evaluation_actuelle",
    "mobilite_interne_ratio",
    "ratio_anciennete",
    "delta_evaluation",
]

# === CHOICES dynamiques à partir des Enums ===
CHOICES = {
    "genre": [e.value for e in Genre],
    "heure_supplementaires": [e.value for e in OuiNon],
    "departement": [e.value for e in Departement],
    "domaine_etude": [e.value for e in DomaineEtude],
    "frequence_deplacement": [e.value for e in FrequenceDeplacement],
    "poste": [e.value for e in Poste],
    "statut_marital": [e.value for e in StatutMarital],
    "niveau_education": [e.value for e in NiveauEducation],
    "niveau_hierarchique_poste": [int(e.value) for e in NiveauHierarchiquePoste],
    "satisfaction_employee_environnement": [int(e.value) for e in SatisfactionEmployee],
    "satisfaction_employee_nature_travail": [
        int(e.value) for e in SatisfactionEmployee
    ],
    "satisfaction_employee_equipe": [int(e.value) for e in SatisfactionEmployee],
    "satisfaction_employee_equilibre_pro_perso": [
        int(e.value) for e in SatisfactionEmployee
    ],
    "note_evaluation_actuelle": [int(e.value) for e in NoteEvaluation],
}


# === Fonction de prédiction ===
def predict_from_ui(**kwargs):
    # Nettoyer les chaînes vides pour les champs optionnels
    if kwargs.get("matricule") == "":
        kwargs["matricule"] = None

    # Convertir le dict brut en schéma Pydantic
    payload = PredictionInputCreate(**kwargs)

    # Créer une session DB manuellement
    db = SessionLocal()
    try:
        full_response = create_prediction_full_service(db, payload)
    finally:
        db.close()

    # Extraire les valeurs pour Gradio
    proba = full_response.output.probability
    verdict = (
        "🚪 Quittera l'entreprise"
        if full_response.output.prediction == 1
        else "🧑‍💼 Restera"
    )
    return float(round(proba, 3)), verdict


# === Construction de l'interface ===
def build_interface():
    """Construit l'interface Gradio avec une mise en page organisée."""

    def create_input_component(feature):
        """Crée un composant d'entrée pour une feature donnée."""
        clean_label = CLEAN_LABELS.get(feature, feature.replace("_", " ").title())

        # Valeurs par défaut réalistes pour chaque champ
        default_values = {
            "age": 35,
            "revenu_mensuel": 3500,
            "nombre_experiences_precedentes": 2,
            "annee_experience_totale": 8,
            "annees_dans_l_entreprise": 3,
            "annees_dans_le_poste_actuel": 2,
            "augmentation_salaire_precedente": 3.5,
            "nombre_participation_pee": 1,
            "nb_formations_suivies": 2,
            "distance_domicile_travail": 15,
            "annees_depuis_la_derniere_promotion": 2,
            "annes_sous_responsable_actuel": 2,
            "mobilite_interne_ratio": 0.5,
            "ratio_anciennete": 0.3,
            "delta_evaluation": 0.0,
        }

        if feature in CHOICES:
            # Dropdown pour les choix prédéfinis avec valeurs par défaut sensées
            choices_list = CHOICES[feature]

            # Valeurs par défaut spécifiques pour les dropdowns
            dropdown_defaults = {
                "genre": "Homme",  # Premier choix typique
                "heure_supplementaires": "Non",  # Plus courant
                "departement": "Research & Development",  # Département le plus commun
                "domaine_etude": "Life Sciences",  # Domaine fréquent
                "frequence_deplacement": "Travel_Rarely",  # Le plus fréquent
                "poste": "Research Scientist",  # Poste courant
                "statut_marital": "Married",  # Statut le plus fréquent
                "niveau_education": "Master",  # Niveau standard
                "niveau_hierarchique_poste": 2,  # Niveau intermédiaire
                "satisfaction_employee_environnement": 3,  # Satisfaction moyenne
                "satisfaction_employee_nature_travail": 3,
                "satisfaction_employee_equipe": 3,
                "satisfaction_employee_equilibre_pro_perso": 3,
                "note_evaluation_actuelle": 3,  # Note moyenne
            }

            default_value = dropdown_defaults.get(feature)
            if default_value is None or default_value not in choices_list:
                default_value = choices_list[0] if choices_list else None

            return gr.Dropdown(
                choices=choices_list, label=clean_label, value=default_value
            )
        elif feature == "matricule":
            # Champ texte optionnel pour le matricule
            return gr.Textbox(
                label=clean_label, placeholder="Ex: EMP001 (optionnel)", value=""
            )
        else:
            # Champ numérique avec valeur par défaut réaliste
            default_value = default_values.get(feature, 1.0)
            return gr.Number(label=clean_label, value=default_value)

    # Construction de l'interface avec layout organisé
    with gr.Blocks(
        title=f"Futurisys - Prédiction d'Attrition {get_version()}"
    ) as interface:
        gr.Markdown(
            f"# 🎯 Futurisys - Prédiction d'Attrition des Employés {get_version()}"
        )
        gr.Markdown(
            "Saisissez les informations de l'employé pour évaluer le risque d'attrition."
        )

        with gr.Row():
            # Colonne gauche - Informations personnelles
            with gr.Column():
                gr.Markdown("### 👤 Informations Personnelles")
                personal_inputs = []
                for feature in PERSONAL_INFO:
                    component = create_input_component(feature)
                    personal_inputs.append(component)

            # Colonne droite - Informations professionnelles
            with gr.Column():
                gr.Markdown("### 💼 Informations Professionnelles")
                professional_inputs = []
                for feature in PROFESSIONAL_INFO:
                    component = create_input_component(feature)
                    professional_inputs.append(component)

        # Section satisfaction (pleine largeur)
        gr.Markdown("### 📊 Indicateurs de Satisfaction et Performance")
        satisfaction_inputs = []
        with gr.Row():
            for i, feature in enumerate(SATISFACTION_METRICS):
                if i % 2 == 0 and i > 0:
                    # Nouvelle ligne tous les 2 éléments
                    with gr.Row():
                        pass
                component = create_input_component(feature)
                satisfaction_inputs.append(component)

        # Bouton de prédiction et résultats
        gr.Markdown("---")
        predict_btn = gr.Button(
            "🔮 Prédire le Risque d'Attrition", variant="primary", size="lg"
        )

        with gr.Row():
            with gr.Column():
                prediction_output = gr.Textbox(
                    label="📋 Résultat de la Prédiction", lines=3, interactive=False
                )
            with gr.Column():
                details_output = gr.JSON(label="📈 Détails Techniques", visible=True)

        # Assemblage de tous les inputs dans l'ordre requis
        all_inputs = personal_inputs + professional_inputs + satisfaction_inputs

        # Configuration de l'événement de prédiction
        predict_btn.click(
            fn=predict_wrapper,
            inputs=all_inputs,
            outputs=[prediction_output, details_output],
        )

    return interface


def predict_wrapper(*args):
    """Wrapper pour la fonction de prédiction."""
    try:
        # Ordre des features : PERSONAL_INFO + PROFESSIONAL_INFO + SATISFACTION_METRICS
        all_features = PERSONAL_INFO + PROFESSIONAL_INFO + SATISFACTION_METRICS
        data = dict(zip(all_features, args))

        # Note: CHOICES sont maintenant des listes, pas des dictionnaires
        # Les valeurs sont directement utilisables

        # Gestion du matricule optionnel
        if not data.get("matricule") or data["matricule"].strip() == "":
            data["matricule"] = None

        # Appel du service de prédiction
        probability, verdict = predict_from_ui(**data)

        # Formatage de la sortie principale
        confidence_percent = probability * 100

        main_output = f"🎯 **Prédiction**: {verdict}\n"
        main_output += f"📊 **Probabilité**: {confidence_percent:.1f}%\n"

        if "Quittera" in verdict:
            main_output += "⚠️ Cet employé présente un risque d'attrition."
        else:
            main_output += "✅ Cet employé devrait rester dans l'entreprise."

        # Détails techniques
        details = {
            "prediction": verdict,
            "probability": probability,
            "confidence_percent": f"{confidence_percent:.1f}%",
            "input_data": {k: v for k, v in data.items() if v is not None},
        }

        return main_output, details

    except Exception as e:
        error_msg = f"❌ **Erreur lors de la prédiction**: {str(e)}"
        return error_msg, {"error": str(e)}


def get_version():
    """Récupère la version de l'application."""
    try:
        # Essayer de récupérer depuis les variables d'environnement
        version = os.getenv("API_VERSION")
        if version and version != "vdev":
            return f"v{version}"

        # Essayer de récupérer depuis git
        try:
            result = subprocess.run(
                ["git", "describe", "--tags", "--exact-match"],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(__file__),
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except (subprocess.SubprocessError, FileNotFoundError):
            pass

        # Fallback
        return "v1.0.0"
    except Exception:
        return "v1.0.0"


if __name__ == "__main__":
    app = build_interface()
    # Le paramètre share=True crée un tunnel SSH temporaire (valide 72h)
    app.launch(share=True, inbrowser=True)
