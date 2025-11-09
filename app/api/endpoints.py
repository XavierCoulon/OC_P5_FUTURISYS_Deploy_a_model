import os
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import inspect
from sqlalchemy.orm import Session

from app.core.database import engine, get_db
from app.schemas import (
    PredictionFullResponse,
    PredictionInputCreate,
    PredictionInputResponse,
)
from app.services import (
    create_prediction_full_service,
    delete_prediction_input,
    get_prediction_input_by_id,
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
    return {
        "message": "Welcome to Futurisys ML API",
        "api_version": os.getenv("API_VERSION", "dev"),
    }


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
                edge_line = "    " + table + "||--||" + referred + " :" + rel_name  # type: ignore
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
    payload: PredictionInputCreate,
    db: Session = Depends(get_db),
):
    return create_prediction_full_service(db, payload)


@api_router.get(
    "/predictions",
    tags=["Prédictions"],
    summary="Lister les entrées de prédiction",
    description="Renvoie la liste paginée des entrées enregistrées dans la base de données. Permet de filtrer par matricule.",
    response_model=list[PredictionInputResponse],
    response_description="Liste des entrées enregistrées, avec leur horodatage de création.",
)
def list_predictions(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 10,
    matricule: str | None = None,
):
    """
    Liste les entrées de prédiction stockées, avec option de filtrage par matricule.
    """
    return get_prediction_inputs(db, skip, limit, matricule)


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
    prediction = get_prediction_input_by_id(db, prediction_id)
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
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
        204: {"description": "Prédiction supprimée avec succès"},
        404: {"description": "Prédiction introuvable"},
    },
)
def delete_prediction(prediction_id: int, db: Session = Depends(get_db)):
    """
    Supprime une entrée de prédiction par son ID.
    """
    success = delete_prediction_input(db, prediction_id)
    if not success:
        raise HTTPException(status_code=404, detail="Prediction not found")
    return Response(status_code=204)
