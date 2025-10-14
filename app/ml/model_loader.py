from pathlib import Path

import joblib

MODEL_PATH = Path(__file__).resolve().parent / "random_forest_pipeline.pkl"


def load_model():
    print(f"🔍 Chargement du modèle depuis {MODEL_PATH}")
    model = joblib.load(MODEL_PATH)
    print("✅ Modèle chargé avec succès !")
    return model


model = load_model()
