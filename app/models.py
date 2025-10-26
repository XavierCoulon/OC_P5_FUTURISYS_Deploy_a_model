# app/models.py
from sqlalchemy import DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy import Float, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.enums import (
    Departement,
    DomaineEtude,
    FrequenceDeplacement,
    Genre,
    OuiNon,
    Poste,
    StatutMarital,
)


class PredictionInput(Base):
    __tablename__ = "prediction_inputs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    age: Mapped[int] = mapped_column(Integer)
    genre: Mapped[Genre] = mapped_column(SAEnum(Genre), nullable=False)
    revenu_mensuel: Mapped[float] = mapped_column(Float)
    nombre_experiences_precedentes: Mapped[int] = mapped_column(Integer)
    annee_experience_totale: Mapped[int] = mapped_column(Integer)
    annees_dans_l_entreprise: Mapped[int] = mapped_column(Integer)
    annees_dans_le_poste_actuel: Mapped[int] = mapped_column(Integer)
    satisfaction_employee_environnement: Mapped[int] = mapped_column(Integer)
    niveau_hierarchique_poste: Mapped[int] = mapped_column(Integer)
    satisfaction_employee_nature_travail: Mapped[int] = mapped_column(Integer)
    satisfaction_employee_equipe: Mapped[int] = mapped_column(Integer)
    satisfaction_employee_equilibre_pro_perso: Mapped[int] = mapped_column(Integer)
    note_evaluation_actuelle: Mapped[int] = mapped_column(Integer)
    heure_supplementaires: Mapped[OuiNon] = mapped_column(SAEnum(OuiNon))
    augmentation_salaire_precedente: Mapped[float] = mapped_column(Float)
    nombre_participation_pee: Mapped[int] = mapped_column(Integer)
    nb_formations_suivies: Mapped[int] = mapped_column(Integer)
    distance_domicile_travail: Mapped[float] = mapped_column(Float)
    niveau_education: Mapped[int] = mapped_column(Integer)
    frequence_deplacement: Mapped[FrequenceDeplacement] = mapped_column(
        SAEnum(FrequenceDeplacement)
    )
    annees_depuis_la_derniere_promotion: Mapped[int] = mapped_column(Integer)
    annes_sous_responsable_actuel: Mapped[int] = mapped_column(Integer)
    departement: Mapped[Departement] = mapped_column(SAEnum(Departement))
    statut_marital: Mapped[StatutMarital] = mapped_column(SAEnum(StatutMarital))
    poste: Mapped[Poste] = mapped_column(SAEnum(Poste))
    domaine_etude: Mapped[DomaineEtude] = mapped_column(SAEnum(DomaineEtude))
    mobilite_interne_ratio: Mapped[float] = mapped_column(Float)
    ratio_anciennete: Mapped[float] = mapped_column(Float)
    delta_evaluation: Mapped[float] = mapped_column(Float)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relation 1:N avec PredictionOutput
    prediction_outputs = relationship(
        "PredictionOutput",
        back_populates="prediction_input",
        cascade="all, delete-orphan",
    )


class PredictionOutput(Base):
    __tablename__ = "prediction_outputs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    prediction_input_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("prediction_inputs.id", ondelete="CASCADE"), nullable=False
    )
    prediction: Mapped[int] = mapped_column(Integer, nullable=False)
    probability: Mapped[float] = mapped_column(Float, nullable=False)
    threshold: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relation vers PredictionInput
    prediction_input = relationship(
        "PredictionInput", back_populates="prediction_outputs"
    )
