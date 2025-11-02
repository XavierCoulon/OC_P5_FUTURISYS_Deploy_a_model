from datetime import UTC, datetime
from enum import Enum

import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

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
    applique l’encodage nécessaire avant sauvegarde.
    """

    data_dict = {
        k: (v.value if isinstance(v, Enum) else v) for k, v in data.model_dump().items()
    }
    db_prediction = PredictionInput(**data_dict)

    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)

    return db_prediction


def get_prediction_inputs(db: Session, skip: int = 0, limit: int = 10):
    """
    Retourne la liste des entrées enregistrées.
    """
    return db.query(PredictionInput).offset(skip).limit(limit).all()


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
    - Enregistre l'entrée (input)
    - Applique le modèle ML
    - Enregistre la sortie (output)
    - Retourne un PredictionFullResponse complet
    """

    # 1️⃣ Sauvegarder l’entrée brute
    db_input = PredictionInput(**payload.model_dump())
    db.add(db_input)
    db.commit()
    db.refresh(db_input)

    # 2️⃣ Préparer les données pour le modèle
    X = pd.DataFrame([payload.model_dump()]).replace("", np.nan)

    # 3️⃣ Prédire via le pipeline ML
    proba = float(model.predict_proba(X)[0][1])
    prediction = int(model.predict(X)[0])
    threshold = 0.5

    # 4️⃣ Sauvegarder le résultat
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
