"""High-level chatbot orchestration with conversation memory."""
from __future__ import annotations

import random
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

from . import config
from .context_manager import ConversationContext
from .data_loader import HotelInfo, TrainingRow, load_hotel_info, load_training_rows
from .dialogue_manager import DialogueManager
from .entity_extractor import EntityExtractor
from .input_validator import InputValidator
from .intent_classifier import IntentClassifier, IntentPrediction


@dataclass
class BotState:
    hotel_info: HotelInfo
    training_rows: list[TrainingRow]


class HotelChatbot:
    def __init__(
        self,
        training_data_path: Path | None = None,
        hotel_info_path: Path | None = None,
        room_types_path: Path | None = None,
        amenity_faq_path: Path | None = None,
        responses_path: Path | None = None,
        auto_train: bool = True,
        confidence_threshold: float = 0.25,
        max_training_rows: int | None = None,
        use_keyword_fallback: bool = True,
    ) -> None:
        self.training_data_path = training_data_path or config.TRAINING_DATA_PATH
        self.hotel_info_path = hotel_info_path or config.HOTEL_INFO_PATH
        self.room_types_path = room_types_path or config.ROOM_TYPES_PATH
        self.amenity_faq_path = amenity_faq_path or config.AMENITY_FAQ_PATH
        self.responses_path = responses_path or config.RESPONSE_TEMPLATES_PATH
        self.confidence_threshold = confidence_threshold
        self.max_training_rows = max_training_rows
        self.use_keyword_fallback = use_keyword_fallback

        self.state = BotState(
            hotel_info=self._load_hotel_info(),
            training_rows=self._load_training_rows(),
        )

        # Initialize conversation context with hotel information
        self.context = ConversationContext(
            hotel_name=self.state.hotel_info.metadata.get("name", "Sunset Bay Hotel"),
            hotel_address=self.state.hotel_info.metadata.get("address", ""),
            hotel_phone=self.state.hotel_info.metadata.get("phone", ""),
            hotel_email=self.state.hotel_info.metadata.get("email", ""),
        )

        self.input_validator = InputValidator()
        self.classifier = IntentClassifier(use_keyword_fallback=use_keyword_fallback)
        self.entity_extractor = EntityExtractor(self.state.hotel_info)
        self.dialogue_manager = DialogueManager(self.state.hotel_info, context=self.context)

        if auto_train:
            self.train()
        else:
            try:
                self.classifier.load()
            except FileNotFoundError:
                pass

    def _load_training_rows(self) -> list[TrainingRow]:
        rows = load_training_rows(self.training_data_path)
        if self.max_training_rows and len(rows) > self.max_training_rows:
            rows = random.sample(rows, self.max_training_rows)
        return rows

    def _load_hotel_info(self) -> HotelInfo:
        return load_hotel_info(
            self.hotel_info_path,
            self.room_types_path,
            self.amenity_faq_path,
            self.responses_path,
        )

    def train(self) -> None:
        if not self.state.training_rows:
            raise RuntimeError("No training data available")
        self.classifier.train(self.state.training_rows)

    def analyze(self, text: str, top_k: int = 3) -> Dict[str, object]:
        preds = self.classifier.top_k(text, k=top_k)
        entities = self.entity_extractor.extract(text)
        return {
            "predictions": [pred.__dict__ for pred in preds],
            "entities": entities,
        }

    def respond(self, text: str) -> Dict[str, object]:
        # Validate input first - check if it's a real question or gibberish
        is_valid, validation_message, validation_analysis = self.input_validator.validate(text)
        
        if not is_valid:
            return {
                "intent": "invalid_input",
                "confidence": 0.0,
                "entities": {},
                "response": validation_message,
                "context": self.context.get_context_summary(),
                "validation": validation_analysis,
            }
        
        # Predict intent with keyword fallback
        prediction: IntentPrediction = self.classifier.predict(text, confidence_threshold=self.confidence_threshold)
        
        # Use threshold to determine intent
        if prediction.confidence >= self.confidence_threshold:
            intent = prediction.intent
        else:
            intent = "unknown"
        
        # Extract entities
        entities = self.entity_extractor.extract(text)
        
        # Generate response using dialogue manager (which updates context)
        reply = self.dialogue_manager.respond(intent, entities)
        
        # Special handling for identity questions that fall through to "unknown"
        if intent == "unknown" and any(pattern in text.lower() for pattern in ["who are you", "what are you", "who r you"]):
            hotel_name = self.state.hotel_info.metadata.get("name", "our hotel")
            reply = f"I'm a hotel reservation assistant for {hotel_name}. I can help with room bookings, availability, pricing, amenities, and hotel policies. What would you like to know?"
        
        # Log conversation
        self.context.add_message("user", text)
        self.context.add_message("assistant", reply, intent)
        
        return {
            "intent": intent,
            "confidence": prediction.confidence,
            "entities": entities,
            "response": reply,
            "context": self.context.get_context_summary(),
        }
    
    def get_context(self) -> ConversationContext:
        """Get current conversation context."""
        return self.context
    
    def reset_context(self) -> None:
        """Reset conversation context, keeping hotel info."""
        self.context.clear_booking()
        self.context.message_history.clear()
        self.context.last_intent = None
