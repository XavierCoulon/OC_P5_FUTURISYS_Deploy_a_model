import logging
import os
from pathlib import Path

import joblib
from huggingface_hub import hf_hub_download

MODEL_PATH = Path(__file__).resolve().parent / "random_forest_pipeline.pkl"
# Nom du dépôt et fichier sur Hugging Face
HF_REPO_ID = "XavierCoulon/futurisys-model"
HF_FILENAME = "random_forest_pipeline.pkl"
if os.environ.get("GITHUB_ACTIONS") == "true":
    # En CI GitHub → dossier temporaire accessible
    HF_DIRECTORY = Path("/tmp/.cache")
else:
    # En local / Docker Hugging Face
    HF_DIRECTORY = Path("/app/.cache")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def load_model():
    """Charge le modèle ML depuis le fichier en local ou depuis Hugging Face."""
    logging.info(f"🔍 Tentative de chargement du modèle depuis {MODEL_PATH}")
    if MODEL_PATH.exists():
        try:
            model = joblib.load(MODEL_PATH)
            logging.info("✅ Modèle chargé depuis le fichier local.")
            return model
        except Exception as e:
            logging.error(f"❌ Échec du chargement local : {e}")
    logging.info("🌐 Téléchargement du modèle depuis Hugging Face...")
    try:
        os.makedirs(HF_DIRECTORY, exist_ok=True)
        model_path = hf_hub_download(
            repo_id=HF_REPO_ID,
            filename=HF_FILENAME,
            cache_dir=HF_DIRECTORY,
            force_download=True,
        )
        model = joblib.load(model_path)
        logging.info("✅ Modèle téléchargé et chargé depuis Hugging Face.")
        return model
    except Exception as e:
        logging.error(f"❌ Échec du téléchargement depuis Hugging Face : {e}")
        raise RuntimeError("Impossible de charger le modèle ML.") from e


model = load_model()
