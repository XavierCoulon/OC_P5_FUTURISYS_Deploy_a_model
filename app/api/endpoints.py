from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
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

    result = create_prediction_input(db, prediction_data)
    return result


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
