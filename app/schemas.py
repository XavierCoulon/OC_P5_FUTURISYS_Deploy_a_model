from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel

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


class PredictionInputBase(BaseModel):
    age: int
    genre: Genre
    revenu_mensuel: float
    nombre_experiences_precedentes: int
    annee_experience_totale: int
    annees_dans_l_entreprise: int
    annees_dans_le_poste_actuel: int
    satisfaction_employee_environnement: SatisfactionEmployee
    niveau_hierarchique_poste: NiveauHierarchiquePoste
    satisfaction_employee_nature_travail: SatisfactionEmployee
    satisfaction_employee_equipe: SatisfactionEmployee
    satisfaction_employee_equilibre_pro_perso: SatisfactionEmployee
    note_evaluation_actuelle: NoteEvaluation
    heure_supplementaires: OuiNon
    augmentation_salaire_precedente: float
    nombre_participation_pee: int
    nb_formations_suivies: int
    distance_domicile_travail: float
    niveau_education: NiveauEducation
    frequence_deplacement: FrequenceDeplacement
    annees_depuis_la_derniere_promotion: int
    annes_sous_responsable_actuel: int

    # Variables catégorielles
    departement: Departement
    statut_marital: StatutMarital
    poste: Poste
    domaine_etude: DomaineEtude

    # Variables dérivées
    mobilite_interne_ratio: float
    ratio_anciennete: float
    delta_evaluation: float

    class Config:
        orm_mode = True


class PredictionInputCreate(PredictionInputBase):
    """Schéma utilisé pour la création (POST)"""

    pass


class PredictionInputResponse(PredictionInputBase):
    """Schéma utilisé pour les retours (GET / prédiction)"""

    id: int

    class Config:
        orm_mode = True  # 👈 permet de lire les objets SQLAlchemy


class PredictionOutputBase(BaseModel):
    prediction: int
    probability: float
    threshold: float

    class Config:
        orm_mode = True


class PredictionOutputCreate(PredictionOutputBase):
    """Schéma pour créer un enregistrement de sortie"""

    prediction_input_id: int


class PredictionOutputResponse(PredictionOutputBase):
    """Schéma de sortie complet (inclut la clé étrangère)"""

    id: int
    prediction_input_id: int


class PredictionFullResponse(BaseModel):
    input: PredictionInputResponse
    output: PredictionOutputResponse


class HealthResponse(BaseModel):
    """Schema for health check responses"""

    status: str
    timestamp: datetime


class GenericResponse(BaseModel):
    """Schema for generic API responses"""

    message: str
    data: Optional[Any] = None
    timestamp: datetime
