from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, model_validator
from pydantic.fields import Field

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
    age: int = Field(
        ...,
        description="Âge de l’employé",
        examples=[35],
        ge=18,
        le=70,
    )
    matricule: Optional[str] = Field(
        None,
        description="Matricule unique de l’employé",
        examples=["M12345"],
    )
    genre: Genre = Field(
        ...,
        description="Genre de l’employé",
        examples=["M"],  # Enum: "M", "F"
    )
    revenu_mensuel: float = Field(
        ...,
        description="Revenu mensuel en euros",
        examples=[3200.50],
    )
    nombre_experiences_precedentes: int = Field(
        ...,
        description="Nombre d’expériences professionnelles précédentes",
        examples=[3],
    )
    annee_experience_totale: int = Field(
        ...,
        description="Années d’expérience totale",
        examples=[10],
    )
    annees_dans_l_entreprise: int = Field(
        ...,
        description="Ancienneté dans l’entreprise (en années)",
        examples=[5],
    )
    annees_dans_le_poste_actuel: int = Field(
        ...,
        description="Nombre d’années dans le poste actuel",
        examples=[3],
    )
    satisfaction_employee_environnement: SatisfactionEmployee = Field(
        ...,
        description="Satisfaction de l’environnement de travail (0–5)",
        examples=[4],
    )
    niveau_hierarchique_poste: NiveauHierarchiquePoste = Field(
        ...,
        description="Niveau hiérarchique du poste (1–5)",
        examples=[3],
    )
    satisfaction_employee_nature_travail: SatisfactionEmployee = Field(
        ...,
        description="Satisfaction concernant la nature du travail (0–5)",
        examples=[5],
    )
    satisfaction_employee_equipe: SatisfactionEmployee = Field(
        ...,
        description="Satisfaction vis-à-vis de l’équipe (0–5)",
        examples=[4],
    )
    satisfaction_employee_equilibre_pro_perso: SatisfactionEmployee = Field(
        ...,
        description="Satisfaction de l’équilibre vie pro/perso (0–5)",
        examples=[3],
    )
    note_evaluation_actuelle: NoteEvaluation = Field(
        ...,
        description="Note de la dernière évaluation (0–5)",
        examples=[4],
    )
    heure_supplementaires: OuiNon = Field(
        ...,
        description="Effectue des heures supplémentaires",
        examples=["Oui"],  # Enum: "Oui", "Non"
    )
    augmentation_salaire_precedente: float = Field(
        ...,
        description="Dernière augmentation de salaire (en %)",
        examples=[3.5],
    )
    nombre_participation_pee: int = Field(
        ...,
        description="Nombre de participations au plan d’épargne entreprise",
        examples=[2],
    )
    nb_formations_suivies: int = Field(
        ...,
        description="Nombre de formations suivies",
        examples=[5],
    )
    distance_domicile_travail: float = Field(
        ...,
        description="Distance domicile–travail (km)",
        examples=[12.3],
    )
    niveau_education: NiveauEducation = Field(
        ...,
        description="Niveau d’éducation (1–5)",
        examples=[4],
    )
    frequence_deplacement: FrequenceDeplacement = Field(
        ...,
        description="Fréquence des déplacements",
        examples=["Occasionnel"],  # Enum: "Aucun", "Occasionnel", "Frequent"
    )
    annees_depuis_la_derniere_promotion: int = Field(
        ...,
        description="Années depuis la dernière promotion",
        examples=[2],
    )
    annes_sous_responsable_actuel: int = Field(
        ...,
        description="Années sous le responsable actuel",
        examples=[3],
    )
    departement: Departement = Field(
        ...,
        description="Département d’affectation",
        examples=[
            "Consulting"
        ],  # Enum: "Consulting", "Commercial", "Ressources Humaines"
    )
    statut_marital: StatutMarital = Field(
        ...,
        description="Statut marital",
        examples=["Marié(e)"],
    )
    poste: Poste = Field(
        ...,
        description="Poste actuel",
        examples=["Consultant"],
    )
    domaine_etude: DomaineEtude = Field(
        ...,
        description="Domaine d’étude ou de formation principal",
        examples=["Infra & Cloud"],
    )
    mobilite_interne_ratio: float = Field(
        ...,
        description="Ratio de mobilité interne (fréquence de changements internes)",
        examples=[0.2],
    )
    ratio_anciennete: float = Field(
        ...,
        description="Ratio ancienneté / expérience totale",
        examples=[0.5],
    )
    delta_evaluation: float = Field(
        ...,
        description="Écart entre la note actuelle et la moyenne des notes précédentes",
        examples=[-0.3],
    )

    model_config = ConfigDict(from_attributes=True)


