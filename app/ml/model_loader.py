import logging
from pathlib import Path

import joblib

MODEL_PATH = Path(__file__).resolve().parent / "random_forest_pipeline.pkl"


def load_model():
    logging.info(f"🔍 Chargement du modèle depuis {MODEL_PATH}")
    if not MODEL_PATH.exists():
        logging.warning(
            "⚠️ Modèle introuvable. Chargement d’un modèle factice pour les tests."
        )

        # Petit mock compatible scikit-learn
        class DummyModel:
            def predict(self, X):
                return [0] * len(X)

            def predict_proba(self, X):
                return [[1.0, 0.0]] * len(X)

        return DummyModel()
    return joblib.load(MODEL_PATH)


model = load_model()
