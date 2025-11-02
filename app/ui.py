# flake8: noqa=E225
# app/ui.py
import os

import gradio as gr
from gradio import themes

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

# === Ordre des features ===
FEATURE_ORDER = [
    "age",
    "genre",
    "revenu_mensuel",
    "nombre_experiences_precedentes",
    "annee_experience_totale",
    "annees_dans_l_entreprise",
    "annees_dans_le_poste_actuel",
    "satisfaction_employee_environnement",
    "niveau_hierarchique_poste",
    "satisfaction_employee_nature_travail",
    "satisfaction_employee_equipe",
    "satisfaction_employee_equilibre_pro_perso",
    "note_evaluation_actuelle",
    "heure_supplementaires",
    "augmentation_salaire_precedente",
    "nombre_participation_pee",
    "nb_formations_suivies",
    "distance_domicile_travail",
    "niveau_education",
    "frequence_deplacement",
    "annees_depuis_la_derniere_promotion",
    "annes_sous_responsable_actuel",
    "departement",
    "statut_marital",
    "poste",
    "domaine_etude",
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
def build_interface() -> gr.Interface:
    inputs = []

    version = os.getenv("API_VERSION", "dev")

    for feature in FEATURE_ORDER:
        if feature in CHOICES:
            inputs.append(gr.Dropdown(choices=CHOICES[feature], label=feature))
        elif "satisfaction" in feature or "ratio" in feature or "delta" in feature:
            inputs.append(gr.Slider(0, 10, step=0.1, label=feature))
        elif "annee" in feature or "nombre" in feature or "nb_" in feature:
            inputs.append(gr.Number(label=feature, value=0, precision=1))
        elif feature in [
            "augmentation_salaire_precedente",
            "annes_sous_responsable_actuel",
        ]:
            inputs.append(gr.Number(label=feature, value=0, precision=1))
        elif feature == "revenu_mensuel":
            inputs.append(gr.Number(label=feature, value=2500, precision=0))
        elif feature == "age":
            inputs.append(gr.Number(label="Âge", value=35, precision=0))
        elif feature == "distance_domicile_travail":
            inputs.append(gr.Slider(0, 100, step=1, label=feature))
        else:
            inputs.append(gr.Text(label=feature))

    outputs = [
        gr.Number(label="Probabilité de départ (classe 1)"),
        gr.Text(label="Verdict"),
    ]

    def predict_fn(*args):
        data = dict(zip(FEATURE_ORDER, args))
        return predict_from_ui(**data)

    theme = themes.Ocean(
        primary_hue="emerald",
        secondary_hue="sky",
        neutral_hue="zinc",
    )

    demo = gr.Interface(
        fn=predict_fn,
        inputs=inputs,
        outputs=outputs,
        title=f"Futurisys – Prédiction de départ d’un employé (v{version})",
        description="Entrez les caractéristiques d’un employé pour estimer la probabilité de départ.",
        theme=theme,
        flagging_mode="never",
        css="""
        footer { visibility: hidden; }
        #component-0 { margin-bottom: 1rem; }
        """,
    )

    return demo
