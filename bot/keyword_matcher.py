"""Keyword-based intent matching for paraphrase handling."""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple


class KeywordMatcher:
    """Enhanced keyword matcher with synonym support for better paraphrase handling."""
    
    def __init__(self):
        # Define keyword patterns for each intent with synonyms
        self.intent_keywords: Dict[str, List[List[str]]] = {
            "greet": [
                ["hello", "hi", "hey", "greetings", "good morning", "good afternoon", "good evening"],
            ],
            "goodbye": [
                ["bye", "goodbye", "see you", "later", "farewell", "exit", "quit"],
            ],
            "thanks": [
                ["thank", "thanks", "appreciate", "grateful", "thx"],
            ],
            "inquire_identity": [
                ["who", "you"],  # "who are you"
                ["what", "you"],  # "what are you"
            ],
            "inquire_availability": [
                ["available", "availability", "check", "vacant", "free", "open"],
                ["room", "rooms", "booking", "reservation"],
            ],
            "inquire_price": [
                ["price", "cost", "rate", "charge", "fee", "how much", "expensive", "cheap"],
            ],
            "inquire_room_type": [
                ["room type", "types of room", "what room", "which room", "room option", "category"],
            ],
            "inquire_amenities": [
                ["amenity", "amenities", "facility", "facilities", "service", "services", "feature", "features"],
                ["have", "offer", "provide", "include", "available"],
            ],
            "inquire_cancellation_policy": [
                ["cancel", "cancellation", "refund", "policy", "cancel policy", "refund policy"],
            ],
            "inquire_checkin_time": [
                ["check in", "check-in", "checkin", "arrival", "arrive", "come in"],
                ["time", "hour", "when", "what time"],
            ],
            "inquire_checkout_time": [
                ["check out", "check-out", "checkout", "departure", "depart", "leave"],
                ["time", "hour", "when", "what time"],
            ],
            "inquire_parking": [
                ["parking", "park", "car park", "garage", "vehicle"],
            ],
            "inquire_pet_policy": [
                ["pet", "pets", "dog", "cat", "animal"],
            ],
            "make_reservation": [
                ["book", "reserve", "reservation", "booking", "want to book", "make a reservation"],
            ],
            "change_dates": [
                ["change", "modify", "update", "adjust"],
                ["date", "dates", "day", "days"],
            ],
            "change_room_type": [
                ["change", "modify", "update", "switch", "upgrade"],
                ["room", "room type"],
            ],
            "change_guest_count": [
                ["change", "modify", "update", "adjust"],
                ["guest", "guests", "people", "person", "adult", "adults", "children"],
            ],
            "cancel_reservation": [
                ["cancel", "cancellation", "abort", "remove"],
                ["reservation", "booking"],
            ],
            "confirm": [
                ["yes", "confirm", "ok", "okay", "sure", "proceed", "go ahead", "correct", "right"],
            ],
            "deny": [
                ["no", "nope", "cancel", "don't", "never mind", "not now", "wrong"],
            ],
            "request_late_checkout": [
                ["late", "extend", "later"],
                ["checkout", "check out", "check-out"],
            ],
            "request_early_checkin": [
                ["early", "earlier", "before"],
                ["checkin", "check in", "check-in", "arrival"],
            ],
            "request_invoice": [
                ["invoice", "receipt", "bill", "statement", "payment confirmation"],
            ],
            "complaint_noise": [
                ["noise", "noisy", "loud", "sound"],
                ["complaint", "complain", "problem", "issue"],
            ],
            "complaint_cleanliness": [
                ["clean", "cleanliness", "dirty", "mess", "tidy"],
                ["complaint", "complain", "problem", "issue"],
            ],
            "complaint_billing": [
                ["billing", "charge", "payment", "invoice", "bill"],
                ["complaint", "complain", "problem", "issue", "wrong", "error"],
            ],
            "feedback_positive": [
                ["great", "excellent", "wonderful", "amazing", "love", "fantastic", "perfect", "good job"],
            ],
            "feedback_negative": [
                ["bad", "terrible", "awful", "horrible", "disappointed", "poor", "worst"],
            ],
        }
        
        # Weight for each match level
        self.weights = {
            "exact_phrase": 3.0,
            "all_keywords": 2.0,
            "partial_keywords": 1.0,
        }
    
    def match(self, text: str, min_score: float = 1.0) -> Optional[Tuple[str, float]]:
        """
        Match text against keyword patterns.
        Returns (intent, confidence_score) or None if no match above threshold.
        """
        text_lower = text.lower()
        best_intent = None
        best_score = 0.0
        
        for intent, keyword_groups in self.intent_keywords.items():
            score = self._calculate_score(text_lower, keyword_groups)
            if score > best_score:
                best_score = score
                best_intent = intent
        
        if best_score >= min_score and best_intent:
            # Normalize score to 0-1 range
            normalized_score = min(best_score / 5.0, 1.0)
            return (best_intent, normalized_score)
        
        return None
    
    def _calculate_score(self, text: str, keyword_groups: List[List[str]]) -> float:
        """Calculate matching score for a text against keyword groups."""
        if not keyword_groups:
            return 0.0
        
        # Check for exact phrase matches
        for group in keyword_groups:
            for phrase in group:
                if phrase in text:
                    return self.weights["exact_phrase"]
        
        # Check if all keyword groups have at least one match
        matches_per_group = []
        for group in keyword_groups:
            group_match = any(keyword in text for keyword in group)
            matches_per_group.append(group_match)
        
        if all(matches_per_group):
            return self.weights["all_keywords"]
        
        # Partial match
        if any(matches_per_group):
            match_ratio = sum(matches_per_group) / len(matches_per_group)
            return self.weights["partial_keywords"] * match_ratio
        
        return 0.0
    
    def get_intents_for_keywords(self, text: str, top_k: int = 3) -> List[Tuple[str, float]]:
        """Get top K intent matches based on keywords."""
        text_lower = text.lower()
        scores = []
        
        for intent, keyword_groups in self.intent_keywords.items():
            score = self._calculate_score(text_lower, keyword_groups)
            if score > 0:
                normalized_score = min(score / 5.0, 1.0)
                scores.append((intent, normalized_score))
        
        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]
