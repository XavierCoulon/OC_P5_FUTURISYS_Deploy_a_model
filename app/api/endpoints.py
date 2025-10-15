from datetime import datetime

import numpy as np
import pandas as pd
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import inspect
from sqlalchemy.orm import Session

from app.core.database import engine, get_db
from app.ml.model_loader import model  # Import the loaded model
from app.models import PredictionInput
from app.schemas import (
    PredictionFullResponse,
    PredictionInputCreate,
    PredictionInputResponse,
    PredictionOutputCreate,
)
from app.services import (
    create_prediction_input,
    create_prediction_output,
    get_prediction_inputs,
)

api_router = APIRouter(
    prefix="",
    responses={404: {"description": "Ressource non trouvée"}},
)


@api_router.get(
    "/",
    tags=["Général"],
    summary="Page d’accueil de l’API",
    description="Renvoie un message d’accueil indiquant que l’API Futurisys ML est en ligne.",
    response_description="Message de bienvenue au format JSON",
)
async def root():
    return {"message": "Welcome to Futurisys ML API"}


@api_router.get(
    "/health",
    tags=["Général"],
    summary="Vérification de l’état du service",
    description="Renvoie l’état de santé de l’API ainsi qu’un horodatage pour vérifier son bon fonctionnement.",
    response_description="Statut du service et horodatage",
    status_code=status.HTTP_200_OK,
)
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}


@api_router.get(
    "/erd",
    tags=["Documentation"],
    summary="Visualiser le schéma de la base (ERD)",
    description=(
        "Génère une représentation **Mermaid** du schéma relationnel de la base de données. "
        "Permet de visualiser les tables, leurs colonnes et leurs relations."
    ),
    response_description="Schéma ERD au format Markdown compatible Mermaid",
    response_class=Response,
)
def get_erd_mermaid():
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    lines = ["```mermaid", "erDiagram"]

    for table in tables:
        lines.append(f"    {table} {{")
        for column in inspector.get_columns(table):
            col_type = str(column["type"])
            col_name = column["name"]
            lines.append(f"        {col_type} {col_name}")
        lines.append("    }")

    for table in tables:
        for fk in inspector.get_foreign_keys(table):
            referred = fk.get("referred_table")
            if referred:
                rel_name = fk.get("name", "fk")
                edge_line = "    " + table + "}o--||" + referred + " :" + rel_name  # type: ignore
                lines.append(edge_line)

    lines.append("```")
    return Response("\n".join(lines), media_type="text/markdown")


@api_router.post(
    "/predictions",
    tags=["Prédictions"],
    summary="Créer une nouvelle prédiction",
    description=(
        "Crée une nouvelle entrée de données, applique le modèle de Machine Learning et "
        "retourne la prédiction correspondante.\n\n"
        "L’entrée est enregistrée dans la base avec sa sortie associée (probabilité, seuil, résultat binaire)."
    ),
    response_model=PredictionFullResponse,
    response_description="Objet combiné contenant l’entrée enregistrée et le résultat du modèle.",
    status_code=status.HTTP_201_CREATED,
)
def create_prediction(
    prediction_data: PredictionInputCreate, db: Session = Depends(get_db)
):
    """
    Crée un nouvel enregistrement et le stocke en base.
    (Étape avant prédiction)
    """

    # Sauvegarde des données d'entrée dans la base de données
    db_input = create_prediction_input(db, prediction_data)

    data_dict = prediction_data.model_dump()  # Convertir en dictionnaire
    df = pd.DataFrame([data_dict])
    print("Données reçues pour la prédiction :", df)

    # Probabilité d'appartenance à la classe 1
    y_proba_raw = model.predict_proba(df)
    y_proba = np.array(y_proba_raw)[:, 1]

    # Application du seuil choisi (par ex. celui trouvé plus tôt)
    THRESHOLD = 0.35  # à adapter selon ton calcul métier

    # Conversion en prédiction binaire selon le seuil
    y_pred = (y_proba >= THRESHOLD).astype(int)

    # Sauvegarde des résultats de prédiction
    db_output = create_prediction_output(
        db,
        PredictionOutputCreate(
            prediction_input_id=getattr(db_input, "id"),
            prediction=y_pred[0],
            probability=y_proba[0],
            threshold=THRESHOLD,
        ),
    )

    return {
        "input": db_input,
        "output": db_output,
    }


@api_router.get(
    "/predictions",
    tags=["Prédictions"],
    summary="Lister les entrées de prédiction",
    description="Renvoie la liste paginée des entrées enregistrées dans la base de données.",
    response_model=list[PredictionInputResponse],
    response_description="Liste des entrées enregistrées, avec leur horodatage de création.",
)
def list_predictions(db: Session = Depends(get_db), skip: int = 0, limit: int = 10):
    """
    Liste les entrées de prédiction stockées.
    """
    return get_prediction_inputs(db, skip=skip, limit=limit)


@api_router.get(
    "/predictions/{prediction_id}",
    tags=["Prédictions"],
    summary="Obtenir une prédiction par ID",
    description="Récupère une entrée de prédiction précise grâce à son identifiant unique.",
    response_model=PredictionInputResponse,
    response_description="Objet contenant les informations de l’entrée demandée.",
    responses={404: {"description": "Prédiction introuvable"}},
)
def get_prediction(prediction_id: int, db: Session = Depends(get_db)):
    """
    Récupère une entrée de prédiction par son ID.
    """
    prediction = (
        db.query(PredictionInput).filter(PredictionInput.id == prediction_id).first()
    )
    if not prediction:
        return {"error": "Prediction not found"}
    return prediction


@api_router.delete(
    "/predictions/{prediction_id}",
    tags=["Prédictions"],
    summary="Supprimer une prédiction par ID",
    description=(
        "Supprime définitivement une entrée de prédiction existante dans la base de données. "
        "Cette action est irréversible."
    ),
    response_description="Message de confirmation de suppression.",
    responses={
        200: {"description": "Prédiction supprimée avec succès"},
        404: {"description": "Prédiction introuvable"},
    },
)
def delete_prediction(prediction_id: int, db: Session = Depends(get_db)):
    """
    Supprime une entrée de prédiction par son ID.
    """
    prediction = (
        db.query(PredictionInput).filter(PredictionInput.id == prediction_id).first()
    )
    if not prediction:
        return {"error": "Prediction not found"}
    db.delete(prediction)
    db.commit()
    return {"message": "Prediction deleted successfully"}