class PredictionInputCreate(PredictionInputBase):
    """Schéma utilisé pour la création (POST)"""

    @model_validator(mode="after")
    def check_coherence_globale(self) -> "PredictionInputCreate":
        """
        Valide la cohérence logique entre plusieurs champs :
        - Le matricule, s’il est fourni, doit commencer par un M.
        - Les années dans le poste et dans l’entreprise ne peuvent pas dépasser l’expérience totale.
        - L’expérience totale ne peut pas être inférieure à ces valeurs.
        - Le ratio de mobilité interne doit être compris entre 0 et 1.
        """

        # --- Vérification sur le matricule ---
        if self.matricule is not None and not self.matricule.startswith("M"):
            raise ValueError("Le matricule doit commencer par un M.")

        # --- Vérifications sur les années ---
        if (
            self.annee_experience_totale is not None
            and self.annees_dans_le_poste_actuel is not None
            and self.annees_dans_le_poste_actuel > self.annee_experience_totale
        ):
            raise ValueError(
                "Le nombre d’années dans le poste actuel ne peut pas dépasser l’expérience totale."
            )

        if (
            self.annee_experience_totale is not None
            and self.annees_dans_l_entreprise is not None
            and self.annees_dans_l_entreprise > self.annee_experience_totale
        ):
            raise ValueError(
                "L’ancienneté dans l’entreprise ne peut pas dépasser l’expérience totale."
            )

        if (
            self.annee_experience_totale is not None
            and self.annees_dans_l_entreprise is not None
            and self.annee_experience_totale < self.annees_dans_l_entreprise
        ):
            raise ValueError(
                "L’expérience totale ne peut pas être inférieure à l’ancienneté dans l’entreprise."
            )

        # --- Vérification sur la mobilité ---
        if self.mobilite_interne_ratio is not None and not (
            0 <= self.mobilite_interne_ratio <= 1
        ):
            raise ValueError(
                "Le ratio de mobilité interne doit être compris entre 0 et 1."
            )

        # --- Vérification sur le ratio d'ancienneté ---
        if self.ratio_anciennete is not None and (
            self.ratio_anciennete < 0 or self.ratio_anciennete > 1
        ):
            raise ValueError("Le ratio d’ancienneté doit être compris entre 0 et 1.")

        # --- Vérification sur l'écart d'évaluation ---
        if self.delta_evaluation is not None and (
            self.delta_evaluation < -5 or self.delta_evaluation > 5
        ):
            raise ValueError("L’écart d’évaluation doit être compris entre -5 et 5.")

        return self


class PredictionInputResponse(PredictionInputBase):
    """Schéma utilisé pour les retours (GET / prédiction)"""

    id: int = Field(
        ...,
        description="Identifiant unique de l’entrée",
        examples=[101],
    )
    created_at: datetime = Field(
        ...,
        description="Date et heure de création automatique (UTC, ISO 8601)",
        examples=["2025-10-15T18:53:48.259Z"],
    )
    prediction_output: PredictionOutputResponse | None = Field(
        default=None,
        description="Sortie de prédiction associée à cette entrée",
    )

    model_config = ConfigDict(from_attributes=True)


class PredictionOutputBase(BaseModel):
    prediction: int = Field(
        ...,
        description="Résultat brut (0 = reste, 1 = quitte l’entreprise)",
        examples=[1],
    )
    probability: float = Field(
        ...,
        description="Probabilité associée (0–1)",
        examples=[0.78],
    )
    threshold: float = Field(
        ...,
        description="Seuil de décision utilisé pour la classification",
        examples=[0.5],
    )

    model_config = ConfigDict(from_attributes=True)


class PredictionOutputCreate(PredictionOutputBase):
    """Schéma pour créer un enregistrement de sortie"""

    prediction_input_id: int


class PredictionOutputResponse(PredictionOutputBase):
    """Schéma de sortie complet (inclut la clé étrangère)"""

    id: int
    prediction_input_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PredictionFullResponse(BaseModel):
    input: PredictionInputResponse
    output: PredictionOutputResponse

    model_config = ConfigDict(from_attributes=True)


class HealthResponse(BaseModel):
    """Schema for health check responses"""

    status: str
    timestamp: datetime


class GenericResponse(BaseModel):
    """Schema for generic API responses"""

    message: str
    data: Optional[Any] = None
    timestamp: datetime
