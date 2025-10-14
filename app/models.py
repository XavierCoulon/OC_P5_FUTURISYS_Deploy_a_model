# app/models.py
from sqlalchemy import Column
from sqlalchemy import Enum as SAEnum
from sqlalchemy import Float, ForeignKey, Integer
from sqlalchemy.orm import relationship

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

    id = Column(Integer, primary_key=True, index=True)
    age = Column(Integer)
    # store string enums as SQLAlchemy Enum for readability
    genre = Column(SAEnum(Genre), nullable=False)
    revenu_mensuel = Column(Float)
    nombre_experiences_precedentes = Column(Integer)
    annee_experience_totale = Column(Integer)
    annees_dans_l_entreprise = Column(Integer)
    annees_dans_le_poste_actuel = Column(Integer)
    # store numeric enums as integers
    satisfaction_employee_environnement = Column(Integer)
    niveau_hierarchique_poste = Column(Integer)
    satisfaction_employee_nature_travail = Column(Integer)
    satisfaction_employee_equipe = Column(Integer)
    satisfaction_employee_equilibre_pro_perso = Column(Integer)
    note_evaluation_actuelle = Column(Integer)
    heure_supplementaires = Column(SAEnum(OuiNon))
    augmentation_salaire_precedente = Column(Float)
    nombre_participation_pee = Column(Integer)
    nb_formations_suivies = Column(Integer)
    distance_domicile_travail = Column(Float)
    niveau_education = Column(Integer)
    frequence_deplacement = Column(SAEnum(FrequenceDeplacement))
    annees_depuis_la_derniere_promotion = Column(Integer)
    annes_sous_responsable_actuel = Column(Integer)

    # Variables catégorielles
    departement = Column(SAEnum(Departement))
    statut_marital = Column(SAEnum(StatutMarital))
    poste = Column(SAEnum(Poste))
    domaine_etude = Column(SAEnum(DomaineEtude))

    # Variables dérivées
    mobilite_interne_ratio = Column(Float)
    ratio_anciennete = Column(Float)
    delta_evaluation = Column(Float)

    # Relation 1:N avec PredictionOutput
    prediction_outputs = relationship(
        "PredictionOutput",
        back_populates="prediction_input",
        cascade="all, delete-orphan",
    )


class PredictionOutput(Base):
    __tablename__ = "prediction_outputs"

    id = Column(Integer, primary_key=True, index=True)
    prediction_input_id = Column(
        Integer, ForeignKey("prediction_inputs.id", ondelete="CASCADE"), nullable=False
    )
    prediction = Column(Integer, nullable=False)
    probability = Column(Float, nullable=False)
    threshold = Column(Float, nullable=False)

    # Relation vers PredictionInput
    prediction_input = relationship(
        "PredictionInput", back_populates="prediction_outputs"
    )
