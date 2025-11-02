from datetime import UTC, datetime
from enum import Enum

import numpy as np
import pandas as pd
from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from app.ml.model_loader import model
from app.models import PredictionInput, PredictionOutput
from app.schemas import (
    PredictionFullResponse,
    PredictionInputCreate,
    PredictionInputResponse,
    PredictionOutputCreate,
    PredictionOutputResponse,
)


def create_prediction_input(
    db: Session, data: PredictionInputCreate
) -> PredictionInput:
    """
    Crée une nouvelle entrée de prédiction dans la base,
    applique l'encodage nécessaire avant sauvegarde.
    """

    # Vérifier l'unicité du matricule si fourni
    if data.matricule is not None:
        existing_prediction = (
            db.query(PredictionInput)
            .filter(PredictionInput.matricule == data.matricule)
            .first()
        )
        if existing_prediction:
            raise HTTPException(
                status_code=409,
                detail=f"Un employé avec le matricule '{data.matricule}' existe déjà.",
            )

    data_dict = {
        k: (v.value if isinstance(v, Enum) else v) for k, v in data.model_dump().items()
    }
    db_prediction = PredictionInput(**data_dict)

    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)

    return db_prediction


def get_prediction_inputs(
    db: Session, skip: int = 0, limit: int = 10, matricule: str | None = None
):
    """
    Retourne la liste des entrées enregistrées avec les relations chargées.
    Permet de filtrer par matricule si spécifié.
    """
    query = db.query(PredictionInput).options(
        joinedload(PredictionInput.prediction_output)
    )

    if matricule:
        query = query.filter(PredictionInput.matricule == matricule)

    return query.offset(skip).limit(limit).all()


def get_prediction_input_by_id(
    db: Session, prediction_id: int
) -> PredictionInput | None:
    """
    Retourne une entrée de prédiction par son ID avec les relations chargées.
    """
    return (
        db.query(PredictionInput)
        .options(joinedload(PredictionInput.prediction_output))
        .filter(PredictionInput.id == prediction_id)
        .first()
    )


def delete_prediction_input(db: Session, prediction_id: int) -> bool:
    """
    Supprime une entrée de prédiction par son ID.
    Retourne True si la suppression a réussi, False si l'entrée n'existe pas.
    """
    prediction = (
        db.query(PredictionInput).filter(PredictionInput.id == prediction_id).first()
    )
    if not prediction:
        return False

    db.delete(prediction)
    db.commit()
    return True


def create_prediction_output(
    db: Session, data: PredictionOutputCreate
) -> PredictionOutput:
    """
    Crée un nouvel enregistrement de sortie de prédiction.
    """
    db_output = PredictionOutput(**data.model_dump())
    db.add(db_output)
    db.commit()
    db.refresh(db_output)
    return db_output


def get_prediction_outputs(db: Session, skip: int = 0, limit: int = 10):
    """
    Retourne la liste des sorties enregistrées.
    """
    return db.query(PredictionOutput).offset(skip).limit(limit).all()


def create_prediction_full_service(
    db: Session,
    payload: PredictionInputCreate,
) -> PredictionFullResponse:
    """
    Service métier complet :
    - Vérifie l'unicité du matricule
    - Enregistre l'entrée (input)
    - Supprime le matricule pour la prédiction
    - Applique le modèle ML
    - Enregistre la sortie (output)
    - Retourne un PredictionFullResponse complet
    """

    # Vérifier l'unicité du matricule si fourni
    if payload.matricule is not None:
        existing_prediction = (
            db.query(PredictionInput)
            .filter(PredictionInput.matricule == payload.matricule)
            .first()
        )
        if existing_prediction:
            raise HTTPException(
                status_code=409,
                detail=f"Un employé avec le matricule '{payload.matricule}' existe déjà.",
            )

    # Sauvegarder l'entrée brute
    db_input = PredictionInput(**payload.model_dump())
    db.add(db_input)
    db.commit()
    db.refresh(db_input)

    # Supprimer le matricule avant la prédiction
    if "matricule" in payload.model_dump():
        del payload.model_dump()["matricule"]

    # Préparer les données pour le modèle
    X = pd.DataFrame([payload.model_dump()]).replace("", np.nan)

    # Prédire via le pipeline ML
    proba = float(model.predict_proba(X)[0][1])
    prediction = int(model.predict(X)[0])
    threshold = 0.5

    # Sauvegarder le résultat
    db_output = PredictionOutput(
        prediction_input_id=db_input.id,
        prediction=prediction,
        probability=proba,
        threshold=threshold,
        created_at=datetime.now(UTC),
    )
    db.add(db_output)
    db.commit()
    db.refresh(db_output)

    # 5️⃣ Construire la réponse finale
    return PredictionFullResponse(
        input=PredictionInputResponse.model_validate(db_input),
        output=PredictionOutputResponse.model_validate(db_output),
    )
