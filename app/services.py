from enum import Enum

# Import encoders if needed in the future
# from encoders import (
#     apply_binary_encoding,
#     apply_label_encoding,
#     apply_onehot_encoding,
#     apply_ordinal_encoding,
# )
from sqlalchemy.orm import Session

from app.models import PredictionInput
from app.schemas import PredictionInputCreate

# Exemple : liste des colonnes binaires à encoder
BINARY_FIELDS = [
    "heure_supplementaires",
    "augmentation_salaire_precedente",
]


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
