"""Input validation to detect questions vs random text."""
from __future__ import annotations

import re
from typing import Dict, Tuple


class InputValidator:
    """Validates user input to detect real questions vs gibberish/random text."""
    
    def __init__(self):
        # Question indicators
        self.question_words = {
            "what", "when", "where", "who", "why", "how", "which", "whose",
            "can", "could", "would", "should", "will", "do", "does", "did",
            "is", "are", "was", "were", "has", "have", "had", "am",
            "tell", "show", "give", "get", "need", "want", "looking",
            "explain", "describe", "say", "know",
        }
        
        # Hotel/booking related keywords (valid domain)
        self.domain_keywords = {
            # Booking/Reservation
            "book", "booking", "reserve", "reservation", "cancel", "cancellation",
            "confirm", "modify", "change", "update",
            
            # Room related
            "room", "suite", "deluxe", "standard", "family", "ocean", "type",
            "available", "availability", "vacant", "free",
            
            # Dates and time
            "date", "day", "night", "week", "month", "today", "tomorrow",
            "check-in", "checkin", "check-out", "checkout", "arrival", "departure",
            "stay", "staying", "arrive", "leave",
            
            # Pricing
            "price", "cost", "rate", "charge", "fee", "pay", "payment",
            "expensive", "cheap", "discount", "total",
            
            # Hotel facilities/amenities
            "amenity", "amenities", "facility", "facilities", "service", "services",
            "pool", "gym", "spa", "wifi", "parking", "breakfast", "restaurant",
            "pet", "pets", "dog", "cat",
            
            # People
            "guest", "guests", "adult", "adults", "child", "children", "kid", "kids",
            "people", "person",
            
            # Policies
            "policy", "policies", "rule", "rules", "regulation",
            
            # Hotel info
            "hotel", "address", "location", "phone", "email", "contact",
            
            # Common actions
            "need", "want", "like", "prefer", "looking", "search", "find",
            "help", "information", "info", "details", "tell", "know",
            
            # Greetings and politeness (acceptable)
            "hello", "hi", "hey", "greetings", "thanks", "thank", "please",
            "bye", "goodbye", "yes", "no", "ok", "okay",
            
            # Identity/info questions (acceptable)
            "you", "your", "who", "name", "about", "information",
        }
        
        # Common short greetings to allow
        self.allowed_short_words = {"hi", "ok", "no"}
        
        # Patterns that indicate gibberish
        self.gibberish_patterns = [
            r'^[a-z]{1,2}$',  # Single or two random letters
            r'^(.)\1{3,}',  # Repeated character (e.g., "aaaaa")
            r'^[^aeiou\s]{5,}',  # Too many consonants without vowels
            r'^\d+$',  # Only numbers
            r'^[!@#$%^&*()]+$',  # Only special characters
            r'^[a-z]+\d+[a-z]+\d+',  # Mixed random letters and numbers
        ]
    
    def validate(self, text: str) -> Tuple[bool, str, Dict[str, object]]:
        """
        Validate user input.
        
        Returns:
            (is_valid, message, analysis)
            - is_valid: True if input is valid question/statement
            - message: Error message if invalid, empty if valid
            - analysis: Dictionary with validation details
        """
        if not text or not text.strip():
            return False, "Please type something. How can I help you?", {"reason": "empty"}
        
        text_clean = text.strip().lower()
        
        # Check minimum length
        if len(text_clean) < 2:
            return False, "Please ask a complete question. I'm here to help with hotel reservations, room information, amenities, and policies.", {"reason": "too_short"}
        
        # Check for gibberish patterns (but allow common short words)
        if text_clean not in self.allowed_short_words:
            for pattern in self.gibberish_patterns:
                if re.match(pattern, text_clean):
                    # Allow if it's in domain keywords or question words
                    if text_clean not in self.domain_keywords and text_clean not in self.question_words:
                        return False, "That doesn't seem like a valid question. Please ask about hotel reservations, room availability, pricing, or our services.", {"reason": "gibberish_pattern"}
        
        # Check if it's just repeated words
        words = text_clean.split()
        if len(words) > 2 and len(set(words)) == 1:
            return False, "Please ask a meaningful question. I can help you with bookings, room types, amenities, check-in/out times, and hotel policies.", {"reason": "repeated_words"}
        
        # Check for single long gibberish-looking word (like aklsdfhasdihf)
        if len(words) == 1 and len(text_clean) > 7:
            # Check if it's clearly not a real word
            if not self._is_likely_real_word(text_clean):
                # Also check if it's not in our domain keywords or question words
                if text_clean not in self.domain_keywords and text_clean not in self.question_words:
                    return False, "That doesn't look like a valid word or question. Please ask about hotel reservations, room availability, pricing, or our services.", {"reason": "gibberish_word"}
        
        # Analyze content
        has_question_word = any(word in text_clean for word in self.question_words)
        has_question_mark = '?' in text
        has_domain_keyword = any(keyword in text_clean for keyword in self.domain_keywords)
        
        # Calculate word validity score
        word_tokens = re.findall(r'\b[a-z]+\b', text_clean)
        if word_tokens:
            # Check if words look like real words (have vowels, reasonable length)
            valid_words = sum(1 for word in word_tokens if self._is_likely_real_word(word))
            word_validity_ratio = valid_words / len(word_tokens)
        else:
            word_validity_ratio = 0.0
        
        analysis = {
            "has_question_word": has_question_word,
            "has_question_mark": has_question_mark,
            "has_domain_keyword": has_domain_keyword,
            "word_validity_ratio": word_validity_ratio,
            "word_count": len(words),
        }
        
        # Very short inputs without question indicators
        if len(words) == 1 and not has_domain_keyword and not has_question_word:
            if words[0] not in self.domain_keywords and words[0] not in self.question_words:
                return False, "I'm a hotel chatbot. Please ask a question about:\n• Room bookings and availability\n• Pricing and rates\n• Hotel amenities and services\n• Check-in/check-out policies\n• Contact information", {"reason": "single_invalid_word", "analysis": analysis}
        
        # Check word validity - if too many invalid-looking words
        if word_validity_ratio < 0.3 and len(word_tokens) > 2:
            return False, "I couldn't understand that. Please ask a clear question about hotel services, such as:\n• 'Do you have rooms available?'\n• 'What's the price for a deluxe room?'\n• 'When is check-in time?'", {"reason": "low_word_validity", "analysis": analysis}
        
        # Check for off-topic/random content
        # If it has question word but NO domain keywords, likely off-topic
        if (has_question_word or has_question_mark) and not has_domain_keyword and len(words) > 2:
            # Check for common off-topic question patterns
            off_topic_keywords = {
                "capital", "country", "president", "cook", "recipe", "weather",
                "math", "calculate", "physics", "chemistry", "science",
                "sports", "game", "movie", "song", "music", "actor",
                "politics", "news", "stock", "market", "crypto",
                "programming", "code", "python", "javascript",
            }
            if any(keyword in text_clean for keyword in off_topic_keywords):
                return False, "I'm a hotel reservation assistant and can only help with hotel-related questions like:\n✓ Room bookings and availability\n✓ Pricing and rates\n✓ Amenities and services\n✓ Check-in/check-out policies\n✓ Hotel information\n\nPlease ask something about your hotel stay.", {"reason": "off_topic_detected", "analysis": analysis}
        
        # More general off-topic check
        if not has_domain_keyword and not has_question_word and len(words) > 2:
            # Might be off-topic
            if word_validity_ratio < 0.6:
                return False, "That doesn't seem related to hotel services. I can help you with:\n✓ Room reservations\n✓ Availability and pricing\n✓ Amenities (WiFi, parking, pets, etc.)\n✓ Hotel policies\n\nWhat would you like to know?", {"reason": "off_topic", "analysis": analysis}
        
        # Valid input - has question indicators or domain keywords
        if has_question_word or has_question_mark or has_domain_keyword:
            return True, "", analysis
        
        # Check if it looks like a greeting, polite phrase, or identity question
        acceptable_patterns = [
            r'\b(hi|hello|hey|good\s+(morning|afternoon|evening|day))\b',
            r'\b(thank|thanks|thx|ty)\b',
            r'\b(bye|goodbye|see\s+you)\b',
            r'\b(yes|yea|yeah|yep|no|nope)\b',
            r'\b(ok|okay|sure|fine|alright)\b',
            r'\b(who|what)\s+(are|is)\s+you\b',  # "who are you", "what are you"
            r'\b(tell|say)\s+(me\s+)?(about\s+)?(you|yourself)\b',  # "tell me about you"
            r'\byour\s+(name|info|information)\b',  # "your name", "your information"
        ]
        
        for pattern in acceptable_patterns:
            if re.search(pattern, text_clean):
                return True, "", analysis
        
        # If we get here, treat it as potentially valid but questionable
        if word_validity_ratio >= 0.5:
            return True, "", analysis
        
        # Final fallback - looks invalid
        return False, "I'm not sure what you're asking. Please try asking about:\n• Room availability: 'Do you have rooms from Dec 10-12?'\n• Pricing: 'How much is a deluxe room?'\n• Amenities: 'Do you have parking?'\n• Policies: 'What's your cancellation policy?'", {"reason": "unclear_intent", "analysis": analysis}
    
    def _is_likely_real_word(self, word: str) -> bool:
        """Check if a word looks like a real English word."""
        if len(word) < 2:
            return True  # Single letters are okay
        
        # Must have at least one vowel (or y)
        if not re.search(r'[aeiouy]', word):
            return False
        
        # Check for reasonable consonant clusters
        # Too many consonants in a row is suspicious
        consonant_clusters = re.findall(r'[^aeiouy\s]{4,}', word)
        if consonant_clusters:
            return False
        
        # Check for repeated patterns that look wrong
        if len(word) > 3:
            # Same 2-char pattern repeated
            for i in range(len(word) - 3):
                if word[i:i+2] == word[i+2:i+4]:
                    return False
        
        return True
