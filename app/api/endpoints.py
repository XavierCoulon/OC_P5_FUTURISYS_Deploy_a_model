from datetime import datetime

import numpy as np
import pandas as pd
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.ml.model_loader import model  # Import the loaded model
from app.models import PredictionInput
from app.schemas import PredictionInputCreate, PredictionInputResponse
from app.services import create_prediction_input, get_prediction_inputs

api_router = APIRouter()


@api_router.get("/")
async def root():
    return {"message": "Welcome to Futurisys ML API"}


@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}


@api_router.post("/predictions", response_model=PredictionInputResponse)
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

    print(
        f"🔮 Prédiction: {y_pred[0]}, Probabilité: {y_proba[0]: .3f}, Seuil utilisé: {THRESHOLD}"
    )

    return db_input


@api_router.get("/predictions", response_model=list[PredictionInputResponse])
def list_predictions(db: Session = Depends(get_db), skip: int = 0, limit: int = 10):
    """
    Liste les entrées de prédiction stockées.
    """
    return get_prediction_inputs(db, skip=skip, limit=limit)


@api_router.get("/predictions/{prediction_id}", response_model=PredictionInputResponse)
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


@api_router.delete("/predictions/{prediction_id}")
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
