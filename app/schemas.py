from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class PredictionInputBase(BaseModel):
    age: int
    genre: str
    revenu_mensuel: float
    nombre_experiences_precedentes: int
    annee_experience_totale: int
    annees_dans_l_entreprise: int
    annees_dans_le_poste_actuel: int
    satisfaction_employee_environnement: float
    niveau_hierarchique_poste: int
    satisfaction_employee_nature_travail: float
    satisfaction_employee_equipe: float
    satisfaction_employee_equilibre_pro_perso: float
    note_evaluation_actuelle: float
    heure_supplementaires: bool
    augmentation_salaire_precedente: bool
    nombre_participation_pee: int
    nb_formations_suivies: int
    distance_domicile_travail: float
    niveau_education: str
    frequence_deplacement: str
    annees_depuis_la_derniere_promotion: int
    annes_sous_responsable_actuel: int

    # Variables catégorielles
    departement_Consulting: bool
    departement_RH: bool
    statut_marital_Divorce: bool
    statut_marital_Marie: bool
    poste_Cadre_Commercial: bool
    poste_Consultant: bool
    poste_Directeur_Technique: bool
    poste_Manager: bool
    poste_Representant_Commercial: bool
    poste_RH: bool
    poste_Senior_Manager: bool
    poste_Tech_Lead: bool
    domaine_etude_Entrepreunariat: bool
    domaine_etude_Infra_Cloud: bool
    domaine_etude_Marketing: bool
    domaine_etude_RH: bool
    domaine_etude_Transformation_Digitale: bool

    # Variables dérivées
    mobilite_interne_ratio: float
    ratio_anciennete: float
    delta_evaluation: float


class PredictionInputCreate(PredictionInputBase):
    """Schéma utilisé pour la création (POST)"""

    pass


class PredictionInputResponse(PredictionInputBase):
    """Schéma utilisé pour les retours (GET / prédiction)"""

    id: int

    class Config:
        orm_mode = True  # 👈 permet de lire les objets SQLAlchemy


class HealthResponse(BaseModel):
    """Schema for health check responses"""

    status: str
    timestamp: datetime


class GenericResponse(BaseModel):
    """Schema for generic API responses"""

    message: str
    data: Optional[Any] = None
    timestamp: datetime
