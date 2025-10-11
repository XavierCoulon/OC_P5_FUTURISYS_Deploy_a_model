# app/models.py
from sqlalchemy import Boolean, Column, Float, Integer, String

from app.core.database import Base


class PredictionInput(Base):
    __tablename__ = "prediction_inputs"

    id = Column(Integer, primary_key=True, index=True)
    age = Column(Integer)
    genre = Column(String)
    revenu_mensuel = Column(Float)
    nombre_experiences_precedentes = Column(Integer)
    annee_experience_totale = Column(Integer)
    annees_dans_l_entreprise = Column(Integer)
    annees_dans_le_poste_actuel = Column(Integer)
    satisfaction_employee_environnement = Column(Float)
    niveau_hierarchique_poste = Column(Integer)
    satisfaction_employee_nature_travail = Column(Float)
    satisfaction_employee_equipe = Column(Float)
    satisfaction_employee_equilibre_pro_perso = Column(Float)
    note_evaluation_actuelle = Column(Float)
    heure_supplementaires = Column(Boolean)
    augmentation_salaire_precedente = Column(Boolean)
    nombre_participation_pee = Column(Integer)
    nb_formations_suivies = Column(Integer)
    distance_domicile_travail = Column(Float)
    niveau_education = Column(String)
    frequence_deplacement = Column(String)
    annees_depuis_la_derniere_promotion = Column(Integer)
    annes_sous_responsable_actuel = Column(Integer)

    # Variables catégorielles (dummy variables)
    departement_Consulting = Column(Boolean)
    departement_RH = Column(Boolean)
    statut_marital_Divorce = Column(Boolean)
    statut_marital_Marie = Column(Boolean)
    poste_Cadre_Commercial = Column(Boolean)
    poste_Consultant = Column(Boolean)
    poste_Directeur_Technique = Column(Boolean)
    poste_Manager = Column(Boolean)
    poste_Representant_Commercial = Column(Boolean)
    poste_RH = Column(Boolean)
    poste_Senior_Manager = Column(Boolean)
    poste_Tech_Lead = Column(Boolean)
    domaine_etude_Entrepreunariat = Column(Boolean)
    domaine_etude_Infra_Cloud = Column(Boolean)
    domaine_etude_Marketing = Column(Boolean)
    domaine_etude_RH = Column(Boolean)
    domaine_etude_Transformation_Digitale = Column(Boolean)

    # Variables dérivées
    mobilite_interne_ratio = Column(Float)
    ratio_anciennete = Column(Float)
    delta_evaluation = Column(Float)
