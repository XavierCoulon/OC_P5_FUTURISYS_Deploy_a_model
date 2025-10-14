from enum import Enum, IntEnum


class FrequenceDeplacement(str, Enum):
    aucun = "Aucun"
    occasionnel = "Occasionnel"
    frequent = "Frequent"


class Genre(str, Enum):
    homme = "H"
    femme = "F"


class StatutMarital(str, Enum):
    marie = "Marié(e)"
    celibataire = "Célibataire"
    divorce = "Divorcé(e)"


class Departement(str, Enum):
    consulting = "Consulting"
    commercial = "Commercial"
    rh = "Ressources Humaines"


class Poste(str, Enum):
    cadre_commercial = "Cadre Commercial"
    assistante_de_direction = "Assistante de Direction"
    consultant = "Consultant"
    tech_lead = "Tech Lead"
    manager = "Manager"
    senior_manager = "Senior Manager"
    representant_commercial = "Représentant Commercial"
    directeur_technique = "Directeur Technique"
    rh = "Ressources Humaines"


class DomaineEtude(str, Enum):
    infra_cloud = "Infra & Cloud"
    transformation_digitale = "Transformation Digitale"
    marketing = "Marketing"
    entrepreunariat = "Entrepreunariat"
    autre = "Autre"
    rh = "Ressources Humaines"


class OuiNon(str, Enum):
    oui = "Oui"
    non = "Non"


class NiveauHierarchiquePoste(IntEnum):
    un = 1
    deux = 2
    trois = 3
    quatre = 4
    cinq = 5


class SatisfactionEmployee(IntEnum):
    zero = 0
    un = 1
    deux = 2
    trois = 3
    quatre = 4
    cinq = 5


class NoteEvaluation(IntEnum):
    zero = 0
    un = 1
    deux = 2
    trois = 3
    quatre = 4
    cinq = 5


class NiveauEducation(IntEnum):
    un = 1
    deux = 2
    trois = 3
    quatre = 4
    cinq = 5
