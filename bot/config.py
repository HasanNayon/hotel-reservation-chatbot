"""Centralized configuration for dataset and resources."""
from __future__ import annotations

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

TRAINING_DATA_PATH = DATA_DIR / "training_data.csv"
HOTEL_INFO_PATH = DATA_DIR / "hotel_info.csv"
ROOM_TYPES_PATH = DATA_DIR / "room_types.csv"
AMENITY_FAQ_PATH = DATA_DIR / "amenity_faq.csv"
RESPONSE_TEMPLATES_PATH = DATA_DIR / "response_templates.csv"

MODEL_DIR = BASE_DIR / "artifacts"
MODEL_PATH = MODEL_DIR / "intent_classifier.joblib"
VECTORIZER_PATH = MODEL_DIR / "tfidf_vectorizer.joblib"


def ensure_model_dir() -> None:
    """Create artifact folder if missing."""
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
