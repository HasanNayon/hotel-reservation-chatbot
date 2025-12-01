"""Intent classifier built on scikit-learn with keyword fallback."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer

from .config import MODEL_PATH, VECTORIZER_PATH, ensure_model_dir
from .data_loader import TrainingRow
from .keyword_matcher import KeywordMatcher


@dataclass
class IntentPrediction:
    intent: str
    confidence: float


class IntentClassifier:
    def __init__(self, use_keyword_fallback: bool = True) -> None:
        self.pipeline: Pipeline | None = None
        self.keyword_matcher = KeywordMatcher() if use_keyword_fallback else None

    def train(self, rows: Sequence[TrainingRow]) -> None:
        ensure_model_dir()
        texts = [row.utterance for row in rows]
        labels = [row.intent for row in rows]
        self.pipeline = Pipeline(
            steps=[
                (
                    "tfidf",
                    TfidfVectorizer(
                        ngram_range=(1, 2),
                        max_features=6000,
                        lowercase=True,
                    ),
                ),
                (
                    "clf",
                    LogisticRegression(max_iter=1000),
                ),
            ]
        )
        self.pipeline.fit(texts, labels)
        joblib.dump(self.pipeline, MODEL_PATH)

    def load(self, model_path: Path = MODEL_PATH) -> None:
        if not model_path.exists():
            raise FileNotFoundError("Trained model not found. Run train() first.")
        self.pipeline = joblib.load(model_path)

    def predict(self, text: str, confidence_threshold: float = 0.25) -> IntentPrediction:
        """Predict intent with keyword fallback for better paraphrase handling."""
        if not self.pipeline:
            raise RuntimeError("Classifier not trained or loaded.")
        
        # Try ML-based classification first
        probs = self.pipeline.predict_proba([text])[0]
        intents = self.pipeline.classes_
        max_idx = probs.argmax()
        ml_prediction = IntentPrediction(intent=intents[max_idx], confidence=float(probs[max_idx]))
        
        # If ML confidence is high enough, use it
        if ml_prediction.confidence >= confidence_threshold:
            return ml_prediction
        
        # Otherwise, try keyword matching as fallback
        if self.keyword_matcher:
            keyword_match = self.keyword_matcher.match(text, min_score=1.0)
            if keyword_match:
                keyword_intent, keyword_confidence = keyword_match
                # Boost confidence slightly to indicate keyword match
                boosted_confidence = min(keyword_confidence * 1.2, 0.95)
                return IntentPrediction(intent=keyword_intent, confidence=boosted_confidence)
        
        # Return ML prediction even if confidence is low
        return ml_prediction

    def top_k(self, text: str, k: int = 3) -> List[IntentPrediction]:
        """Get top K predictions combining ML and keyword matching."""
        if not self.pipeline:
            raise RuntimeError("Classifier not trained or loaded.")
        
        # Get ML predictions
        probs = self.pipeline.predict_proba([text])[0]
        intents = self.pipeline.classes_
        sorted_indices = probs.argsort()[::-1][:k]
        ml_predictions = [IntentPrediction(intent=intents[i], confidence=float(probs[i])) for i in sorted_indices]
        
        # Add keyword predictions if available
        if self.keyword_matcher:
            keyword_predictions = self.keyword_matcher.get_intents_for_keywords(text, top_k=k)
            keyword_preds = [IntentPrediction(intent=intent, confidence=conf) for intent, conf in keyword_predictions]
            
            # Merge and deduplicate
            all_predictions = {}
            for pred in ml_predictions + keyword_preds:
                if pred.intent not in all_predictions or pred.confidence > all_predictions[pred.intent].confidence:
                    all_predictions[pred.intent] = pred
            
            # Sort by confidence and return top k
            merged = sorted(all_predictions.values(), key=lambda x: x.confidence, reverse=True)
            return merged[:k]
        
        return ml_predictions
